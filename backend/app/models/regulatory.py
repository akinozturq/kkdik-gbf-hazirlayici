"""
KKDİK ve SEA Yönetmeliği v2.0 Yapısal Regülatif Veri Modelleri
(Structured Regulatory Substance & Calculation Context Models)
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Literal, Dict, Any, Set, Union
from pydantic import BaseModel, Field, ConfigDict, model_validator


class ConcentrationValue(BaseModel):
    """
    Nitelikli konsantrasyon modeli.
    Fiziksel ve regülatif kısıt: 0 <= konsantrasyon <= 100
    Örn: 15% -> value=15.0, qualifier='exact'
    < 0.1% -> value=0.0999, qualifier='less_than'
    10 - 25% -> value=25.0, min_val=10.0, max_val=25.0, qualifier='range'
    """
    value: float = Field(..., ge=0.0, le=100.0, description="Hesaplamada kullanılan sayısal üst sınır veya tam konsantrasyon (%0-%100)")
    min_val: Optional[float] = Field(None, ge=0.0, le=100.0, description="Aralık belirtilmişse alt sınır (%0-%100)")
    max_val: Optional[float] = Field(None, ge=0.0, le=100.0, description="Aralık belirtilmişse üst sınır (%0-%100)")
    qualifier: Literal["exact", "less_than", "greater_than", "range"] = Field(
        "exact", description="Konsantrasyon niteleyicisi"
    )
    raw_text: Optional[str] = Field(None, description="Ham girdi metni (örn. '%10-25')")

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_range_bounds(self) -> "ConcentrationValue":
        if self.min_val is not None and self.max_val is not None:
            if self.min_val > self.max_val:
                raise ValueError(
                    f"Konsantrasyon alt sınırı (%{self.min_val}), üst sınırından (%{self.max_val}) büyük olamaz."
                )
        return self


class SpecificConcentrationLimit(BaseModel):
    """
    CLP / SEA Spesifik Konsantrasyon Sınırı (SCL) hedefli veri yapısı.
    Fiziksel kısıt: 0 < SCL <= 100
    """
    hazard_class: Optional[str] = Field(None, description="Zararlılık sınıfı adı (örn. 'Skin Corr.')")
    category: Optional[str] = Field(None, description="Kategori veya alt kategori (örn. '1B')")
    h_code: Optional[str] = Field(None, description="H-kodu veya EUH-kodu (örn. 'H314')")
    scl: float = Field(..., gt=0.0, le=100.0, description="Spesifik Konsantrasyon Sınırı (SCL - %0-%100 arası)")

    model_config = ConfigDict(populate_by_name=True)


class MFactor(BaseModel):
    """
    Sucul toksisite M-Faktörü (Çarpan Katsayısı) ve denetim izi (audit trail) veri yapısı.
    CLP / SEA Ek-1 uyarınca M-faktörü daima >= 1.0 tamsayı/katsayıdır.
    """
    value: Optional[float] = Field(None, ge=1.0, description="Bileşenin bilinen gerçek M-faktörü (CLP/SEA uyarınca M >= 1.0)")
    effective_value: float = Field(1.0, ge=1.0, description="Hesaplamada fiilen kullanılan katsayı (varsayılan 1.0, M >= 1.0)")
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
        if val is not None and float(val) >= 1.0:
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
    scl: Optional[float] = Field(None, gt=0.0, le=100.0, description="Varsa Spesifik Konsantrasyon Sınırı (SCL - %0-%100)")
    m_factor_acute: Optional[float] = Field(None, ge=1.0, description="Sucul Akut 1 M-faktörü (>= 1.0)")
    m_factor_chronic: Optional[float] = Field(None, ge=1.0, description="Sucul Kronik 1 M-faktörü (>= 1.0)")
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
    ate: float = Field(..., gt=0.0, description="Sayısal ATE değeri (ATE > 0 olmalıdır)")
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
    ate_val: Optional[float] = Field(None, gt=0.0, description="Bileşenin bilinen soluma ATE değeri (> 0)")
    form: Literal["buhar", "gaz", "toz_sis"] = Field("buhar", description="Fiziksel maruziyet formu")
    unit: str = Field("mg/L", description="Birim (Gaz için ppmV, buhar ve toz için mg/L)")
    provenance: Optional[ATEProvenance] = Field(None, description="Soluma ATE menşei / denetim izi")

    model_config = ConfigDict(populate_by_name=True)


class SubstanceDataQuality(BaseModel):
    """
    Tek bir bileşene ait veri kalitesi ve regülatif güvenilirlik değerlendirmesi (DATA QUALITY).
    Girdi verisinin (konsantrasyon, zararlılık sınıfı, fiziksel testler vb.) kesinliğini modeller.
    Örn: Konsantrasyon = %10-25 -> UNCERTAIN
    """
    quality_level: Literal["CONFIRMED", "UNCERTAIN", "INCOMPLETE", "CONTRADICTORY"] = Field(
        "CONFIRMED",
        description="Genel veri kalitesi seviyesi: CONFIRMED (Kesin) | UNCERTAIN (Belirsiz/Aralık) | INCOMPLETE (Eksik Veri) | CONTRADICTORY (Çelişkili)"
    )
    concentration_quality: Literal["EXACT", "UNCERTAIN", "BOUNDED", "ESTIMATED"] = Field(
        "EXACT",
        description="Konsantrasyon kalitesi: EXACT (Tam değer) | UNCERTAIN (Aralık) | BOUNDED (Sınır) | ESTIMATED (Tahmini)"
    )
    hazard_quality: Literal["CONFIRMED", "CATEGORY_UNRESOLVED", "SYNTACTIC_ONLY", "CONTRADICTORY"] = Field(
        "CONFIRMED",
        description="Zararlılık kalitesi: CONFIRMED | CATEGORY_UNRESOLVED | SYNTACTIC_ONLY | CONTRADICTORY"
    )
    uncertainty_score: float = Field(
        0.0,
        description="Belirsizlik skoru (0.0 = kesin, 1.0 = azami belirsizlik)"
    )
    flags: List[str] = Field(
        default_factory=list,
        description="Veri kalitesi uyarı bayrakları (örn. 'CONCENTRATION_RANGE_UNCERTAINTY')"
    )
    details: List[str] = Field(
        default_factory=list,
        description="Doğrulama ve denetim gerekçeleri"
    )

    model_config = ConfigDict(populate_by_name=True)


class StructuredSubstance(BaseModel):
    """
    Tip güvenli, yapılandırılmış regülatif kimyasal madde profili.
    """
    name: str = Field(..., description="Bileşen adı")
    cas_no: Optional[str] = Field(None, description="CAS Numarası")
    ec_no: Optional[str] = Field(None, description="EC Numarası")
    concentration: ConcentrationValue = Field(..., description="Nitelikli konsantrasyon nesnesi (%0-%100)")
    hazards: List[HazardEntry] = Field(default_factory=list, description="Ayrıştırılmış zararlılık listesi")
    raw_h_codes: List[str] = Field(default_factory=list, description="H-kodları listesi")
    has_euh066: bool = Field(False, description="Bileşen açıkça EUH066 taşıyor mu?")
    euh066_source: Optional[str] = Field(None, description="EUH066 kaynak/dayanak bilgisi")
    data_quality: SubstanceDataQuality = Field(
        default_factory=SubstanceDataQuality,
        description="Bileşen veri kalitesi ve güvenilirlik değerlendirmesi"
    )
    
    # Akut toksisite değerleri (Fiziksel kısıt: ATE > 0)
    ate_oral: Optional[float] = Field(None, gt=0.0, description="Oral ATE (mg/kg, > 0)")
    ate_dermal: Optional[float] = Field(None, gt=0.0, description="Dermal ATE (mg/kg, > 0)")
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
    
    # Özel kimyasal özellikler (CLP kısıtı: M >= 1.0)
    is_isocyanate: bool = Field(False, description="İzosiyanat türevi mi?")
    m_factor_acute: Optional[float] = Field(None, ge=1.0, description="Sucul Akut 1 M-faktörü (>= 1.0)")
    m_factor_chronic: Optional[float] = Field(None, ge=1.0, description="Sucul Kronik 1 M-faktörü (>= 1.0)")
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


class MixtureDataQuality(BaseModel):
    """
    Karışım genel veri kalitesi, belirsizlik profili ve eksik test parametreleri (DATA QUALITY).
    """
    overall_quality: Literal["CONFIRMED", "UNCERTAIN", "INCOMPLETE", "CONTRADICTORY"] = Field(
        "CONFIRMED",
        description="Karışım genel veri kalitesi seviyesi"
    )
    quality_score: float = Field(
        100.0,
        description="0-100 arası veri kalitesi ve güvenilirlik puanı (100 = tam teyitli)"
    )
    has_uncertain_components: bool = Field(False, description="Belirsiz (UNCERTAIN) konsantrasyona sahip bileşen var mı?")
    has_unresolved_hazards: bool = Field(False, description="Kategorisi çözümlenememiş zararlılık var mı?")
    missing_physical_data: List[str] = Field(
        default_factory=list,
        description="Mevzuat kuralları için eksik olan fiziksel test verileri (parlama noktası, viskozite vb.)"
    )
    component_qualities: Dict[str, SubstanceDataQuality] = Field(
        default_factory=dict,
        description="Bileşen bazlı veri kalitesi haritası"
    )
    audit_notes: List[str] = Field(
        default_factory=list,
        description="Veri kalitesi denetim izi notları"
    )
    # REG-015: Toplam konsantrasyon denetimi (Σ component concentration)
    total_concentration_min: Optional[float] = Field(
        None,
        description="Bileşenlerin minimum toplam konsantrasyonu (%)"
    )
    total_concentration_max: Optional[float] = Field(
        None,
        description="Bileşenlerin maksimum toplam konsantrasyonu (%)"
    )
    total_concentration_nominal: Optional[float] = Field(
        None,
        description="Bileşenlerin nominal toplam konsantrasyonu (%)"
    )
    total_concentration_status: Literal["VALID", "UNCERTAIN", "EXCEEDS_100"] = Field(
        "VALID",
        description="Toplam konsantrasyon uygunluk durumu (VALID, UNCERTAIN, EXCEEDS_100)"
    )
    total_concentration_error: Optional[str] = Field(
        None,
        description="Toplam konsantrasyon %100'ü aştığında üretilen hata mesajı"
    )

    model_config = ConfigDict(populate_by_name=True)


class CalculationContext(BaseModel):
    """
    Karışımın test verileri ve operasyonel fiziksel parametreleri.
    """
    parlama_noktasi: Optional[float] = Field(None, description="Karışımın ölçülmüş parlama noktası (°C)")
    kaynama_noktasi: Optional[float] = Field(None, description="Karışımın kaynama noktası (°C)")
    kinematik_viskozite_40c: Optional[float] = Field(None, gt=0.0, description="Karışımın 40°C'deki kinematik viskozitesi (mm²/s, > 0)")
    ph: Optional[float] = Field(None, description="Ölçülmüş pH değeri")
    fiziksel_hal: Optional[str] = Field("Sıvı", description="Karışımın fiziksel hali (Sıvı, Katı, Gaz)")
    data_quality: Optional[MixtureDataQuality] = Field(
        None,
        description="Karışım genel veri kalitesi ve fiziksel test gereksinimleri değerlendirmesi"
    )

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
    Tek bir kural stratejisinin ürettiği kanıta dayalı (evidence-based) düzenleyici karar ve denetim sonucu.
    SEA Ek-1 ve ECHA rehberlerine uygun yapısal denetim izi (audit trail) sağlar.
    """
    rule_name: str = Field(..., description="Kural adı (örn. 'FlammableLiquidRule')")
    rule: Optional[str] = Field(None, description="Kural adı alias (örn. 'AspirationHazardRule')")

    status: Literal["SUFFICIENT", "INSUFFICIENT_DATA", "INDETERMINATE", "NOT_APPLICABLE"] = Field(
        "SUFFICIENT",
        description="Kural değerlendirme durumu: SUFFICIENT | INSUFFICIENT_DATA | INDETERMINATE | NOT_APPLICABLE"
    )
    data_status: Literal["SUFFICIENT", "INSUFFICIENT_DATA", "INDETERMINATE", "NOT_APPLICABLE"] = Field(
        "SUFFICIENT",
        description="Geriye dönük uyumluluk için veri yeterlilik durumu"
    )

    hazards: List[ClassifiedHazard] = Field(default_factory=list, description="Atanan tehlikeler")
    evidence: Union[Dict[str, Any], List[Any]] = Field(
        default_factory=dict,
        description="Karar için kullanılan kanıtlar, konsantrasyon toplamları ve test verileri"
    )
    calculations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Adım adım formüller ve hesaplanan matematiksel değerler"
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Hesaplama ve değerlendirme varsayımları"
    )
    source_references: List[str] = Field(
        default_factory=list,
        description="Mevzuat ve kılavuz referansları (SEA Ek-1, CLP Annex I vb.)"
    )
    decision: Optional[str] = Field(
        None,
        description="Alınan nihai karar / sınıflandırma kodu (örn. 'Asp. Tox. 1 H304') veya None"
    )
    reason: Optional[str] = Field(
        None,
        description="Kararın veya belirsizliğin (INDETERMINATE / INSUFFICIENT_DATA) gerekçesi"
    )

    euh_codes: List[str] = Field(default_factory=list, description="Tetiklenen EUH kodları")
    piktogramlar: List[str] = Field(default_factory=list, description="Önerilen GHS piktogramları")
    uyari_kelimesi: Optional[str] = Field(None, description="'Tehlike' veya 'Dikkat'")
    calculation_notes: List[str] = Field(default_factory=list, description="Adım adım denetim açıklamaları")
    has_indeterminate: bool = Field(False, description="Kural kapsamında aralığa bağlı belirsizlik (INDETERMINATE) var mı?")

    @model_validator(mode="before")
    @classmethod
    def _sync_fields_before(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # rule <-> rule_name
            if "rule" in data and not data.get("rule_name"):
                data["rule_name"] = data["rule"]
            elif "rule_name" in data and not data.get("rule"):
                data["rule"] = data["rule_name"]

            # status <-> data_status
            if "status" in data and "data_status" not in data:
                data["data_status"] = data["status"]
            elif "data_status" in data and "status" not in data:
                data["status"] = data["data_status"]
        return data

    @model_validator(mode="after")
    def _sync_fields_after(self) -> "RuleResult":
        if not self.rule:
            self.rule = self.rule_name
        if not self.rule_name:
            self.rule_name = self.rule
        if self.status and not self.data_status:
            self.data_status = self.status
        elif self.data_status and not self.status:
            self.status = self.data_status
        return self

    def __setattr__(self, name: str, value: Any):
        super().__setattr__(name, value)
        if name == "status" and getattr(self, "data_status", None) != value:
            super().__setattr__("data_status", value)
        elif name == "data_status" and getattr(self, "status", None) != value:
            super().__setattr__("status", value)
        elif name == "rule_name" and getattr(self, "rule", None) != value:
            super().__setattr__("rule", value)
        elif name == "rule" and getattr(self, "rule_name", None) != value:
            super().__setattr__("rule_name", value)


class RegulatoryDecision(BaseModel):
    """
    Otoriter ve Değişmez Düzenleyici Karar (Regulatory Decision).
    Mevzuat kural motorunun (SEA / CLP) formülasyon ve test verilerine göre
    aldığı saf sınıflandırma ve yasal durum kararıdır.
    SDS dokümanı, etiket grafiği veya dilden bağımsızdır.
    """
    decision_id: str = Field(default_factory=lambda: f"DEC-{uuid.uuid4().hex[:8].upper()}", description="Benzersiz karar kimliği")
    product_identifier: Optional[str] = Field(None, description="Varsa ürün/karışım adı veya ticari kodu")
    data_quality: Optional[MixtureDataQuality] = Field(None, description="Karışım veri kalitesi profili")
    hazards: List[ClassifiedHazard] = Field(default_factory=list, description="Kesinleşen zararlılık sınıfları")
    indeterminate_hazards: List[ClassifiedHazard] = Field(
        default_factory=list, description="Aralık eşiğinde kalan (belirsiz) zararlılıklar"
    )
    evidence_pack: List[RuleResult] = Field(default_factory=list, description="Kural bazlı kanıt modelleri paketi")
    h_codes: List[str] = Field(default_factory=list, description="Karar verilen H-kodları listesi")
    euh_codes: List[str] = Field(default_factory=list, description="Karar verilen EUH-kodları listesi")
    has_indeterminate: bool = Field(False, description="Aralığa bağlı belirsizlik var mı?")
    has_classification: bool = Field(False, description="En az bir zararlılık sınıfı oluştu mu?")
    regulatory_frameworks: List[str] = Field(
        default_factory=lambda: ["SEA (Mükerrer RG: 28848)", "CLP (EC 1272/2008)"],
        description="Dayanak alınan mevzuat çerçeveleri"
    )
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Karar zaman damgası")
    audit_notes: List[str] = Field(default_factory=list, description="Karar mekanizması özet notları")

    model_config = ConfigDict(populate_by_name=True)


class RegulatoryLabel(BaseModel):
    """
    Düzenleyici Kararın Fiziksel / Ambalaj Etiket Projeksiyonu (Label Projection).
    SEA Madde 19-33 ve CLP Madde 17-33 uyarınca etiket elemanlarını modeller.
    """
    signal_word: str = Field("Yok", description="Uyarı kelimesi ('Tehlike', 'Dikkat' veya 'Yok')")
    pictograms: List[str] = Field(default_factory=list, description="GHS Piktogramları (GHS01 - GHS09)")
    hazard_statements: List[str] = Field(default_factory=list, description="H-kodları")
    supplemental_statements: List[str] = Field(default_factory=list, description="EUH-kodları")
    precautionary_statements: List[str] = Field(default_factory=list, description="SEA Ek-4 P-kodları")
    precedence_audit_log: List[Dict[str, Any]] = Field(
        default_factory=list, description="Piktogram eleme denetim izi"
    )
    tactile_warning_required: bool = Field(
        False, description="Dokunulabilir Tehlike İşareti zorunlu mu? (SEA Md. 33 / CLP Ek-II)"
    )
    child_resistant_fastening_required: bool = Field(
        False, description="Çocuk Emniyetli Kapak zorunlu mu? (SEA Md. 33 / CLP Ek-II)"
    )

    model_config = ConfigDict(populate_by_name=True)


class TransportClassification(BaseModel):
    """
    Düzenleyici Kararın ADR / RID / IMDG Taşımacılık Projeksiyonu (Transport Projection).
    """
    un_number: Optional[str] = Field(None, description="UN Numarası (örn. 'UN 1263')")
    proper_shipping_name_tr: Optional[str] = Field(None, description="Uygun Taşıma Adı (Türkçe)")
    proper_shipping_name_en: Optional[str] = Field(None, description="Proper Shipping Name (İngilizce)")
    class_code: Optional[str] = Field(None, description="ADR Sınıf Kodu ('3', '8', '9', '6.1' vb.)")
    class_label: Optional[str] = Field(None, description="ADR Sınıf Tanımı (örn. '3 (Alevlenir Sıvılar)')")
    packing_group: Optional[str] = Field(None, description="Paketleme Grubu ('PG I', 'PG II', 'PG III')")
    packing_group_label: Optional[str] = Field(None, description="PG Etiketi")
    environmental_hazards: bool = Field(False, description="Çevre için tehlikeli madde (Marine Pollutant) mi?")
    environmental_hazards_tr: Optional[str] = Field(None, description="Çevresel zararlar Türkçe açıklaması")
    environmental_hazards_en: Optional[str] = Field(None, description="Çevresel zararlar İngilizce açıklaması")
    tunnel_restriction_code: Optional[str] = Field(None, description="Tünel Kısıtlama Kodu (örn. '(D/E)', '(E)')")
    special_provisions: List[str] = Field(default_factory=list, description="ADR Özel Hükümleri (örn. SP 163, SP 274)")
    user_special_precautions: Optional[str] = Field(None, description="Kullanıcı için özel önlemler (Bölüm 14.6)")
    status: str = Field("SUGGESTION", description="Durum ('SUGGESTION', 'CONFIRMED')")
    status_label: str = Field("⚠️ Taslak Öneri (TMGD Doğrulaması Gerekir)", description="Durum etiketi")
    disclaimer: Optional[str] = Field(None, description="Yasal sorumluluk reddi beyanı")
    adr_table_a_reference: Optional[str] = Field(None, description="ADR Tablo A referansı")
    audit_note: Optional[str] = Field(None, description="Sınıflandırma gerekçesi ve notlar")

    model_config = ConfigDict(populate_by_name=True)


class AuditTrailEntry(BaseModel):
    """
    Tekil Denetim İzi Kaydı (Audit Trail Entry).
    """
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    stage: Literal[
        "INPUT", "NORMALIZATION", "DATA_QUALITY",
        "RULE_EXECUTION", "DECISION", "LABEL", "TRANSPORT", "SDS"
    ] = Field(..., description="Boru hattı aşaması")
    action: str = Field(..., description="Yapılan işlem özeti")
    details: Dict[str, Any] = Field(default_factory=dict, description="İşlem detayları ve sayısal veriler")
    legislative_reference: Optional[str] = Field(None, description="Mevzuat maddesi / yasal dayanak")

    model_config = ConfigDict(populate_by_name=True)


class RegulatoryAuditTrail(BaseModel):
    """
    Uçtan Uca Birleşik Regülatif Denetim İzi (Unified Audit Trail).
    """
    decision_id: str = Field(..., description="İlgili karar kimliği")
    entries: List[AuditTrailEntry] = Field(default_factory=list, description="Kronolojik denetim kayıtları")
    summary: Optional[str] = Field(None, description="Genel denetim özeti")

    model_config = ConfigDict(populate_by_name=True)


class ClassificationResult(BaseModel):
    """
    Tüm kuralların birleşimi ve etiket önceliklendirmesi sonrası nihai karışım çıktısı.
    Regulatory Decision, Regulatory Label, Transport ve Audit Trail'i bir arada sunan kompozit Facade.
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
    data_quality: Optional[MixtureDataQuality] = Field(
        None, description="Karışım veri kalitesi ve regülatif güvenilirlik profili"
    )
    precedence_audit_log: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Piktogram öncelik ve eleme denetim izi (PictogramPrecedenceMatrix)"
    )

    # Kurumsal Regülasyon Karar Mimarisi Projeksiyonları:
    decision: Optional[RegulatoryDecision] = Field(
        None, description="Saf Düzenleyici Karar Nesnesi (Regulatory Decision)"
    )
    label: Optional[RegulatoryLabel] = Field(
        None, description="Etiket Projeksiyonu (Label Projection)"
    )
    transport: Optional[TransportClassification] = Field(
        None, description="Taşımacılık Projeksiyonu (Transport Projection)"
    )
    audit_trail: Optional[RegulatoryAuditTrail] = Field(
        None, description="Uçtan Uca Denetim İzi (Regulatory Audit Trail)"
    )


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

