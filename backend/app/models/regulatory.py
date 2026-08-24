"""
KKDİK ve SEA Yönetmeliği v2.0 Yapısal Regülatif Veri Modelleri
(Structured Regulatory Substance & Calculation Context Models)
"""

from typing import List, Optional, Literal, Dict, Any, Set
from pydantic import BaseModel, Field, ConfigDict


class ConcentrationValue(BaseModel):
    """
    Nitelikli konsantrasyon modeli.
    Örn: 15% -> value=15.0, qualifier='exact'
    < 0.1% -> value=0.0999, qualifier='less_than'
    10 - 25% -> value=25.0, min_val=10.0, max_val=25.0, qualifier='range'
    """
    value: float = Field(..., description="Hesaplamada kullanılan sayısal üst sınır veya tam konsantrasyon")
    min_val: Optional[float] = Field(None, description="Aralık belirtilmişse alt sınır")
    max_val: Optional[float] = Field(None, description="Aralık belirtilmişse üst sınır")
    qualifier: Literal["exact", "less_than", "greater_than", "range"] = Field(
        "exact", description="Konsantrasyon niteleyicisi"
    )
    raw_text: Optional[str] = Field(None, description="Ham girdi metni (örn. '%10-25')")

    model_config = ConfigDict(populate_by_name=True)


class HazardEntry(BaseModel):
    """
    Bir bileşenin tekil zararlılık sınıfı profili.
    Örn: hazard_class="Skin Corr. 1A", category="1A", h_code="H314"
    """
    hazard_class: str = Field(..., description="Zararlılık sınıfı adı (örn. 'Skin Corr.', 'Flam. Liq.')")
    category: str = Field(..., description="Kategori veya alt kategori (örn. '1A', '1B', 'Kat 2')")
    h_code: str = Field(..., description="H-kodu veya EUH-kodu (örn. 'H314', 'H225', 'EUH066')")
    scl: Optional[float] = Field(None, description="Varsa Spesifik Konsantrasyon Sınırı (SCL - %)")
    m_factor_acute: Optional[float] = Field(None, description="Sucul Akut 1 M-faktörü")
    m_factor_chronic: Optional[float] = Field(None, description="Sucul Kronik 1 M-faktörü")

    model_config = ConfigDict(populate_by_name=True)


class InhalationExposure(BaseModel):
    """
    Soluma yolu akut toksisite fiziksel maruziyet formu ve birimi.
    """
    ate_val: Optional[float] = Field(None, description="Bileşenin bilinen soluma ATE değeri")
    form: Literal["buhar", "gaz", "toz_sis"] = Field("buhar", description="Fiziksel maruziyet formu")
    unit: str = Field("mg/L", description="Birim (Gaz için ppmV, buhar ve toz için mg/L)")

    model_config = ConfigDict(populate_by_name=True)


class StructuredSubstance(BaseModel):
    """
    Tip güvenli, yapılandırılmış regülatif kimyasal madde profili.
    """
    name: str = Field(..., description="Bileşen adı")
    cas_no: Optional[str] = Field(None, description="CAS Numarası")
    ec_no: Optional[str] = Field(None, description="EC Numarası")
    concentration: ConcentrationValue = Field(..., description="Nitelikli konsantrasyon nesnesi")
    hazards: List[HazardEntry] = Field(default_factory=list, description="Ayrıştırılmış zararlılık listesi")
    raw_h_codes: List[str] = Field(default_factory=list, description="H-kodları listesi")
    
    # Akut toksisite değerleri
    ate_oral: Optional[float] = Field(None, description="Oral ATE (mg/kg)")
    ate_dermal: Optional[float] = Field(None, description="Dermal ATE (mg/kg)")
    inhalation: Optional[InhalationExposure] = Field(None, description="Soluma ATE ve maruziyet formu")
    
    # Özel kimyasal özellikler
    is_isocyanate: bool = Field(False, description="İzosiyanat türevi mi?")
    m_factor_acute: Optional[float] = Field(None, description="Sucul Akut 1 M-faktörü")
    m_factor_chronic: Optional[float] = Field(None, description="Sucul Kronik 1 M-faktörü")

    model_config = ConfigDict(populate_by_name=True)


class CalculationContext(BaseModel):
    """
    Karışımın test verileri ve operasyonel fiziksel parametreleri.
    """
    parlama_noktasi: Optional[float] = Field(None, description="Karışımın ölçülmüş parlama noktası (°C)")
    kaynama_noktasi: Optional[float] = Field(None, description="Karışımın kaynama noktası (°C)")
    kinematik_viskozite_40c: Optional[float] = Field(None, description="Karışımın 40°C'deki kinematik viskozitesi (mm²/s)")
    ph: Optional[float] = Field(None, description="Ölçülmüş pH değeri")
    fiziksel_hal: Optional[str] = Field("Sıvı", description="Karışımın fiziksel hali (Sıvı, Katı, Gaz)")

    model_config = ConfigDict(populate_by_name=True)


class ClassifiedHazard(BaseModel):
    """
    Kural motoru tarafından karışıma atanan nihai zararlılık kaydı.
    """
    zararlilik_sinifi: str = Field(..., description="Zararlılık sınıfı başlığı")
    kategori: str = Field(..., description="Atanan kategori")
    h_kodu: str = Field(..., description="Atanan H veya EUH kodu")


class RuleResult(BaseModel):
    """
    Tek bir kural stratejisinin ürettiği sonuç.
    """
    rule_name: str = Field(..., description="Kural adı (örn. 'FlammableLiquidRule')")
    hazards: List[ClassifiedHazard] = Field(default_factory=list, description="Atanan tehlikeler")
    euh_codes: List[str] = Field(default_factory=list, description="Tetiklenen EUH kodları")
    piktogramlar: List[str] = Field(default_factory=list, description="Önerilen GHS piktogramları")
    uyari_kelimesi: Optional[str] = Field(None, description="'Tehlike' veya 'Dikkat'")
    calculation_notes: List[str] = Field(default_factory=list, description="Adım adım denetim açıklamaları")
    data_status: Literal["SUFFICIENT", "INSUFFICIENT_DATA", "NOT_APPLICABLE"] = Field(
        "SUFFICIENT", description="Veri yeterlilik ve güvenilirlik durumu"
    )


class ClassificationResult(BaseModel):
    """
    Tüm kuralların birleşimi ve etiket önceliklendirmesi sonrası nihai karışım çıktısı.
    """
    siniflandirmalar: List[Dict[str, str]] = Field(default_factory=list)
    h_ifadeleri: List[str] = Field(default_factory=list)
    euh_ifadeleri: List[str] = Field(default_factory=list)
    piktogramlar: List[str] = Field(default_factory=list)
    uyari_kelimesi: str = Field("Yok")
    p_ifadeleri: List[str] = Field(default_factory=list)
    calculation_steps: List[str] = Field(default_factory=list)
    rule_results: List[RuleResult] = Field(default_factory=list)
