"""
Referans Veri API Router'ı (H-kodları, P-kodları, Piktogramlar)
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.reference import HStatementItem, PStatementItem, PictogramItem
from app.services.reference_service import reference_service

router = APIRouter(prefix="/api/references", tags=["Mevzuat Referans Kütüphanesi"])


@router.get(
    "/h-statements",
    response_model=List[HStatementItem],
    summary="Tüm H-ifadeleri listesi (Zararlılık İfadeleri)"
)
def get_h_statements(
    category: Optional[str] = Query(None, description="Filtreleme: Fiziksel, Sağlık, Çevre, İlave"),
    search: Optional[str] = Query(None, description="Kod veya metin içi arama")
):
    """
    CLP / SEA / KKDİK uyumlu standart H-kodlarını ve resmi Türkçe açıklamalarını getirir.
    """
    return reference_service.get_all_h_statements(category=category, search=search)


@router.get(
    "/h-statements/{code}",
    response_model=HStatementItem,
    summary="Belirli bir H-kodu detayını getir"
)
def get_h_statement_by_code(code: str):
    item = reference_service.get_h_statement(code)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{code}' kodlu zararlılık ifadesi bulunamadı."
        )
    return item


@router.get(
    "/p-statements",
    response_model=List[PStatementItem],
    summary="Tüm P-ifadeleri listesi (Önlem İfadeleri)"
)
def get_p_statements(
    type_filter: Optional[str] = Query(None, alias="type", description="Filtreleme: Genel, Önlem, Müdahale, Depolama, Bertaraf"),
    search: Optional[str] = Query(None, description="Kod veya metin içi arama")
):
    """
    Standart P-kodlarını ve resmi Türkçe açıklamalarını getirir.
    """
    return reference_service.get_all_p_statements(type_filter=type_filter, search=search)


@router.get(
    "/p-statements/{code}",
    response_model=PStatementItem,
    summary="Belirli bir P-kodu detayını getir"
)
def get_p_statement_by_code(code: str):
    item = reference_service.get_p_statement(code)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{code}' kodlu önlem ifadesi bulunamadı."
        )
    return item


@router.get(
    "/pictograms",
    response_model=List[PictogramItem],
    summary="GHS Tehlike Piktogramları listesi (GHS01-GHS09)"
)
def get_pictograms():
    """
    GHS piktogram listesini (GHS01 - GHS09) ve açıklamalarını getirir.
    """
    return reference_service.get_all_pictograms()


@router.get(
    "/pictograms/{code}",
    response_model=PictogramItem,
    summary="Belirli bir piktogram detayını getir"
)
def get_pictogram_by_code(code: str):
    item = reference_service.get_pictogram(code)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{code}' kodlu piktogram bulunamadı."
        )
    return item


@router.get(
    "/exposure-limits",
    summary="Mesleki Maruziyet Sınır Değerleri Tablosu (311 Madde)"
)
def get_exposure_limits(
    search: Optional[str] = Query(None, description="Madde adı, CAS no veya EC no arama terimi")
):
    """
    Kimyasal Maddelerle Çalışmalarda Sağlık ve Güvenlik Önlemleri Hakkında Yönetmelik
    Ek-1 Mesleki Maruziyet Sınır Değerleri tablosunu döner.
    """
    return reference_service.get_all_exposure_limits(search=search)


@router.get(
    "/raw-materials",
    summary="Hammadde Kütüphanesi Listesi"
)
def get_raw_materials(
    search: Optional[str] = Query(None, description="Hammadde adı, ticari kod veya CAS no arama terimi")
):
    """
    Hammadde kütüphanesindeki kimyasal maddeleri (Aseton, Toluen vb.) döner.
    """
    return reference_service.get_all_raw_materials(search=search)


@router.get(
    "/raw-materials/{id_or_cas}",
    summary="Hammadde Detayı"
)
def get_raw_material_by_id(id_or_cas: str):
    """
    Belirli bir hammaddenin tüm teknik ve mevzuat özelliklerini getirir.
    """
    item = reference_service.get_raw_material_by_id(id_or_cas)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{id_or_cas}' kimlikli hammadde bulunamadı."
        )
    return item


