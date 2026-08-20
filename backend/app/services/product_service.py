"""
Ürün Yönetimi ve SDS CRUD Servis Katmanı
"""

import copy
import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import or_, desc, asc
from app.models.db_models import Product, Category
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductDuplicateRequest,
    ProductListItem,
    ProductListResponse,
    ProductResponse,
    CategoryItem,
    CategoryCreateRequest,
    CategoryDeleteRequest,
)
from app.schemas.sds_sections import SDSModel
from app.schemas.validation import ValidationResult
from app.schemas.reference import AutoFillHResponse
from app.services.validator_service import validator_service
from app.services.reference_service import reference_service


def _deep_merge_dict(target: dict, source: dict) -> dict:
    """İki sözlüğü özyinelemeli olarak birleştirir ve yeni bir kopya döndürür."""
    result = copy.deepcopy(target)
    for key, value in source.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = _deep_merge_dict(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


class ProductService:
    def create_product(self, db: Session, product_in: ProductCreate) -> Product:
        sds_obj = product_in.sds_data or SDSModel()
        sds_dict = sds_obj.model_dump()

        # Otomatik varsayılanlar: B1.1'deki adı ürün adıyla eşle
        if not sds_dict.get("b1_kimlik", {}).get("b1_1", {}).get("madde_karisim_adi"):
            if "b1_kimlik" not in sds_dict:
                sds_dict["b1_kimlik"] = {}
            if "b1_1" not in sds_dict["b1_kimlik"]:
                sds_dict["b1_kimlik"]["b1_1"] = {}
            sds_dict["b1_kimlik"]["b1_1"]["madde_karisim_adi"] = product_in.urun_adi

        # Meta hazırlama tarihi yoksa bugünü koy
        if not sds_dict.get("meta", {}).get("hazirlama_tarihi"):
            if "meta" not in sds_dict:
                sds_dict["meta"] = {}
            sds_dict["meta"]["hazirlama_tarihi"] = datetime.date.today().strftime("%d.%m.%Y")

        now = datetime.datetime.now(datetime.timezone.utc)
        db_product = Product(
            urun_adi=product_in.urun_adi.strip(),
            ticari_kod=product_in.ticari_kod.strip(),
            kategori=product_in.kategori.strip() if product_in.kategori else None,
            sds_data=sds_dict,
            olusturma_tarihi=now,
            son_guncelleme=now
        )
        db.add(db_product)
        db.commit()
        if product_in.kategori and product_in.kategori.strip():
            self.create_category(db, product_in.kategori.strip())
        db.refresh(db_product)
        return db_product

    def get_product(self, db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    def list_products(
        self,
        db: Session,
        query_str: Optional[str] = None,
        kategori: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "son_guncelleme",
        sort_order: str = "desc"
    ) -> ProductListResponse:
        db_query = db.query(Product)

        # Filtreleme
        if query_str:
            term = f"%{query_str.strip()}%"
            db_query = db_query.filter(
                or_(
                    Product.urun_adi.ilike(term),
                    Product.ticari_kod.ilike(term),
                    Product.kategori.ilike(term)
                )
            )

        if kategori:
            db_query = db_query.filter(Product.kategori == kategori.strip())

        # Sıralama
        sort_column = getattr(Product, sort_by, Product.son_guncelleme)
        if sort_order.lower() == "asc":
            db_query = db_query.order_by(asc(sort_column))
        else:
            db_query = db_query.order_by(desc(sort_column))

        total = db_query.count()
        offset = (page - 1) * page_size
        products = db_query.offset(offset).limit(page_size).all()

        items: List[ProductListItem] = []
        for p in products:
            val_res = validator_service.validate_sds(p.sds_data or {})
            if val_res.total_errors > 0:
                status = "Eksik / Hatalı"
            elif val_res.total_warnings > 0:
                status = "Uyarılı"
            else:
                status = "Eksiksiz"

            items.append(ProductListItem(
                id=p.id,
                urun_adi=p.urun_adi,
                ticari_kod=p.ticari_kod,
                kategori=p.kategori,
                olusturma_tarihi=p.olusturma_tarihi,
                son_guncelleme=p.son_guncelleme,
                tamamlanma_yuzdesi=val_res.overall_completion_percentage,
                dogrulama_durumu=status
            ))

        return ProductListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=items
        )

    def _seed_categories_if_needed(self, db: Session):
        """Varsayılan ürün ailelerini ve ürünlerdeki mevcut kategorileri Category tablosuna ekler."""
        defaults = [
            "Solventler & Tinerler",
            "Poliüretan Sistemler & Sertleştiriciler",
            "Endüstriyel Boyalar & Astarlar",
            "Su Bazlı Sistemler & Emülsiyonlar",
            "Reçineler & Polimerler",
            "Epoksi Sistemler",
        ]
        existing = {c.name.lower(): c for c in db.query(Category).all()}
        product_cats = [
            r[0].strip() for r in db.query(Product.kategori)
            .filter(Product.kategori.isnot(None), Product.kategori != "")
            .distinct().all() if r[0] and r[0].strip()
        ]
        all_initial = list(dict.fromkeys(defaults + product_cats))
        added = False
        for cat_name in all_initial:
            if cat_name.lower() not in existing:
                db.add(Category(name=cat_name))
                existing[cat_name.lower()] = True
                added = True
        if added:
            db.commit()

    def get_categories(self, db: Session) -> List[CategoryItem]:
        """Kayıtlı tüm ürün ailelerini ve her birindeki ürün adedini döner."""
        self._seed_categories_if_needed(db)
        categories = db.query(Category).order_by(asc(Category.name)).all()

        results: List[CategoryItem] = []
        for cat in categories:
            count = db.query(Product).filter(Product.kategori == cat.name).count()
            results.append(CategoryItem(
                name=cat.name,
                product_count=count
            ))
        return results

    def create_category(self, db: Session, name: str) -> Category:
        """Yeni bir ürün ailesi oluşturur."""
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Kategori adı boş olamaz.")

        existing = db.query(Category).filter(Category.name.ilike(clean_name)).first()
        if existing:
            return existing

        new_cat = Category(name=clean_name)
        db.add(new_cat)
        db.commit()
        db.refresh(new_cat)
        return new_cat

    def delete_category(self, db: Session, name: str, target_category: Optional[str] = None) -> Dict[str, Any]:
        """
        Belirtilen ürün ailesini siler.
        Bu aileye bağlı ürünleri hedef kategoriye (veya Genel'e) aktarır.
        """
        clean_name = name.strip()
        target = target_category.strip() if target_category else "Genel"

        # Hedef kategori yoksa ve silinecek kategoriyle aynı değilse oluştur
        if target and target.lower() != clean_name.lower():
            target_exists = db.query(Category).filter(Category.name.ilike(target)).first()
            if not target_exists:
                db.add(Category(name=target))
                db.commit()

        # Bu kategoriye bağlı ürünleri güncelle
        affected_products = db.query(Product).filter(Product.kategori.ilike(clean_name)).all()
        count = len(affected_products)
        for p in affected_products:
            p.kategori = target

        # Category tablosundan sil
        cat_rec = db.query(Category).filter(Category.name.ilike(clean_name)).first()
        if cat_rec:
            db.delete(cat_rec)

        db.commit()
        return {
            "deleted": clean_name,
            "affected_products": count,
            "reassigned_to": target
        }

    def update_product(self, db: Session, product_id: int, product_in: Any) -> Optional[Product]:
        product = self.get_product(db, product_id)
        if not product:
            return None

        if isinstance(product_in, dict):
            urun_adi = product_in.get("urun_adi")
            ticari_kod = product_in.get("ticari_kod")
            kategori = product_in.get("kategori")
            sds_data = product_in.get("sds_data")
        else:
            urun_adi = product_in.urun_adi
            ticari_kod = product_in.ticari_kod
            kategori = product_in.kategori
            sds_data = product_in.sds_data

        if urun_adi is not None:
            product.urun_adi = urun_adi.strip()
        if ticari_kod is not None:
            product.ticari_kod = ticari_kod.strip()
        if kategori is not None:
            product.kategori = kategori.strip()

        if sds_data is not None:
            current_sds = dict(product.sds_data or {})
            updated_sds = _deep_merge_dict(current_sds, sds_data)
            product.sds_data = updated_sds
            flag_modified(product, "sds_data")

        product.son_guncelleme = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
        db.refresh(product)
        return product

    def delete_product(self, db: Session, product_id: int) -> bool:
        product = self.get_product(db, product_id)
        if not product:
            return False
        db.delete(product)
        db.commit()
        return True

    def duplicate_product(
        self,
        db: Session,
        product_id: int,
        req: Optional[ProductDuplicateRequest] = None
    ) -> Optional[Product]:
        original = self.get_product(db, product_id)
        if not original:
            return None

        new_name = (req.yeni_urun_adi.strip() if req and req.yeni_urun_adi else f"{original.urun_adi} - Kopya")
        new_code = (req.yeni_ticari_kod.strip() if req and req.yeni_ticari_kod else f"{original.ticari_kod}-COPY")

        new_sds = copy.deepcopy(original.sds_data or {})
        # B1.1'deki ürün adını güncelle
        if "b1_kimlik" in new_sds and "b1_1" in new_sds["b1_kimlik"]:
            new_sds["b1_kimlik"]["b1_1"]["madde_karisim_adi"] = new_name

        now = datetime.datetime.now(datetime.timezone.utc)
        duplicated = Product(
            urun_adi=new_name,
            ticari_kod=new_code,
            kategori=original.kategori,
            sds_data=new_sds,
            olusturma_tarihi=now,
            son_guncelleme=now
        )
        db.add(duplicated)
        db.commit()
        db.refresh(duplicated)
        return duplicated

    def validate_product_sds(self, db: Session, product_id: int) -> Optional[ValidationResult]:
        product = self.get_product(db, product_id)
        if not product:
            return None
        return validator_service.validate_sds(product.sds_data or {})

    def auto_fill_product_h_statements(
        self,
        db: Session,
        product_id: int,
        save_to_sds: bool = False
    ) -> Optional[AutoFillHResponse]:
        product = self.get_product(db, product_id)
        if not product:
            return None

        sds_dict = product.sds_data or {}
        found_codes = reference_service.extract_h_codes_from_sds(sds_dict)
        h_items = [reference_service.get_h_statement(c) for c in found_codes if reference_service.get_h_statement(c)]
        formatted_list = reference_service.format_h_statements(found_codes)

        updated = False
        if save_to_sds and formatted_list:
            current_sds = copy.deepcopy(sds_dict)
            if "b16_diger_bilgiler" not in current_sds:
                current_sds["b16_diger_bilgiler"] = {}
            current_sds["b16_diger_bilgiler"]["tam_h_ifadeleri"] = formatted_list
            product.sds_data = current_sds
            flag_modified(product, "sds_data")
            product.son_guncelleme = datetime.datetime.now(datetime.timezone.utc)
            db.commit()
            db.refresh(product)
            updated = True

        return AutoFillHResponse(
            product_id=product_id,
            found_h_codes=found_codes,
            h_statements=h_items,
            formatted_texts=formatted_list,
            updated_section16=updated
        )


product_service = ProductService()
