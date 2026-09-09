"""
v2.0 Regulatory Pipeline & Strategy Pattern Bağımsız Birim Testleri
"""

import pytest
from app.models.regulatory import (
    ConcentrationValue,
    HazardEntry,
    StructuredSubstance,
    CalculationContext,
    InhalationExposure
)
from app.services.rules import (
    FlammableLiquidRule,
    AspirationHazardRule,
    AcuteToxicityRule,
    SkinEyeRule,
    CMRRule,
    AquaticRule
)
from app.services.regulatory_engine.pipeline import RegulatoryPipeline


def test_v2_concentration_model_qualifiers():
    """Konsantrasyon parser'ı exact, less_than ve range niteleyicilerini doğru üretmelidir."""
    p = RegulatoryPipeline

    # Exact
    c1 = p.parse_concentration_model("15.5%")
    assert c1.value == 15.5
    assert c1.qualifier == "exact"

    # Strict less than (< 0.1%)
    c2 = p.parse_concentration_model("< 0.1%")
    assert c2.value < 0.1
    assert c2.qualifier == "less_than"

    # Range (10 - 25%)
    c3 = p.parse_concentration_model("10-25%")
    assert c3.value == 25.0
    assert c3.min_val == 10.0
    assert c3.max_val == 25.0
    assert c3.qualifier == "range"


def test_v2_flammable_liquid_rule_isolated():
    """FlammableLiquidRule izole test: Parlama noktası < 23°C ve KN > 35°C -> Kat 2 (H225)"""
    rule = FlammableLiquidRule()
    context = CalculationContext(parlama_noktasi=18.0, kaynama_noktasi=56.0)
    substances = []

    res = rule.evaluate(context, substances)
    assert len(res.hazards) == 1
    assert res.hazards[0].h_kodu == "H225"
    assert res.hazards[0].kategori == "Kategori 2"
    assert "GHS02" in res.piktogramlar
    assert res.uyari_kelimesi == "Tehlike"


def test_v2_aspiration_rule_isolated():
    """AspirationHazardRule izole test: %12 H304 ve viskozite 15 mm²/s <= 20.5 -> H304 Kat 1"""
    rule = AspirationHazardRule()
    context = CalculationContext(kinematik_viskozite_40c=15.0)
    substances = [
        StructuredSubstance(
            name="Nafta",
            concentration=ConcentrationValue(value=12.0, qualifier="exact"),
            raw_h_codes=["H304"]
        )
    ]

    res = rule.evaluate(context, substances)
    assert len(res.hazards) == 1
    assert res.hazards[0].h_kodu == "H304"
    assert "GHS08" in res.piktogramlar


def test_v2_aspiration_rule_suppressed_by_viscosity():
    """AspirationHazardRule izole test: %12 H304 ancak viskozite 30 mm²/s > 20.5 -> Sınıflandırılmaz"""
    rule = AspirationHazardRule()
    context = CalculationContext(kinematik_viskozite_40c=30.0)
    substances = [
        StructuredSubstance(
            name="Ağır Reçine Solüsyonu",
            concentration=ConcentrationValue(value=12.0, qualifier="exact"),
            raw_h_codes=["H304"]
        )
    ]

    res = rule.evaluate(context, substances)
    assert len(res.hazards) == 0
    assert any("20.5 mm²/s" in note for note in res.calculation_notes)


def test_v2_cmr_repro_deterministic_resolution():
    """CMRRule izole test: H360D ve H360FD içeren karışımda deterministik olarak H360FD seçilmelidir."""
    rule = CMRRule()
    context = CalculationContext()
    substances = [
        StructuredSubstance(
            name="Bileşen 1",
            concentration=ConcentrationValue(value=0.5, qualifier="exact"),
            raw_h_codes=["H360D"],
            hazards=[HazardEntry(hazard_class="Repr. 1B", category="1B", h_code="H360D")]
        ),
        StructuredSubstance(
            name="Bileşen 2",
            concentration=ConcentrationValue(value=0.5, qualifier="exact"),
            raw_h_codes=["H360FD"],
            hazards=[HazardEntry(hazard_class="Repr. 1B", category="1B", h_code="H360FD")]
        )
    ]

    res = rule.evaluate(context, substances)
    assert len(res.hazards) == 1
    assert res.hazards[0].h_kodu == "H360FD"
    assert res.hazards[0].kategori == "Kategori 1B"


def test_v2_pipeline_full_execution():
    """RegulatoryPipeline boru hattının uçtan uca çalıştırılması"""
    pipeline = RegulatoryPipeline()
    context = CalculationContext(parlama_noktasi=12.0, kaynama_noktasi=78.0, kinematik_viskozite_40c=1.5)
    
    substances = [
        StructuredSubstance(
            name="Aseton",
            concentration=ConcentrationValue(value=50.0, qualifier="exact"),
            raw_h_codes=["H225", "H319", "H336", "EUH066"],
            ate_oral=5800.0
        ),
        StructuredSubstance(
            name="Etil Asetat",
            concentration=ConcentrationValue(value=50.0, qualifier="exact"),
            raw_h_codes=["H225", "H319", "H336", "EUH066"],
            ate_oral=5620.0
        )
    ]

    result = pipeline.execute(substances, context)
    
    assert "H225" in result.h_ifadeleri
    assert "H319" in result.h_ifadeleri
    assert "H336" in result.h_ifadeleri
    assert "EUH066" in result.euh_ifadeleri
    assert "GHS02" in result.piktogramlar
    assert "GHS07" in result.piktogramlar
    assert result.uyari_kelimesi == "Tehlike"
    assert len(result.p_ifadeleri) > 0
    assert len(result.calculation_steps) > 5


def test_regulatory_parser_rich_string():
    """Zengin sınıflandırma metninden SCL, M-Factor, Class ve Category doğru ayrıştırılmalıdır."""
    from app.services.regulatory_engine.parser import RegulatoryClassificationParser
    text = "Skin Corr. 1B H314 (SCL >= 1%), Eye Dam. 1 H318 (SCL >= 3%), Aquatic Chronic 1 H410 (M=10)"
    entries = RegulatoryClassificationParser.parse_classification_string(text)

    assert len(entries) == 3
    # Skin Corr 1B
    e1 = next(e for e in entries if e.h_code == "H314")
    assert e1.hazard_class == "Skin Corr."
    assert e1.category == "1B"
    assert e1.scl == 1.0

    # Eye Dam 1
    e2 = next(e for e in entries if e.h_code == "H318")
    assert e2.hazard_class == "Eye Dam."
    assert e2.scl == 3.0

    # Aquatic Chronic 1
    e3 = next(e for e in entries if e.h_code == "H410")
    assert e3.m_factor_chronic == 10.0


def test_scl_skin_corrosion_trigger():
    """Normalde %5 gereken Skin Corr 1B, SCL=%1 olan maddede %2 konsantrasyonda tetiklenmelidir."""
    from app.services.classification_engine import ClassificationEngine
    components = [
        {
            "ad": "Özel Aşındırıcı Asit",
            "konsantrasyon": "%2",
            "siniflandirma": "Skin Corr. 1B H314 (SCL >= 1%)"
        }
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H314" in res["h_ifadeleri"]
    assert "GHS05" in res["piktogramlar"]
    assert any("Kategori 1B" in s["kategori"] for s in res["siniflandirmalar"])
    assert any("SCL (%1.0)" in step for step in res["calculation_steps"])


def test_data_status_insufficient_for_flammable():
    """Parlama noktası verisi yokken FlammableLiquidRule data_status == 'INSUFFICIENT_DATA' vermelidir."""
    from app.services.classification_engine import ClassificationEngine
    components = [
        {"ad": "Aseton", "konsantrasyon": "%50", "siniflandirma": "Flam. Liq. 2 H225"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components, parlama_noktasi=None)
    assert "H225" not in res["h_ifadeleri"]
    assert "data_status_summary" in res
    assert res["data_status_summary"]["FlammableLiquidRule"] == "INSUFFICIENT_DATA"


def test_concentration_range_three_valued_logic():
    """
    REG-001: Konsantrasyon aralıklarında 3 durumlu mantık doğrulaması:
    1. min < threshold <= max -> INDETERMINATE (Belirsiz / Aralık Eşiği)
    2. min >= threshold -> DEFINITELY_TRUE (Kesin)
    3. max < threshold -> DEFINITELY_FALSE (Sınıflandırılmadı)
    """
    from app.services.classification_engine import ClassificationEngine

    # Durum 1: 10 - 25% vs SCL = 20% -> INDETERMINATE
    components_indeterminate = [
        {
            "ad": "Madde X",
            "konsantrasyon": "10 - 25%",
            "siniflandirma": "Skin Corr. 1B H314 (SCL >= 20%)"
        }
    ]
    res1 = ClassificationEngine.calculate_mixture_hazards(components_indeterminate)
    assert res1["has_indeterminate"] is True
    assert len(res1["indeterminate_hazards"]) == 1
    assert res1["siniflandirmalar"][0]["status"] == "INDETERMINATE"
    assert res1["siniflandirmalar"][0]["status_label"] == "Belirsiz (Aralık Eşiği)"
    assert "H314" in res1["h_ifadeleri"]

    # Durum 2: 22 - 25% vs SCL = 20% -> DEFINITELY_TRUE
    components_true = [
        {
            "ad": "Madde X",
            "konsantrasyon": "22 - 25%",
            "siniflandirma": "Skin Corr. 1B H314 (SCL >= 20%)"
        }
    ]
    res2 = ClassificationEngine.calculate_mixture_hazards(components_true)
    assert res2["has_indeterminate"] is False
    assert len(res2["indeterminate_hazards"]) == 0
    assert res2["siniflandirmalar"][0]["status"] == "DEFINITELY_TRUE"
    assert res2["siniflandirmalar"][0]["status_label"] == "Kesin"
    assert "H314" in res2["h_ifadeleri"]

    # Durum 3: 5 - 15% vs SCL = 20% -> DEFINITELY_FALSE (Hiç sınıflandırılmaz)
    components_false = [
        {
            "ad": "Madde X",
            "konsantrasyon": "5 - 15%",
            "siniflandirma": "Skin Corr. 1B H314 (SCL >= 20%)"
        }
    ]
    res3 = ClassificationEngine.calculate_mixture_hazards(components_false)
    assert res3["has_indeterminate"] is False
    assert "H314" not in res3["h_ifadeleri"]
    assert len(res3["siniflandirmalar"]) == 0


def test_reg002_aspiration_hazard_three_cases():
    """
    REG-002: Aspirasyon toksisitesi için doğru kural modeli:
    1. >=10% + viscosity <= 20.5 mm²/s -> H304 (Kat 1)
    2. >=10% + viscosity > 20.5 mm²/s -> H304 yok (Sınıflandırılmaz)
    3. >=10% + viscosity UNKNOWN (None) -> INSUFFICIENT_DATA (H304 verilmez)
    """
    from app.services.classification_engine import ClassificationEngine

    components = [
        {
            "ad": "Hidrokarbon Solvent",
            "konsantrasyon": "%12",
            "siniflandirma": "Asp. Tox. 1 H304"
        }
    ]

    # Durum 1: >=10% ve viskozite <= 20.5 -> H304
    res_low = ClassificationEngine.calculate_mixture_hazards(components, kinematik_viskozite=15.0)
    assert "H304" in res_low["h_ifadeleri"]
    assert "GHS08" in res_low["piktogramlar"]
    assert res_low["data_status_summary"]["AspirationHazardRule"] == "SUFFICIENT"
    assert any("Aspirasyon Zararı" in s["zararlilik_sinifi"] for s in res_low["siniflandirmalar"])

    # Durum 2: >=10% ve viskozite > 20.5 -> H304 yok
    res_high = ClassificationEngine.calculate_mixture_hazards(components, kinematik_viskozite=25.0)
    assert "H304" not in res_high["h_ifadeleri"]
    assert not any("Aspirasyon Zararı" in s["zararlilik_sinifi"] for s in res_high["siniflandirmalar"])
    assert res_high["data_status_summary"]["AspirationHazardRule"] == "SUFFICIENT"

    # Durum 3: >=10% ve viskozite bilinmiyor (None) -> INSUFFICIENT_DATA ve H304 YOK
    res_unknown = ClassificationEngine.calculate_mixture_hazards(components, kinematik_viskozite=None)
    assert "H304" not in res_unknown["h_ifadeleri"]
    assert not any("Aspirasyon Zararı" in s["zararlilik_sinifi"] for s in res_unknown["siniflandirmalar"])
    assert res_unknown["data_status_summary"]["AspirationHazardRule"] == "INSUFFICIENT_DATA"
    assert any("INSUFFICIENT_DATA" in step for step in res_unknown["calculation_steps"])


def test_reg003_flammable_liquid_boiling_point_requirement():
    """
    REG-003: Parlama noktası < 23°C olduğunda kaynama noktası gereksinimi:
    1. FP < 23°C ve BP <= 35°C -> Cat 1 (H224)
    2. FP < 23°C ve BP > 35°C -> Cat 2 (H225)
    3. FP < 23°C ve BP UNKNOWN (None) -> INSUFFICIENT_DATA (H224/H225 verilmez)
    """
    from app.services.classification_engine import ClassificationEngine

    components = [
        {"ad": "Uçucu Çözücü", "konsantrasyon": "%50", "siniflandirma": "Flam. Liq. 2 H225"}
    ]

    # Durum 1: FP < 23 ve BP <= 35 -> H224 (Kat 1)
    res_cat1 = ClassificationEngine.calculate_mixture_hazards(components, parlama_noktasi=15.0, kaynama_noktasi=30.0)
    assert "H224" in res_cat1["h_ifadeleri"]
    assert "GHS02" in res_cat1["piktogramlar"]
    assert res_cat1["data_status_summary"]["FlammableLiquidRule"] == "SUFFICIENT"
    assert any("Kategori 1" in s["kategori"] for s in res_cat1["siniflandirmalar"])

    # Durum 2: FP < 23 ve BP > 35 -> H225 (Kat 2)
    res_cat2 = ClassificationEngine.calculate_mixture_hazards(components, parlama_noktasi=15.0, kaynama_noktasi=56.0)
    assert "H225" in res_cat2["h_ifadeleri"]
    assert "GHS02" in res_cat2["piktogramlar"]
    assert res_cat2["data_status_summary"]["FlammableLiquidRule"] == "SUFFICIENT"
    assert any("Kategori 2" in s["kategori"] for s in res_cat2["siniflandirmalar"])

    # Durum 3: FP < 23 ve BP Bilinmiyor (None) -> INSUFFICIENT_DATA ve H224/H225 atanmaz
    res_unknown = ClassificationEngine.calculate_mixture_hazards(components, parlama_noktasi=15.0, kaynama_noktasi=None)
    assert "H224" not in res_unknown["h_ifadeleri"]
    assert "H225" not in res_unknown["h_ifadeleri"]
    assert not any("Alevlenir Sıvılar" in s["zararlilik_sinifi"] for s in res_unknown["siniflandirmalar"])
    assert res_unknown["data_status_summary"]["FlammableLiquidRule"] == "INSUFFICIENT_DATA"
    assert any("INSUFFICIENT_DATA" in step for step in res_unknown["calculation_steps"])


def test_reg004_euh066_explicit_requirement():
    """
    REG-004: EUH066 değerlendirmesi:
    1. Yalnızca H304 veya H336 taşıyan maddeler (sezgisel solvent varsayımı) EUH066 tetiklemez.
    2. Açıkça EUH066 taşıyan maddeler EUH066 tetikler.
    3. Cilt Aşınması / Tahrişi olan karışımlarda EUH066 CLP Ek-2 uyarınca bastırılır.
    """
    from app.services.classification_engine import ClassificationEngine

    # Durum 1: %20 H304 maddesi (EUH066 içermiyor) -> EUH066 tetiklenmemelidir
    comp_asp = [
        {"ad": "Mineral Yağ", "konsantrasyon": "%20", "siniflandirma": "Asp. Tox. 1 H304"}
    ]
    res1 = ClassificationEngine.calculate_mixture_hazards(comp_asp, kinematik_viskozite=10.0)
    assert "EUH066" not in res1["euh_ifadeleri"]

    # Durum 2: %20 H336 maddesi (EUH066 içermiyor) -> EUH066 tetiklenmemelidir
    comp_stot = [
        {"ad": "Solvent Y", "konsantrasyon": "%20", "siniflandirma": "STOT SE 3 H336"}
    ]
    res2 = ClassificationEngine.calculate_mixture_hazards(comp_stot)
    assert "EUH066" not in res2["euh_ifadeleri"]

    # Durum 3: Açıkça EUH066 içeren madde -> EUH066 tetiklenmelidir
    comp_explicit = [
        {"ad": "Etil Asetat", "konsantrasyon": "%20", "siniflandirma": "Flam. Liq. 2 H225, Eye Irrit. 2 H319, STOT SE 3 H336, EUH066"}
    ]
    res3 = ClassificationEngine.calculate_mixture_hazards(comp_explicit, parlama_noktasi=-4.0, kaynama_noktasi=77.0)
    assert "EUH066" in res3["euh_ifadeleri"]

    # Durum 4: Açıkça EUH066 var ancak karışım Skin Corr 1B -> EUH066 bastırılır
    comp_suppressed = [
        {"ad": "Etil Asetat", "konsantrasyon": "%20", "siniflandirma": "Flam. Liq. 2 H225, Eye Irrit. 2 H319, EUH066"},
        {"ad": "Aşındırıcı Asit", "konsantrasyon": "%10", "siniflandirma": "Skin Corr. 1B H314"}
    ]
    res4 = ClassificationEngine.calculate_mixture_hazards(comp_suppressed, parlama_noktasi=-4.0, kaynama_noktasi=77.0)
    assert "H314" in res4["h_ifadeleri"]
    assert "EUH066" not in res4["euh_ifadeleri"]





