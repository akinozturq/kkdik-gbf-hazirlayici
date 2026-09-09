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


class STOTSE3Effect(BaseModel):
    """
    CLP / SEA Bölüm 3.8.3 uyarınca STOT SE 3 mekanizma ve uygulanabilirlik modeli.
    Solunum Yolu Tahrişi (RTI - H335) ve Narkotik Etkiler (NE - H336) iki bağımsız fizyolojik
    etkidir; toplanabilirlik havuzları, veri kaynakları ve uygulanabilirlik koşulları ayrı modellenir.
    """
    effect_type: Literal["respiratory_tract_irritation", "narcotic_effects"] = Field(
        ..., description="Etki tipi: 'respiratory_tract_irritation' (RTI - H335) veya 'narcotic_effects' (NE - H336)"
    )
    h_code: str = Field(..., description="İlgili H-kodu ('H335' veya 'H336')")
    source: Literal["CLASSIFICATION", "ANNEX_VI", "SUPPLIER_SDS", "EXPOSURE_DATA", "DEFAULT"] = Field(
        "CLASSIFICATION", description="Veri kaynağı veya dayanağı"
    )
    is_applicable: bool = Field(
        True, description="Karışımın fiziksel formu/maruziyet senaryosuna göre bu etki uygulanabilir mi?"
    )
    applicability_note: Optional[str] = Field(
        None, description="Uygulanabilirlik veya hariç tutma gerekçesi"
    )

    model_config = ConfigDict(populate_by_name=True)


class ValidationIssue(BaseModel):
    """
    Regülatif doğrulama kuralı ihlali, çelişki veya uyarı detayı.
    """
    code: str = Field(..., description="Bulgu kodu (örn. 'CLASS_CODE_MISMATCH', 'INVALID_SCL_BOUNDS')")
    severity: Literal["ERROR", "WARNING", "INFO"] = Field("WARNING", description="Önem seviyesi")
    message: str = Field(..., description="Kullanıcı ve denetçi için açıklayıcı mesaj")

    model_config = ConfigDict(populate_by_name=True)


class ParsedHazardAssertion(BaseModel):
    """
    Aşama 2: Ham metinden ayrıştırılmış doğrudan iddia (Parsed Assertion).
    Metnin ne iddia ettiğini kaydeder; mevzuat doğruluğu veya geçerliliği varsayımı yapmaz.
    Örn: 'Skin Corr. 1B H314 (SCL >= 1%)' ->
      raw_text='Skin Corr. 1B H314 (SCL >= 1%)'
      asserted_class='Skin Corr.'
      asserted_category='1B'
      asserted_codes=['H314']
      asserted_scl=1.0
      asserted_m_factor=None
    """
    raw_text: str = Field(..., description="Ayrıştırılan ham metin parçacığı")
    asserted_class: Optional[str] = Field(None, description="Metinde tespit edilen ham sınıf ifadesi")
    asserted_category: Optional[str] = Field(None, description="Metinde tespit edilen ham kategori ifadesi")
    asserted_codes: List[str] = Field(default_factory=list, description="Metinde bulunan ham H ve EUH kodları")
    asserted_scl: Optional[float] = Field(None, description="Metinde bulunan sayısal SCL değeri")
    asserted_m_factor: Optional[float] = Field(None, description="Metinde bulunan sayısal M-faktörü")
    has_euh066: bool = Field(False, description="Metinde EUH066 ifadesi veya kodu var mı?")
    parsing_notes: List[str] = Field(default_factory=list, description="Ayrıştırma esnasındaki gözlemler")

    model_config = ConfigDict(populate_by_name=True)


class NormalizedHazard(BaseModel):
    """
    Aşama 3: Standartlaştırılmış Regülatif Veri (Normalized Regulatory Data).
    Yazım varyasyonları, Türkçe terimler, kod biçimleri ve eksik alanlar
    kanonik CLP / SEA terminolojisine dönüştürülmüştür.
    """
    raw_assertion: ParsedHazardAssertion = Field(..., description="Dayanak oluşturan ham ayrıştırma iddiası")
    canonical_class: str = Field(..., description="Kanonik zararlılık sınıfı (örn. 'Skin Corr.')")
    canonical_category: str = Field(..., description="Kanonik kategori (örn. '1B', 'CATEGORY_UNRESOLVED')")
    canonical_code: str = Field(..., description="Kanonik H-kodu (örn. 'H314', 'H361d')")
    scl: Optional[float] = Field(None, description="Normalize edilmiş SCL değeri")
    m_factor: Optional[float] = Field(None, description="Normalize edilmiş M-faktörü")
    has_euh066: bool = Field(False, description="EUH066 normalize varlık bilgisi")
    euh066_source: Optional[str] = Field(None, description="EUH066 kaynak bilgisi")
    normalization_notes: List[str] = Field(default_factory=list, description="Normalizasyon notları ve yapılan düzeltmeler")

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
    m_acute_factor: Optional[MFactor] = Field(None, description="Yapılandırılmış Akut M-faktörü ve denetim izi")
    m_chronic_factor: Optional[MFactor] = Field(None, description="Yapılandırılmış Kronik M-faktörü ve denetim izi")
    has_euh066: bool = Field(False, description="Bu zararlılık veya bileşen açıkça EUH066 taşıyor mu?")
    euh066_source: Optional[str] = Field(None, description="EUH066 kaynak/uygulanabilirlik bilgisi ('explicit_code', 'annex_vi', 'supplier_sds')")
    stot_effect: Optional[STOTSE3Effect] = Field(None, description="STOT SE 3 etki ve kaynak modeli (H335/H336)")
    validation_status: Literal["VALID", "CORRECTED", "CONTRADICTORY", "INVALID", "UNRESOLVED"] = Field(
        "VALID", description="Regülatif doğrulama durumu: VALID | CORRECTED | CONTRADICTORY | INVALID | UNRESOLVED"
    )
    validation_issues: List[ValidationIssue] = Field(
        default_factory=list, description="Tespit edilen doğrulama bulguları ve uyarılar"
    )
    raw_assertion: Optional[str] = Field(None, description="Ayrıştırılan ham iddia metni")

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


class ValidatedHazard(BaseModel):
    """
    Aşama 4: Doğrulanmış Regülatif Veri (Validated Regulatory Data).
    CLP / SEA kurallarına (H-kodu vs sınıf tutarlılığı, kategori sınırları, SCL ve M-faktörü limitleri,
    CMR kategori çözünürlüğü) göre denetlenmiş ve doğrulanmış nesne.
    """
    normalized: NormalizedHazard = Field(..., description="Normalize edilmiş regülatif veri")
    status: Literal["VALID", "CORRECTED", "CONTRADICTORY", "INVALID", "UNRESOLVED"] = Field(
        "VALID", description="Doğrulama nihai durumu"
    )
    issues: List[ValidationIssue] = Field(default_factory=list, description="Tespit edilen doğrulama bulguları")
    is_applicable_for_classification: bool = Field(
        True, description="Bu zararlılık karışım sınıflandırma motorunda hesaba katılabilir mi?"
    )

    model_config = ConfigDict(populate_by_name=True)

    def to_hazard_entry(self) -> HazardEntry:
        """Sınıflandırma motorunun tüketeceği nihai tip güvenli HazardEntry nesnesine dönüştürür."""
        norm = self.normalized
        stot_eff = None
        if norm.canonical_code == "H335":
            stot_eff = STOTSE3Effect(
                effect_type="respiratory_tract_irritation",
                h_code="H335",
                source="CLASSIFICATION"
            )
        elif norm.canonical_code == "H336":
            stot_eff = STOTSE3Effect(
                effect_type="narcotic_effects",
                h_code="H336",
                source="CLASSIFICATION"
            )

        m_acute = norm.m_factor if ("Acute" in norm.canonical_class or norm.canonical_code == "H400") else None
        m_chronic = norm.m_factor if ("Chronic" in norm.canonical_class or norm.canonical_code == "H410") else None

        # SCL sadece geçerli ise atanır (INVALID_SCL_BOUNDS durumunda SCL motoru bozmasın)
        has_invalid_scl = any(i.code == "INVALID_SCL_BOUNDS" for i in self.issues)
        scl_val = None if has_invalid_scl else norm.scl

        # M-factor sadece geçerli ise atanır
        has_invalid_m = any(i.code in ("INVALID_M_FACTOR", "INAPPLICABLE_M_FACTOR") for i in self.issues)
        m_acute_val = None if has_invalid_m else m_acute
        m_chronic_val = None if has_invalid_m else m_chronic

        return HazardEntry(
            hazard_class=norm.canonical_class,
            category=norm.canonical_category,
            h_code=norm.canonical_code,
            scl=scl_val,
            m_factor_acute=m_acute_val,
            m_factor_chronic=m_chronic_val,
            has_euh066=norm.has_euh066,
            euh066_source=norm.euh066_source,
            stot_effect=stot_eff,
            validation_status=self.status,
            validation_issues=self.issues,
            raw_assertion=norm.raw_assertion.raw_text
        )


class ATEProvenance(BaseModel):
    """
    Akut Toksisite Tahmin Değeri (ATE) ve Menşei / Denetim İzi (Provenance) Modeli.
    SEA Ek-1 Bölüm 3.1 & Tablo 3.1.2 uyarınca hesaplanan veya girilen ATE değerinin
    kaynağını, türetilme yöntemini ve mevzuat referansını belgeler.
    Örnek:
    {
      "ate": 500.0,
      "value_source": "H302_CONVERSION",
      "source_type": "DERIVED",
      "source_reference": "SEA_ANNEX_I",
      "route": "oral",
      "unit": "mg/kg"
    }
    """
    ate: float = Field(..., description="Sayısal ATE değeri")
    value_source: str = Field(..., description="Değer kaynağı (örn. 'EXPLICIT_TEST_DATA', 'H302_CONVERSION', 'SUPPLIER_SDS')")
    source_type: Literal["EXPERIMENTAL", "DERIVED", "DEFAULT", "ESTIMATED"] = Field(
        "DERIVED", description="Kaynak tipi: EXPERIMENTAL (Deneysel) | DERIVED (Dönüştürülmüş) | DEFAULT | ESTIMATED"
    )
    source_reference: str = Field("SEA_ANNEX_I", description="Mevzuat veya standart referansı (örn. 'SEA_ANNEX_I', 'CLP_TABLE_3_1_2')")
    route: Optional[str] = Field(None, description="Maruziyet yolu ('oral', 'dermal', 'inhalation_vapour', 'inhalation_gas', 'inhalation_dust')")
    unit: str = Field("mg/kg", description="Ölçü birimi ('mg/kg', 'mg/L', 'ppmV')")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def create_experimental(
        cls,
        ate: float,
        route: str = "oral",
        unit: Optional[str] = None,
        source_ref: str = "EXPLICIT_TEST_DATA"
    ) -> "ATEProvenance":
        default_unit = "ppmV" if route == "inhalation_gas" else ("mg/L" if "inhalation" in route else "mg/kg")
        return cls(
            ate=float(ate),
            value_source="EXPLICIT_TEST_DATA",
            source_type="EXPERIMENTAL",
            source_reference=source_ref,
            route=route,
            unit=unit or default_unit
        )

    @classmethod
    def create_derived_conversion(
        cls,
        ate: float,
        h_code: str,
        route: str = "oral",
        unit: Optional[str] = None,
        source_ref: str = "SEA_ANNEX_I"
    ) -> "ATEProvenance":
        default_unit = "ppmV" if route == "inhalation_gas" else ("mg/L" if "inhalation" in route else "mg/kg")
        return cls(
            ate=float(ate),
            value_source=f"{h_code}_CONVERSION",
            source_type="DERIVED",
            source_reference=source_ref,
            route=route,
            unit=unit or default_unit
        )


class InhalationExposure(BaseModel):
    """
    Soluma yolu akut toksisite fiziksel maruziyet formu, birimi ve ATE menşei.
    """
    ate_val: Optional[float] = Field(None, description="Bileşenin bilinen soluma ATE değeri")
    form: Literal["buhar", "gaz", "toz_sis"] = Field("buhar", description="Fiziksel maruziyet formu")
    unit: str = Field("mg/L", description="Birim (Gaz için ppmV, buhar ve toz için mg/L)")
    provenance: Optional[ATEProvenance] = Field(None, description="Soluma ATE menşei / denetim izi")

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
    ate_oral_provenance: Optional[ATEProvenance] = Field(None, description="Oral ATE kaynak ve denetim izi")
    ate_dermal_provenance: Optional[ATEProvenance] = Field(None, description="Dermal ATE kaynak ve denetim izi")

    @property
    def oral_ate_model(self) -> Optional[ATEProvenance]:
        if self.ate_oral_provenance is not None:
            return self.ate_oral_provenance
        if self.ate_oral is not None and self.ate_oral > 0:
            return ATEProvenance.create_experimental(self.ate_oral, route="oral", unit="mg/kg")
        return None

    @property
    def dermal_ate_model(self) -> Optional[ATEProvenance]:
        if self.ate_dermal_provenance is not None:
            return self.ate_dermal_provenance
        if self.ate_dermal is not None and self.ate_dermal > 0:
            return ATEProvenance.create_experimental(self.ate_dermal, route="dermal", unit="mg/kg")
        return None
    
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


class HazardThreshold(BaseModel):
    """
    CLP / SEA Eşik ve Limit Abstraction Modeli.
    Cut-off (ilgili bileşen kesme sınırı), GCL (Genel Konsantrasyon Sınırı)
    ve SCL (Spesifik Konsantrasyon Sınırı) ayrımını ve hiyerarşisini modeller.
    """
    hazard_class: str = Field(..., description="Zararlılık sınıfı (örn. 'Skin Corr.', 'Eye Irrit.')")
    category: Optional[str] = Field(None, description="Kategori (örn. '1', '1A', '2')")
    h_code: Optional[str] = Field(None, description="İlgili H-kodu (örn. 'H314', 'H315', 'H318', 'H319')")
    cut_off: float = Field(1.0, description="Genel kesme sınırı (cut-off limit, varsayılan %1.0)")
    gcl: float = Field(..., description="Genel Konsantrasyon Sınırı (GCL - Generic Concentration Limit)")
    scl: Optional[float] = Field(None, description="Varsa Spesifik Konsantrasyon Sınırı (SCL)")

    @property
    def effective_cutoff(self) -> float:
        """
        CLP Madde 11(3) ve ECHA Rehberi uyarınca:
        Eğer SCL < cut_off ise, ilgili bileşen kesme sınırı SCL değerine düşer.
        Aksi takdirde genel cut-off (%1.0) geçerlidir.
        """
        if self.scl is not None and self.scl < self.cut_off:
            return self.scl
        return self.cut_off

    @property
    def effective_limit(self) -> float:
        """
        Sınıflandırma için geçerli olan eşik (SCL varsa SCL, yoksa GCL).
        """
        if self.scl is not None:
            return self.scl
        return self.gcl

    def is_relevant(self, concentration: float) -> bool:
        """
        Konsantrasyonun toplanabilirlik/hesaplama havuzuna dahil edilip edilmeyeceğini belirler.
        concentration >= effective_cutoff olmalıdır.
        """
        return concentration >= self.effective_cutoff

    def triggers_classification(self, concentration: float) -> bool:
        """
        Tekil olarak eşiği aşıp aşmadığını kontrol eder (örn. SCL veya tekil bileşen kuralı).
        """
        return concentration >= self.effective_limit

    @classmethod
    def create(
        cls,
        hazard_class: str,
        category: Optional[str] = None,
        h_code: Optional[str] = None,
        cut_off: float = 1.0,
        gcl: float = 0.0,
        scl: Optional[float] = None,
    ) -> "HazardThreshold":
        return cls(
            hazard_class=hazard_class,
            category=category,
            h_code=h_code,
            cut_off=cut_off,
            gcl=gcl,
            scl=scl,
        )

    model_config = ConfigDict(populate_by_name=True)

