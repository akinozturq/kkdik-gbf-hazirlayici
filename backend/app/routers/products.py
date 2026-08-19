"""
Ürün Yönetimi, SDS ve Export API Router'ı
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import urllib.parse
import traceback
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductDuplicateRequest,
    ProductResponse,
    ProductListResponse,
)
from app.schemas.sds_sections import SDSModel
from app.schemas.validation import ValidationResult
from app.schemas.reference import AutoFillHResponse
from app.services.product_service import product_service
from app.services.validator_service import validator_service
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
def export_docx(product_id: int, db: Session = Depends(get_db)):
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
        docx_stream = DocxExportService.generate_docx(product_dict)
        filename = f"{product.ticari_kod or 'GBF'}_Guvenlik_Bilgi_Formu.docx"
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
def export_pdf(product_id: int, db: Session = Depends(get_db)):
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
        pdf_stream = PdfExportService.generate_pdf(product_dict)
        filename = f"{product.ticari_kod or 'GBF'}_Guvenlik_Bilgi_Formu.pdf"
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
def preview_html(product_id: int, db: Session = Depends(get_db)):
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
        return PdfExportService.render_html(product_dict)
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

    b9 = sds.get("b9_fiziksel_kimyasal_ozellikler", {}).get("b9_1", {})
    fp_str = b9.get("parlama_noktasi")
    bp_str = b9.get("kaynama_noktasi_araligi")

    fp_val = ClassificationEngine.parse_concentration(fp_str) if fp_str else None
    bp_val = ClassificationEngine.parse_concentration(bp_str) if bp_str else None

    result = ClassificationEngine.calculate_mixture_hazards(
        bilesenler=bilesenler,
        parlama_noktasi=fp_val,
        kaynama_noktasi=bp_val
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

    sds = product.sds_data or {}
    bilesenler = sds.get("b3_bilesim", {}).get("karisim", {}).get("bilesenler", [])

    b9 = sds.get("b9_fiziksel_kimyasal_ozellikler", {}).get("b9_1", {})
    fp_str = b9.get("parlama_noktasi")
    bp_str = b9.get("kaynama_noktasi_araligi")
    fp_val = ClassificationEngine.parse_concentration(fp_str) if fp_str else None
    bp_val = ClassificationEngine.parse_concentration(bp_str) if bp_str else None

    result = ClassificationEngine.calculate_mixture_hazards(
        bilesenler=bilesenler,
        parlama_noktasi=fp_val,
        kaynama_noktasi=bp_val
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
    return {"status": "success", "product": updated, "calculation_result": result}


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
        kaynama_noktasi=req.kaynama_noktasi
    )

