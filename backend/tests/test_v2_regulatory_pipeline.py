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

