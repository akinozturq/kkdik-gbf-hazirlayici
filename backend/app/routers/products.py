"""
Ürün Yönetimi, SDS ve Export API Router'ı
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import copy
import urllib.parse
import traceback
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductDuplicateRequest,
    ProductResponse,
    ProductListResponse,
    CategoryItem,
    CategoryCreateRequest,
    CategoryDeleteRequest,
)
from app.schemas.sds_sections import SDSModel
from app.schemas.validation import ValidationResult
from app.schemas.reference import AutoFillHResponse
from app.services.product_service import product_service
from app.services.validator_service import validator_service
from app.services.reference_service import reference_service
from app.services.docx_export_service import DocxExportService
from app.services.pdf_export_service import PdfExportService

router = APIRouter(prefix="/api/products", tags=["Ürünler & SDS"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kimyasal ürün ve SDS taslağı oluşturma"
)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    """
    Yeni bir kimyasal ürün ve 16 bölümlük boş/doldurulmuş SDS taslağı oluşturur.
    """
    return product_service.create_product(db, product_in)


@router.get(
    "",
    response_model=ProductListResponse,
    summary="Ürün listesi, arama ve filtreleme"
)
def list_products(
    query: Optional[str] = Query(None, description="Ürün adı, ticari kod veya kategori arama terimi"),
    kategori: Optional[str] = Query(None, description="Kategoriye göre filtreleme"),
    page: int = Query(1, ge=1, description="Sayfa numarası"),
    page_size: int = Query(20, ge=1, le=100, description="Sayfa başına kayıt sayısı"),
    sort_by: str = Query("son_guncelleme", description="Sıralama alanı (son_guncelleme, urun_adi, ticari_kod)"),
    sort_order: str = Query("desc", description="Sıralama yönü (asc, desc)"),
    db: Session = Depends(get_db)
):
    """
    Ürünleri arama, kategori filtreleme ve tamamlama durumu ile birlikte listeler.
    """
    return product_service.list_products(
        db,
        query_str=query,
        kategori=kategori,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get(
    "/categories",
    response_model=List[CategoryItem],
    summary="Tüm benzersiz ürün aileleri / kategorileri listesi ve ürün sayıları"
)
def get_categories(db: Session = Depends(get_db)):
    """
    Kayıtlı tüm ürün ailelerini, hazır önerileri ve her kategorideki ürün sayısını döner.
    """
    return product_service.get_categories(db)


@router.post(
    "/categories",
    response_model=CategoryItem,
    summary="Yeni ürün ailesi / kategori oluştur"
)
def create_category(req: CategoryCreateRequest, db: Session = Depends(get_db)):
    """
    Yeni bir ürün ailesi tanımlar.
    """
    cat = product_service.create_category(db, req.name)
    count = db.query(Product).filter(Product.kategori == cat.name).count()
    return CategoryItem(name=cat.name, product_count=count)


@router.delete(
    "/categories/{name}",
    summary="Ürün ailesini sil ve ürünleri aktar"
)
def delete_category(
    name: str,
    target_category: Optional[str] = Query(None, description="Silinen kategorideki ürünlerin aktarılacağı hedef kategori"),
    db: Session = Depends(get_db)
):
    """
    Belirtilen ürün ailesini siler ve bu aileye ait ürünleri hedef kategoriye (veya Genel'e) aktarır.
    """
    decoded_name = urllib.parse.unquote(name)
    return product_service.delete_category(db, decoded_name, target_category)



@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Ürün detayı ve 16 bölümlük SDS verisi"
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Belirtilen ID'ye sahip ürünün tüm 16 bölümlük SDS verisini getirir.
    """
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )
    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Ürün ve SDS form verilerini güncelleme (Autosave uyumlu)"
)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Ürün meta bilgilerini veya 16 bölümlük SDS verilerini kısmi/tam günceller.
    Frontend debounced autosave mekanizmasıyla tam uyumludur.
    """
    updated = product_service.update_product(db, product_id, product_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )
    return updated


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Ürün silme"
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Ürünü ve ilişkili tüm SDS verisini veritabanından kalıcı olarak siler.
    """
    deleted = product_service.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )
    return None


@router.post(
    "/{product_id}/duplicate",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Var olan bir üründen kopyala -> yeni ürün oluştur"
)
def duplicate_product(
    product_id: int,
    duplicate_req: Optional[ProductDuplicateRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Benzer formülasyonlar için hızlı başlangıç sağlamak amacıyla var olan ürünü ve 16 bölümlük SDS'ini kopyalar.
    """
    duplicated = product_service.duplicate_product(db, product_id, duplicate_req)
    if not duplicated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )
    return duplicated


@router.get(
    "/{product_id}/validate",
    response_model=ValidationResult,
    summary="Ürünün SDS verisini KKDİK Ek-2 kurallarına göre doğrula"
)
def validate_product_sds(product_id: int, db: Session = Depends(get_db)):
    """
    Ürünün SDS verilerini Bölüm 4'teki doğrulama kurallarına (md. 0.4, md. 0.3.1, md. 0.2.4, md. 0.2.5, md. 2.1)
    göre test eder; hata, uyarı ve 16 bölüm ilerleme yüzdesini döndürür.
    """
    result = product_service.validate_product_sds(db, product_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )
    return result


@router.post(
    "/{product_id}/auto-fill-h-codes",
    response_model=AutoFillHResponse,
    summary="Bölüm 2 ve 3'teki H-kodlarını topla ve Bölüm 16'ya tam metin olarak derle"
)
def auto_fill_h_codes(
    product_id: int,
    save_to_sds: bool = Query(False, description="Oluşturulan tam metinleri doğrudan ürünün Bölüm 16'sına kaydet"),
    db: Session = Depends(get_db)
):
    """
    KKDİK Ek-2 Madde 2.1 ve 16.d gereği, formda geçen tüm H-kodlarını otomatik olarak bulur ve
    Bölüm 16 için Türkçe açıklamalarıyla birlikte liste haline getirir.
    """
    result = product_service.auto_fill_product_h_statements(db, product_id, save_to_sds=save_to_sds)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )
    return result


@router.post(
    "/validate-raw",
    response_model=ValidationResult,
    summary="Kaydetmeden doğrudan ham SDS JSON'ını doğrula"
)
def validate_raw_sds(sds_in: SDSModel):
    """
    Veritabanına kaydetmeksizin gönderilen herhangi bir SDS modelini anında doğrular.
    """
    return validator_service.validate_sds(sds_in)


# =========================================================================
# FAZ 3: EXPORT MOTORU ENDPOINT'LERİ (WORD DOCX, PDF, HTML PREVIEW)
# =========================================================================

@router.get(
    "/{product_id}/export/docx",
    summary="16 Bölümlük Kurumsal Antetli Word (.docx) GBF İndir"
)
def export_docx(
    product_id: int,
    lang: Optional[str] = Query("tr", description="Dil seçeneği: 'tr' (KKDİK) veya 'en' (REACH Annex II)"),
    db: Session = Depends(get_db)
):
    """
    GBF ANTET.docx şablonunu ve kurumsal tasarımı kullanarak 16 bölümlük resmi Word belgesi üretir.
    """
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )

    product_dict = {
        "id": product.id,
        "urun_adi": product.urun_adi,
        "ticari_kod": product.ticari_kod,
        "kategori": product.kategori,
        "sds_data": product.sds_data
    }

    try:
        lang_clean = (lang or "tr").lower()
        docx_stream = DocxExportService.generate_docx(product_dict, lang=lang_clean)
        suffix = "Safety_Data_Sheet" if lang_clean == "en" else "Guvenlik_Bilgi_Formu"
        filename = f"{product.ticari_kod or 'GBF'}_{suffix}.docx"
        encoded_filename = urllib.parse.quote(filename)

        return Response(
            content=docx_stream.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        err_msg = f"DOCX Üretim Hatası: {str(e)}\n{traceback.format_exc()}"
        print(err_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_msg
        )


@router.get(
    "/{product_id}/export/pdf",
    summary="16 Bölümlük Kurumsal Antetli PDF GBF İndir"
)
def export_pdf(
    product_id: int,
    lang: Optional[str] = Query("tr", description="Dil seçeneği: 'tr' (KKDİK) veya 'en' (REACH Annex II)"),
    db: Session = Depends(get_db)
):
    """
    Kurumsal antet tasarımı ve 16 bölüm mevzuat tabloları içeren resmi PDF belgesi üretir.
    """
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )

    product_dict = {
        "id": product.id,
        "urun_adi": product.urun_adi,
        "ticari_kod": product.ticari_kod,
        "kategori": product.kategori,
        "sds_data": product.sds_data
    }

    try:
        lang_clean = (lang or "tr").lower()
        pdf_stream = PdfExportService.generate_pdf(product_dict, lang=lang_clean)
        suffix = "Safety_Data_Sheet" if lang_clean == "en" else "Guvenlik_Bilgi_Formu"
        filename = f"{product.ticari_kod or 'GBF'}_{suffix}.pdf"
        encoded_filename = urllib.parse.quote(filename)

        return Response(
            content=pdf_stream.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        err_msg = f"PDF Üretim Hatası: {str(e)}\n{traceback.format_exc()}"
        print(err_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_msg
        )


@router.get(
    "/{product_id}/export/preview-html",
    response_class=HTMLResponse,
    summary="16 Bölümlük GBF HTML Canlı Önizleme"
)
def preview_html(
    product_id: int,
    lang: Optional[str] = Query("tr", description="Dil seçeneği: 'tr' (KKDİK) veya 'en' (REACH Annex II)"),
    db: Session = Depends(get_db)
):
    """
    Belgenin tarayıcıda doğrudan önizlenebilmesi için derlenmiş HTML çıktısını döner.
    """
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )

    product_dict = {
        "id": product.id,
        "urun_adi": product.urun_adi,
        "ticari_kod": product.ticari_kod,
        "kategori": product.kategori,
        "sds_data": product.sds_data
    }

    try:
        lang_clean = (lang or "tr").lower()
        return PdfExportService.render_html(product_dict, lang=lang_clean)
    except Exception as e:
        err_msg = f"HTML Önizleme Hatası: {str(e)}\n{traceback.format_exc()}"
        print(err_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=err_msg
        )


# ==========================================
# SEA KARIŞIM HESAPLAMA & H -> P HARİTALAMA ENDPOINT'LERİ
# ==========================================

from app.services.classification_engine import ClassificationEngine

class HToPRequest(BaseModel):
    h_codes: List[str]

class CalculatePreviewRequest(BaseModel):
    bilesenler: List[dict]
    parlama_noktasi: Optional[float] = None
    kaynama_noktasi: Optional[float] = None
    kinematik_viskozite: Optional[float] = None


@router.post(
    "/{product_id}/calculate-hazards",
    summary="Bölüm 3.2 Karışım Tablosundan Bölüm 2 Zararlılıklarını Hesapla"
)
def calculate_product_hazards(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )

    sds = product.sds_data or {}
    bilesenler = sds.get("b3_bilesim", {}).get("karisim", {}).get("bilesenler", [])

    b9 = sds.get("b9_fiziksel_kimyasal_ozellikler", {}).get("b9_1", {}) or sds.get("b9_fiziksel_kimyasal", {}).get("b9_1", {})
    fp_str = b9.get("parlama_noktasi")
    bp_str = b9.get("kaynama_noktasi_araligi") or b9.get("kaynama_noktasi")
    visk_str = b9.get("kinematik_viskozite") or b9.get("akiskanlik")

    fp_val = ClassificationEngine.parse_float_safe(fp_str)
    bp_val = ClassificationEngine.parse_float_safe(bp_str)
    visk_val = ClassificationEngine.parse_float_safe(visk_str)

    result = ClassificationEngine.calculate_mixture_hazards(
        bilesenler=bilesenler,
        parlama_noktasi=fp_val,
        kaynama_noktasi=bp_val,
        kinematik_viskozite=visk_val
    )
    return result


@router.post(
    "/{product_id}/apply-calculated-hazards",
    summary="Hesaplanan Zararlılıkları Ürünün Bölüm 2'sine Aktar ve Kaydet"
)
def apply_calculated_hazards(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )

    sds = copy.deepcopy(product.sds_data or {})
    bilesenler = sds.get("b3_bilesim", {}).get("karisim", {}).get("bilesenler", [])

    b9 = sds.get("b9_fiziksel_kimyasal_ozellikler", {}).get("b9_1", {}) or sds.get("b9_fiziksel_kimyasal", {}).get("b9_1", {})
    fp_str = b9.get("parlama_noktasi")
    bp_str = b9.get("kaynama_noktasi_araligi") or b9.get("kaynama_noktasi")
    visk_str = b9.get("kinematik_viskozite") or b9.get("akiskanlik")

    fp_val = ClassificationEngine.parse_float_safe(fp_str)
    bp_val = ClassificationEngine.parse_float_safe(bp_str)
    visk_val = ClassificationEngine.parse_float_safe(visk_str)

    result = ClassificationEngine.calculate_mixture_hazards(
        bilesenler=bilesenler,
        parlama_noktasi=fp_val,
        kaynama_noktasi=bp_val,
        kinematik_viskozite=visk_val
    )

    if not sds.get("b2_zarar_tanimi"):
        sds["b2_zarar_tanimi"] = {}
    if not sds["b2_zarar_tanimi"].get("b2_1"):
        sds["b2_zarar_tanimi"]["b2_1"] = {}
    if not sds["b2_zarar_tanimi"].get("b2_2"):
        sds["b2_zarar_tanimi"]["b2_2"] = {}

    sds["b2_zarar_tanimi"]["b2_1"]["siniflandirmalar"] = result["siniflandirmalar"]
    sds["b2_zarar_tanimi"]["b2_1"]["siniflandirilmamis"] = len(result["siniflandirmalar"]) == 0
    sds["b2_zarar_tanimi"]["b2_2"]["piktogramlar"] = result["piktogramlar"]
    sds["b2_zarar_tanimi"]["b2_2"]["uyari_kelimesi"] = result["uyari_kelimesi"]
    sds["b2_zarar_tanimi"]["b2_2"]["h_ifadeleri"] = result["h_ifadeleri"]
    sds["b2_zarar_tanimi"]["b2_2"]["p_ifadeleri"] = result["p_ifadeleri"]

    updated = product_service.update_product(db, product_id, {"sds_data": sds})
    val_res = validator_service.validate_sds(updated.sds_data or {})

    product_dict = {
        "id": updated.id,
        "urun_adi": updated.urun_adi,
        "ticari_kod": updated.ticari_kod,
        "kategori": updated.kategori,
        "sds_data": updated.sds_data,
        "olusturma_tarihi": updated.olusturma_tarihi.isoformat() if updated.olusturma_tarihi else None,
        "son_guncelleme": updated.son_guncelleme.isoformat() if updated.son_guncelleme else None,
        "tamamlanma_yuzdesi": val_res.overall_completion_percentage
    }

    return {"status": "success", "product": product_dict, "calculation_result": result}


@router.post(
    "/hazards/h-to-p",
    summary="H-Kodlarından Standart P-Kodlarını Türet"
)
def derive_p_from_h(req: HToPRequest):
    p_codes = ClassificationEngine.generate_p_statements(req.h_codes)
    return {"p_codes": p_codes}


@router.post(
    "/hazards/calculate-preview",
    summary="Bileşen Listesinden Zararlılık Önizlemesi Hesapla"
)
def calculate_preview(req: CalculatePreviewRequest):
    return ClassificationEngine.calculate_mixture_hazards(
        bilesenler=req.bilesenler,
        parlama_noktasi=req.parlama_noktasi,
        kaynama_noktasi=req.kaynama_noktasi,
        kinematik_viskozite=req.kinematik_viskozite
    )


@router.post(
    "/{product_id}/auto-fill-exposure-limits",
    summary="Bölüm 3 Bileşenlerinden Bölüm 8.1 Maruziyet Limitlerini Otomatik Doldur"
)
def auto_fill_exposure_limits(
    product_id: int,
    save_to_sds: bool = Query(False, description="Bulunan limitleri doğrudan Bölüm 8.1'e kaydet"),
    db: Session = Depends(get_db)
):
    """
    Bölüm 3'teki bileşenleri tarar ve Kimyasal Maddelerle Çalışmalarda Sağlık ve Güvenlik Önlemleri
    Yönetmeliği Ek-1 Mesleki Maruziyet Sınır Değerleri tablosuyla eşleştirip Bölüm 8.1'i otomatik doldurur.
    """
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )

    sds = copy.deepcopy(product.sds_data or {})
    matched_limits = reference_service.auto_match_exposure_limits_from_sds(sds)

    if save_to_sds:
        if "b8_maruz_kalma_kontrolu" not in sds:
            sds["b8_maruz_kalma_kontrolu"] = {}
        sds["b8_maruz_kalma_kontrolu"]["b8_1_kontrol_parametreleri"] = matched_limits
        updated = product_service.update_product(db, product_id, {"sds_data": sds})
        val_res = validator_service.validate_sds(updated.sds_data or {})
        return {
            "product_id": product_id,
            "matched_limits": matched_limits,
            "saved": True,
            "product": {
                "id": updated.id,
                "sds_data": updated.sds_data,
                "tamamlanma_yuzdesi": val_res.overall_completion_percentage
            }
        }

    return {
        "product_id": product_id,
        "matched_limits": matched_limits,
        "saved": False
    }


class CalculateTransportPreviewRequest(BaseModel):
    sds_data: Dict[str, Any]
    urun_adi: Optional[str] = ""


@router.post(
    "/hazards/calculate-transport-preview",
    summary="Canlı Form Verilerinden Otomatik ADR / UN Taşımacılık Sınıflandırması Hesapla"
)
def calculate_transport_preview(req: CalculateTransportPreviewRequest):
    """
    Bölüm 9 fiziksel özellikleri ve Bölüm 2 zararlılık sınıflarını analiz ederek
    Bölüm 14 için ADR / RID / IMDG / IATA taşımacılık sınıflandırması önerir.
    """
    from app.services.transport_engine import transport_engine
    return transport_engine.evaluate_transport(req.sds_data, urun_adi=req.urun_adi or "")


@router.post(
    "/{product_id}/calculate-transport",
    summary="Ürünün Kayıtlı SDS'inden ADR / UN Taşımacılık Sınıflandırmasını Hesapla"
)
def calculate_product_transport(
    product_id: int,
    save_to_sds: bool = Query(False, description="Hesaplanan bilgileri doğrudan Bölüm 14'e kaydet"),
    db: Session = Depends(get_db)
):
    """
    Kayıtlı ürünün verilerini tarar, ADR karar ağacını çalıştırır ve Bölüm 14 alanlarını döner/kaydeder.
    """
    from app.services.transport_engine import transport_engine

    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} numaralı ürün bulunamadı."
        )

    sds = copy.deepcopy(product.sds_data or {})
    result = transport_engine.evaluate_transport(sds, urun_adi=product.urun_adi or "")

    if save_to_sds:
        if "b14_tasimacilik" not in sds:
            sds["b14_tasimacilik"] = {}
        b14 = sds["b14_tasimacilik"]
        b14["b14_1_un_numarasi"] = result.get("b14_1_un_numarasi")
        b14["b14_2_un_tasimacilik_adi"] = result.get("b14_2_un_tasimacilik_adi")
        b14["b14_3_tasimacilik_sinifi"] = result.get("b14_3_tasimacilik_sinifi")
        b14["b14_4_ambalajlama_grubu"] = result.get("b14_4_ambalajlama_grubu")
        b14["b14_5_cevresel_zararlar"] = result.get("b14_5_cevresel_zararlar")
        b14["b14_6_kullanici_ozel_onlemler"] = result.get("b14_6_kullanici_ozel_onlemler")

        updated = product_service.update_product(db, product_id, {"sds_data": sds})
        val_res = validator_service.validate_sds(updated.sds_data or {})
        return {
            "product_id": product_id,
            "transport_data": result,
            "saved": True,
            "product": {
                "id": updated.id,
                "sds_data": updated.sds_data,
                "tamamlanma_yuzdesi": val_res.overall_completion_percentage
            }
        }

    return {
        "product_id": product_id,
        "transport_data": result,
        "saved": False
    }



