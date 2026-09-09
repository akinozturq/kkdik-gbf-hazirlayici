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


class SpecificConcentrationLimit(BaseModel):
    """
    CLP / SEA Spesifik Konsantrasyon Sınırı (SCL) hedefli veri yapısı.
    Zararlılık sınıfı, kategori ve/veya H-kodu ile tam hedeflenmiş eşleştirme sağlar.
    Örn:
    {
      "hazard_class": "Skin Corr.",
      "category": "1B",
      "h_code": "H314",
      "scl": 2.0
    }
    """
    hazard_class: Optional[str] = Field(None, description="Zararlılık sınıfı adı (örn. 'Skin Corr.')")
    category: Optional[str] = Field(None, description="Kategori veya alt kategori (örn. '1B')")
    h_code: Optional[str] = Field(None, description="H-kodu veya EUH-kodu (örn. 'H314')")
    scl: float = Field(..., description="Spesifik Konsantrasyon Sınırı (SCL - %)")

    model_config = ConfigDict(populate_by_name=True)


class MFactor(BaseModel):
    """
    Sucul toksisite M-Faktörü (Çarpan Katsayısı) ve denetim izi (audit trail) veri yapısı.
    CLP / SEA Ek-1 uyarınca M-faktörü belirtilmemişse hesaplama için varsayılan (effective_value=1.0)
    kullanılır, ancak denetim izinde kaynak 'DEFAULT' (value=None) olarak işaretlenir.
    Açıkça M=1 girilmişse value=1.0, effective_value=1.0, source='EXPLICIT' olur.
    """
    value: Optional[float] = Field(None, description="Bileşenin bilinen gerçek M-faktörü (belirtilmemişse None)")
    effective_value: float = Field(1.0, description="Hesaplamada fiilen kullanılan katsayı (varsayılan 1.0)")
    source: Literal["EXPLICIT", "ANNEX_VI", "DEFAULT"] = Field(
        "DEFAULT", description="M-faktörü kaynağı: EXPLICIT | ANNEX_VI | DEFAULT"
    )

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def create(
        cls,
        val: Optional[float] = None,
        source: Optional[Literal["EXPLICIT", "ANNEX_VI", "DEFAULT"]] = None
    ) -> "MFactor":
        if val is not None and float(val) > 0:
            return cls(
                value=float(val),
                effective_value=float(val),
                source=source or "EXPLICIT"
            )
        return cls(
            value=None,
            effective_value=1.0,
            source="DEFAULT"
        )


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
    m_acute_factor: Optional[MFactor] = Field(None, description="Yapılandırılmış Akut M-faktörü ve denetim izi")
    m_chronic_factor: Optional[MFactor] = Field(None, description="Yapılandırılmış Kronik M-faktörü ve denetim izi")
    has_euh066: bool = Field(False, description="Bu zararlılık veya bileşen açıkça EUH066 taşıyor mu?")
    euh066_source: Optional[str] = Field(None, description="EUH066 kaynak/uygulanabilirlik bilgisi ('explicit_code', 'annex_vi', 'supplier_sds')")

    @property
    def m_acute(self) -> MFactor:
        if self.m_acute_factor is not None:
            return self.m_acute_factor
        return MFactor.create(self.m_factor_acute)

    @property
    def m_chronic(self) -> MFactor:
        if self.m_chronic_factor is not None:
            return self.m_chronic_factor
        return MFactor.create(self.m_factor_chronic)

    model_config = ConfigDict(populate_by_name=True)

    def to_scl_entry(self) -> Optional[SpecificConcentrationLimit]:
        """Zararlılığın SCL değerini hedefli SpecificConcentrationLimit nesnesine dönüştürür."""
        if self.scl is not None:
            return SpecificConcentrationLimit(
                hazard_class=self.hazard_class,
                category=self.category,
                h_code=self.h_code,
                scl=self.scl
            )
        return None

    def to_scl_dict(self) -> Optional[Dict[str, Any]]:
        """Zararlılığın SCL değerini sözlük formatında döner."""
        if self.scl is not None:
            return {
                "hazard_class": self.hazard_class,
                "category": self.category,
                "h_code": self.h_code,
                "scl": self.scl
            }
        return None


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
    has_euh066: bool = Field(False, description="Bileşen açıkça EUH066 taşıyor mu?")
    euh066_source: Optional[str] = Field(None, description="EUH066 kaynak/dayanak bilgisi")
    
    # Akut toksisite değerleri
    ate_oral: Optional[float] = Field(None, description="Oral ATE (mg/kg)")
    ate_dermal: Optional[float] = Field(None, description="Dermal ATE (mg/kg)")
    inhalation: Optional[InhalationExposure] = Field(None, description="Soluma ATE ve maruziyet formu")
    
    # Özel kimyasal özellikler
    is_isocyanate: bool = Field(False, description="İzosiyanat türevi mi?")
    m_factor_acute: Optional[float] = Field(None, description="Sucul Akut 1 M-faktörü")
    m_factor_chronic: Optional[float] = Field(None, description="Sucul Kronik 1 M-faktörü")
    m_acute_factor: Optional[MFactor] = Field(None, description="Yapılandırılmış Akut M-faktörü ve denetim izi")
    m_chronic_factor: Optional[MFactor] = Field(None, description="Yapılandırılmış Kronik M-faktörü ve denetim izi")

    @property
    def m_acute(self) -> MFactor:
        if self.m_acute_factor is not None:
            return self.m_acute_factor
        return MFactor.create(self.m_factor_acute)

    @property
    def m_chronic(self) -> MFactor:
        if self.m_chronic_factor is not None:
            return self.m_chronic_factor
        return MFactor.create(self.m_factor_chronic)

    @property
    def structured_scls(self) -> List[SpecificConcentrationLimit]:
        """Bileşenin tüm zararlılıklarına ait hedefli SCL kayıtlarını döner."""
        return [h.to_scl_entry() for h in self.hazards if h.scl is not None]

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
    status: Literal["DEFINITELY_TRUE", "INDETERMINATE"] = Field(
        "DEFINITELY_TRUE",
        description="Konsantrasyon aralığı kesinlik durumu: DEFINITELY_TRUE (Kesin) | INDETERMINATE (Aralık Eşiği / Belirsiz)"
    )
    status_label: Optional[str] = Field("Kesin", description="Kullanıcı dostu durum etiketi ('Kesin' veya 'Belirsiz (Aralık Eşiği)')")
    range_details: Optional[str] = Field(None, description="Aralık belirsizliği detay açıklaması")


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
    has_indeterminate: bool = Field(False, description="Kural kapsamında aralığa bağlı belirsizlik (INDETERMINATE) var mı?")


class ClassificationResult(BaseModel):
    """
    Tüm kuralların birleşimi ve etiket önceliklendirmesi sonrası nihai karışım çıktısı.
    """
    siniflandirmalar: List[Dict[str, Any]] = Field(default_factory=list)
    h_ifadeleri: List[str] = Field(default_factory=list)
    euh_ifadeleri: List[str] = Field(default_factory=list)
    piktogramlar: List[str] = Field(default_factory=list)
    uyari_kelimesi: str = Field("Yok")
    p_ifadeleri: List[str] = Field(default_factory=list)
    calculation_steps: List[str] = Field(default_factory=list)
    rule_results: List[RuleResult] = Field(default_factory=list)
    has_indeterminate: bool = Field(False, description="Karışım genelinde aralık belirsizliği (INDETERMINATE) var mı?")
    indeterminate_hazards: List[Dict[str, Any]] = Field(default_factory=list, description="Aralığa bağlı belirsiz sınıflandırmalar")

