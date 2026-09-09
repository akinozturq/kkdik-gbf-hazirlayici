"""
Referans Veri Şemaları (H-İfadeleri, P-İfadeleri, GHS Piktogramları)
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class HStatementItem(BaseModel):
    code: str = Field(..., description="H-kodu (ör. 'H225')")
    category: str = Field(..., description="Zararlılık grubu (Fiziksel, Sağlık, Çevre, İlave)")
    text: str = Field(..., description="Türkçe standart zararlılık ifadesi metni")


class PStatementItem(BaseModel):
    code: str = Field(..., description="P-kodu (ör. 'P210', 'P301+P310')")
    type: str = Field(..., description="Önlem türü (Genel, Önlem, Müdahale, Depolama, Bertaraf)")
    text: str = Field(..., description="Türkçe standart önlem ifadesi metni")


class PictogramItem(BaseModel):
    code: str = Field(..., description="Piktogram kodu (ör. 'GHS02')")
    name: str = Field(..., description="Piktogram Türkçe adı")
    symbol: str = Field(..., description="Sembol açıklaması")
    description: str = Field(..., description="Kapsadığı zararlılık sınıfları")


class AutoFillHResponse(BaseModel):
    product_id: int
    found_h_codes: List[str] = Field(default_factory=list, description="SDS içerisinden tespit edilen H-kodları")
    h_statements: List[HStatementItem] = Field(default_factory=list, description="Kodlara karşılık gelen tam Türkçe metinler")
    formatted_texts: List[str] = Field(default_factory=list, description="Bölüm 16'ya yazılmaya hazır biçimlendirilmiş metinler ('H225: Kolay alevlenir sıvı...')")
    updated_section16: bool = Field(False, description="Ürün Bölüm 16'sına otomatik kaydedildi mi")


class RawMaterialSchema(BaseModel):
    id: Optional[str] = Field(None, description="Benzersiz ID (ör. 'raw-aseton')")
    ad: str = Field(..., description="Kimyasal veya hammadde adı (ör. 'Aseton')")
    ticari_ad: Optional[str] = Field("", description="Ticari adı veya formülasyon kodu")
    iupac_adi: Optional[str] = Field("", description="IUPAC sistematik adı")
    cas_no: Optional[str] = Field("", description="CAS Numarası")
    ec_no: Optional[str] = Field("", description="EC / EINECS Numarası")
    kayit_no: Optional[str] = Field("", description="REACH / KKDİK Kayıt Numarası")
    molekul_formulu: Optional[str] = Field("", description="Kimyasal formül")
    molekul_agirligi: Optional[str] = Field("", description="Molekül ağırlığı")
    kategori: Optional[str] = Field("Genel", description="Kategori (Solventler, Sertleştiriciler, Reçineler, Katkılar, Pigmentler vb.)")
    fiziksel_hal: Optional[str] = Field("Sıvı", description="Fiziksel hal ve görünüm")
    siniflandirma_str: Optional[str] = Field("", description="CLP/SEA sınıflandırma dizesi")
    h_kodlari: Optional[List[str]] = Field(default_factory=list, description="H-kodları listesi")
    piktogramlar: Optional[List[str]] = Field(default_factory=list, description="GHS Piktogramları listesi")
    uyari_kelimesi: Optional[str] = Field("Uyarı", description="Uyarı kelimesi (Tehlike / Uyarı)")
    maruziyet_limitleri: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Mesleki maruziyet sınır değerleri (TWA, STEL)")
    fiziksel_ozellikler: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Fiziksel ve kimyasal özellikler")
    toksikolojik_bilgiler: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Toksikolojik özet metinleri")
    akut_toksisite_oral: Optional[float] = Field(None, description="Akut oral LD50 (mg/kg)")
    akut_toksisite_dermal: Optional[float] = Field(None, description="Akut dermal LD50 (mg/kg)")
    akut_toksisite_soluma: Optional[float] = Field(None, description="Akut soluma LC50 (mg/L)")
    akut_toksisite_soluma_formu: Optional[str] = Field("buhar", description="Soluma formu (buhar, toz_sis, gaz)")
    is_isocyanate: Optional[bool] = Field(False, description="İzosiyanat türevi mi (EUH204 tetikler)")
    m_faktoru_akut: Optional[int] = Field(None, description="Akut sucul M faktörü")
    m_faktoru_kronik: Optional[int] = Field(None, description="Kronik sucul M faktörü")
    ekolojik_bilgiler: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Ekotoksikolojik veriler")
    tasimacilik_bilgileri: Optional[Dict[str, Any]] = Field(default_factory=dict, description="ADR / UN taşıma bilgileri")

