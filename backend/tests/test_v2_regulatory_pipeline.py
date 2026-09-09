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
    assert res_unknown["data_status_summary"]["AspirationHazardRule"] in ["INSUFFICIENT_DATA", "INDETERMINATE"]
    assert any("INDETERMINATE" in step or "INSUFFICIENT_DATA" in step for step in res_unknown["calculation_steps"])


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


def test_reg005_euh204_decoupled_from_h334_threshold():
    """
    REG-005: EUH204 ve H334 ayrık karar yolları:
    1. İzosiyanat var ama H334 yok (prepolimer/H317) -> EUH204 tetiklenir, H334 tetiklenmez.
    2. İzosiyanat var ve H334 >= %0.2 -> Hem H334 hem EUH204 tetiklenir.
    3. İzosiyanat yok ve H334 >= %0.2 -> H334 tetiklenir, EUH204 tetiklenmez.
    4. İzosiyanat var ve %0.1 <= H334 < %0.2 -> EUH204 tetiklenir, H334 tetiklenmez.
    5. İzosiyanat yok ve %0.1 <= H334 < %0.2 -> EUH208 tetiklenir, EUH204 ve H334 tetiklenmez.
    """
    from app.services.classification_engine import ClassificationEngine

    # Senaryo 1: İzosiyanat var ama H334 yok (HDI prepolimer, H317 + H332)
    comp_iso_no_h334 = [
        {"ad": "Alifatik Poliizosiyanat HDI Reçine", "konsantrasyon": "%5", "siniflandirma": "Skin Sens. 1 H317, Acute Tox. 4 H332"}
    ]
    res1 = ClassificationEngine.calculate_mixture_hazards(comp_iso_no_h334)
    assert "EUH204" in res1["euh_ifadeleri"]
    assert "H334" not in res1["h_ifadeleri"]
    assert "H317" in res1["h_ifadeleri"]

    # Senaryo 2: İzosiyanat var ve H334 >= 0.2% (%2.0 MDI) -> Hem H334 hem EUH204
    comp_iso_high_h334 = [
        {"ad": "Polimerik MDI İzosiyanat", "konsantrasyon": "%2.0", "siniflandirma": "Resp. Sens. 1 H334, Carc. 2 H351"}
    ]
    res2 = ClassificationEngine.calculate_mixture_hazards(comp_iso_high_h334)
    assert "H334" in res2["h_ifadeleri"]
    assert "EUH204" in res2["euh_ifadeleri"]

    # Senaryo 3: İzosiyanat yok ve H334 >= 0.2% (%0.5 Enzim) -> H334 var, EUH204 yok
    comp_no_iso_high_h334 = [
        {"ad": "Proteaz Enzimi", "konsantrasyon": "%0.5", "siniflandirma": "Resp. Sens. 1 H334"}
    ]
    res3 = ClassificationEngine.calculate_mixture_hazards(comp_no_iso_high_h334)
    assert "H334" in res3["h_ifadeleri"]
    assert "EUH204" not in res3["euh_ifadeleri"]

    # Senaryo 4: İzosiyanat var ve %0.15 H334 -> EUH204 var, H334 yok
    comp_iso_sub_threshold = [
        {"ad": "MDI Monomer", "konsantrasyon": "%0.15", "siniflandirma": "Resp. Sens. 1 H334"}
    ]
    res4 = ClassificationEngine.calculate_mixture_hazards(comp_iso_sub_threshold)
    assert "EUH204" in res4["euh_ifadeleri"]
    assert "H334" not in res4["h_ifadeleri"]

    # Senaryo 5: İzosiyanat yok ve %0.15 H334 -> EUH208 var, EUH204 yok, H334 yok
    comp_no_iso_sub_threshold = [
        {"ad": "Glutaraldehit Çözeltisi", "konsantrasyon": "%0.15", "siniflandirma": "Resp. Sens. 1 H334"}
    ]
    res5 = ClassificationEngine.calculate_mixture_hazards(comp_no_iso_sub_threshold)
    assert "H334" not in res5["h_ifadeleri"]
    assert "EUH204" not in res5["euh_ifadeleri"]
    assert "EUH208" in res5["euh_ifadeleri"]


def test_reg007_targeted_scl_architecture():
    """
    REG-007: Hedefli SCL Mimarisinin Doğrulaması.
    Bir bileşende birden fazla zararlılık varken (örn: Skin Corr. 1B H314 SCL=2%, Eye Dam. 1 H318 SCL=5%):
    1. Sınıflandırma dizesindeki veya 'scl_entries' içindeki SCL değerleri yalnızca ilgili zararlılık sınıfına atanmalıdır.
    2. %3.0 konsantrasyonda Skin Corr 1B tetiklenmeli (3% >= 2%), Eye Dam 1 ise SCL'ye (%5) ulaşmadığı için SCL üzerinden tetiklenmemelidir.
    """
    from app.models.regulatory import SpecificConcentrationLimit
    from app.services.regulatory_engine.pipeline import RegulatoryPipeline
    from app.services.classification_engine import ClassificationEngine

    # 1. Zengin metin ayrıştırma testi
    text = "Skin Corr. 1B H314 (SCL >= 2%), Eye Dam. 1 H318 (SCL >= 5%)"
    comps = [{"ad": "Asit Karışımı", "konsantrasyon": "%3", "siniflandirma": text}]
    substances = RegulatoryPipeline.adapt_raw_components(comps)
    assert len(substances) == 1
    sub = substances[0]

    h_skin = next(h for h in sub.hazards if h.h_code == "H314")
    h_eye = next(h for h in sub.hazards if h.h_code == "H318")
    assert h_skin.scl == 2.0
    assert h_eye.scl == 5.0

    # Model yardımcı metodları
    scl_dict = h_skin.to_scl_dict()
    assert scl_dict == {
        "hazard_class": "Skin Corr.",
        "category": "1B",
        "h_code": "H314",
        "scl": 2.0
    }
    scl_entry = h_skin.to_scl_entry()
    assert isinstance(scl_entry, SpecificConcentrationLimit)
    assert scl_entry.scl == 2.0
    assert len(sub.structured_scls) == 2

    # 2. Dışarıdan yapılandırılmış 'scl_entries' ile besleme testi
    comps_structured = [
        {
            "ad": "Özel Bileşik",
            "konsantrasyon": "%3",
            "siniflandirma": "Skin Corr. 1B H314, Eye Dam. 1 H318",
            "scl_entries": [
                {"hazard_class": "Skin Corr.", "category": "1B", "h_code": "H314", "scl": 2.0},
                {"hazard_class": "Eye Dam.", "category": "1", "h_code": "H318", "scl": 5.0}
            ]
        }
    ]
    substances_struct = RegulatoryPipeline.adapt_raw_components(comps_structured)
    sub2 = substances_struct[0]
    h_skin2 = next(h for h in sub2.hazards if h.h_code == "H314")
    h_eye2 = next(h for h in sub2.hazards if h.h_code == "H318")
    assert h_skin2.scl == 2.0
    assert h_eye2.scl == 5.0

    # 3. Kural motoru değerlendirmesi:
    # Konsantrasyon = %3.0 -> Skin Corr 1B tetiklenmeli (3 >= 2), Eye Dam 1 SCL'si (%5) aşılmamalı
    res = ClassificationEngine.calculate_mixture_hazards(comps)
    assert "H314" in res["h_ifadeleri"]
    assert any("SCL (%2.0)" in step for step in res["calculation_steps"])
    assert not any("Eye Dam" in step and "SCL (%2.0)" in step for step in res["calculation_steps"])


def test_reg007_scalar_scl_broadcast_prevention():
    """
    REG-007: Birden fazla zararlılık içeren bileşene dışarıdan genel skaler 'scl' verildiğinde,
    tüm zararlılıklara körlemesine atanması engellenmelidir.
    """
    from app.services.regulatory_engine.pipeline import RegulatoryPipeline

    # Multi-hazard bileşene genel skaler scl=2 verilmesi durumu
    comps = [
        {
            "ad": "Karmaşık Madde",
            "konsantrasyon": "%3",
            "siniflandirma": "Skin Corr. 1B H314, Eye Dam. 1 H318",
            "scl": 2.0  # Hedefsiz, genel skaler
        }
    ]
    substances = RegulatoryPipeline.adapt_raw_components(comps)
    sub = substances[0]
    h_skin = next(h for h in sub.hazards if h.h_code == "H314")
    h_eye = next(h for h in sub.hazards if h.h_code == "H318")

    # Genel skaler 2.0, hangi sınıfa ait olduğu belirsiz olduğu için körlemesine atanmaz!
    assert h_skin.scl is None
    assert h_eye.scl is None

    # Tekil zararlılığı olan bileşende ise geriye dönük uyumluluk korunur
    comp_single = [
        {
            "ad": "Tekil Aşındırıcı",
            "konsantrasyon": "%2",
            "siniflandirma": "Skin Corr. 1B H314",
            "scl": 1.5  # Tekil hedef olduğundan belirsizlik yok
        }
    ]
    sub_single = RegulatoryPipeline.adapt_raw_components(comp_single)[0]
    assert sub_single.hazards[0].scl == 1.5


def test_reg008_cmr_category_unresolved():
    """
    REG-008: CMR'de H-code -> kategori dönüşümü doğrulaması.
    H340, H350, H360 kodları 1A/1B ayrımını kendi başlarına taşımazlar.
    1. Sadece 'H350' geldiğinde parser varsayılan 1B üretmemeli, 'CATEGORY_UNRESOLVED' üretmelidir.
    2. %0.2 konsantrasyonda 'H350' içeren karışım 'Kategori 1B' değil, 'CATEGORY_UNRESOLVED' olarak sınıflandırılmalıdır.
    3. Açıkça 'Carc. 1A H350' verilmişse 'Kategori 1A', 'Carc. 1B H350' verilmişse 'Kategori 1B' olmalıdır.
    4. Mutajenite (H340) ve Üreme Toksisitesi (H360) için de aynı kategori çözümsüzlük tespiti yapılmalıdır.
    """
    from app.services.regulatory_engine.parser import RegulatoryClassificationParser
    from app.services.classification_engine import ClassificationEngine

    # 1. Parser düzeyinde doğrulama
    # Yalın H350
    p_h350 = RegulatoryClassificationParser.parse_classification_string("H350")
    assert len(p_h350) == 1
    assert p_h350[0].hazard_class == "Carc."
    assert p_h350[0].category == "CATEGORY_UNRESOLVED"

    # Yalın H340
    p_h340 = RegulatoryClassificationParser.parse_classification_string("H340")
    assert len(p_h340) == 1
    assert p_h340[0].hazard_class == "Muta."
    assert p_h340[0].category == "CATEGORY_UNRESOLVED"

    # Yalın H360D
    p_h360 = RegulatoryClassificationParser.parse_classification_string("H360D")
    assert len(p_h360) == 1
    assert p_h360[0].hazard_class == "Repr."
    assert p_h360[0].category == "CATEGORY_UNRESOLVED"

    # Açıkça 1A veya 1B belirtilmişse
    p_carc_1a = RegulatoryClassificationParser.parse_classification_string("Carc. 1A H350")
    assert p_carc_1a[0].category == "1A"
    p_carc_1b = RegulatoryClassificationParser.parse_classification_string("Carc. 1B H350")
    assert p_carc_1b[0].category == "1B"

    # 2. Sınıflandırma motoru düzeyinde doğrulama:
    # A. Yalın H350 (%0.2) -> CATEGORY_UNRESOLVED
    res_unresolved = ClassificationEngine.calculate_mixture_hazards([
        {"ad": "Belirsiz Kanserojen Madde", "konsantrasyon": "%0.2", "siniflandirma": "H350"}
    ])
    assert "H350" in res_unresolved["h_ifadeleri"]
    assert "GHS08" in res_unresolved["piktogramlar"]
    assert res_unresolved["uyari_kelimesi"] == "Tehlike"
    assert any(
        s["zararlilik_sinifi"] == "Kanserojenite" and s["kategori"] == "CATEGORY_UNRESOLVED"
        for s in res_unresolved["siniflandirmalar"]
    )
    assert any("CATEGORY_UNRESOLVED" in step for step in res_unresolved["calculation_steps"])

    # B. Açıkça Carc. 1A H350 (%0.2) -> Kategori 1A
    res_1a = ClassificationEngine.calculate_mixture_hazards([
        {"ad": "Kanserojen Madde 1A", "konsantrasyon": "%0.2", "siniflandirma": "Carc. 1A H350"}
    ])
    assert any(
        s["zararlilik_sinifi"] == "Kanserojenite" and s["kategori"] == "Kategori 1A"
        for s in res_1a["siniflandirmalar"]
    )

    # C. Açıkça Carc. 1B H350 (%0.2) -> Kategori 1B
    res_1b = ClassificationEngine.calculate_mixture_hazards([
        {"ad": "Kanserojen Madde 1B", "konsantrasyon": "%0.2", "siniflandirma": "Carc. 1B H350"}
    ])
    assert any(
        s["zararlilik_sinifi"] == "Kanserojenite" and s["kategori"] == "Kategori 1B"
        for s in res_1b["siniflandirmalar"]
    )

    # D. Yalın H340 (%0.2) -> CATEGORY_UNRESOLVED
    res_muta = ClassificationEngine.calculate_mixture_hazards([
        {"ad": "Belirsiz Mutajen Madde", "konsantrasyon": "%0.2", "siniflandirma": "H340"}
    ])
    assert any(
        s["zararlilik_sinifi"] == "Eşey Hücre Mutajenitesi" and s["kategori"] == "CATEGORY_UNRESOLVED"
        for s in res_muta["siniflandirmalar"]
    )

    # E. Yalın H360 (%0.5) -> CATEGORY_UNRESOLVED
    res_repr = ClassificationEngine.calculate_mixture_hazards([
        {"ad": "Belirsiz Üreme Toksik Madde", "konsantrasyon": "%0.5", "siniflandirma": "H360D"}
    ])
    assert any(
        s["zararlilik_sinifi"] == "Üreme Sistemi Toksisitesi" and s["kategori"] == "CATEGORY_UNRESOLVED"
        for s in res_repr["siniflandirmalar"]
    )


def test_reg009_aquatic_m_factor_audit_trail():
    """
    REG-009: AquaticRule M-faktörü denetim izi (audit trail) doğrulaması.
    'M = 1' (açıkça 1 belirtilmiş) ile 'M bilgisi yok' (varsayılan 1) ayrılmalıdır:
    1. M bilgisi yoksa: value=None, effective_value=1.0, source='DEFAULT'
    2. M açıkça 1 ise: value=1.0, effective_value=1.0, source='EXPLICIT'
    3. M açıkça 10 ise: value=10.0, effective_value=10.0, source='EXPLICIT'
    4. Denetim izinde (calculation_notes) bu ayrım şeffaf şekilde belgelenmelidir.
    """
    from app.models.regulatory import MFactor
    from app.services.regulatory_engine.pipeline import RegulatoryPipeline
    from app.services.classification_engine import ClassificationEngine

    # 1. Model düzeyinde MFactor testi
    m_default = MFactor.create(None)
    assert m_default.value is None
    assert m_default.effective_value == 1.0
    assert m_default.source == "DEFAULT"

    m_explicit_1 = MFactor.create(1.0)
    assert m_explicit_1.value == 1.0
    assert m_explicit_1.effective_value == 1.0
    assert m_explicit_1.source == "EXPLICIT"

    m_explicit_10 = MFactor.create(10.0)
    assert m_explicit_10.value == 10.0
    assert m_explicit_10.effective_value == 10.0
    assert m_explicit_10.source == "EXPLICIT"

    # 2. Pipeline adapt_raw_components ayrıştırma testi:
    # A. M-faktörü belirtilmemiş bileşen
    comp_no_m = [{"ad": "M Bilinmeyen Madde", "konsantrasyon": "%10", "siniflandirma": "Aquatic Acute 1 H400"}]
    sub_no_m = RegulatoryPipeline.adapt_raw_components(comp_no_m)[0]
    assert sub_no_m.m_acute.value is None
    assert sub_no_m.m_acute.effective_value == 1.0
    assert sub_no_m.m_acute.source == "DEFAULT"

    res_no_m = ClassificationEngine.calculate_mixture_hazards(comp_no_m)
    assert any("value=null, effective_value=1.0, source='DEFAULT'" in step for step in res_no_m["calculation_steps"])

    # B. M-faktörü açıkça M=1 belirtilmiş bileşen
    comp_m_1 = [{"ad": "M=1 Açık Madde", "konsantrasyon": "%10", "siniflandirma": "Aquatic Acute 1 H400 (M=1)"}]
    sub_m_1 = RegulatoryPipeline.adapt_raw_components(comp_m_1)[0]
    assert sub_m_1.m_acute.value == 1.0
    assert sub_m_1.m_acute.effective_value == 1.0
    assert sub_m_1.m_acute.source == "EXPLICIT"

    res_m_1 = ClassificationEngine.calculate_mixture_hazards(comp_m_1)
    assert any("value=1, effective_value=1, source='EXPLICIT'" in step for step in res_m_1["calculation_steps"])

    # C. M-faktörü açıkça M=10 belirtilmiş bileşen (%3 * 10 = %30 >= %25 -> H400 tetiklenir)
    comp_m_10 = [{"ad": "Yüksek Zehirli Sucul Madde", "konsantrasyon": "%3", "siniflandirma": "Aquatic Acute 1 H400 (M=10)"}]
    sub_m_10 = RegulatoryPipeline.adapt_raw_components(comp_m_10)[0]
    assert sub_m_10.m_acute.value == 10.0
    assert sub_m_10.m_acute.effective_value == 10.0
    assert sub_m_10.m_acute.source == "EXPLICIT"

    res_m_10 = ClassificationEngine.calculate_mixture_hazards(comp_m_10)
    assert "H400" in res_m_10["h_ifadeleri"]
    assert any("value=10, effective_value=10, source='EXPLICIT'" in step for step in res_m_10["calculation_steps"])


def test_reg010_skin_eye_cut_off_and_threshold_abstraction():
    """
    REG-010: Cilt ve Göz kurallarında Relevant Component Cut-off ve
    Eşik Abstraction Modeli (HazardThreshold & RegulatoryThresholdProvider) doğrulaması.
    """
    from app.models.regulatory import HazardThreshold
    from app.services.regulatory_engine.thresholds import RegulatoryThresholdProvider
    from app.services.classification_engine import ClassificationEngine

    # 1. HazardThreshold Modeli & Eşik Hiyerarşisi Birim Testleri:
    # A. Standart cut-off (1.0%), GCL (10.0%), SCL yok
    t_default = HazardThreshold(hazard_class="Skin Irrit.", category="2", h_code="H315", cut_off=1.0, gcl=10.0)
    assert t_default.effective_cutoff == 1.0
    assert t_default.effective_limit == 10.0
    assert not t_default.is_relevant(0.8)
    assert t_default.is_relevant(1.0)
    assert not t_default.triggers_classification(9.9)
    assert t_default.triggers_classification(10.0)

    # B. SCL > cut-off (örn. SCL = 15.0%)
    t_high_scl = HazardThreshold(hazard_class="Skin Irrit.", category="2", h_code="H315", cut_off=1.0, gcl=10.0, scl=15.0)
    assert t_high_scl.effective_cutoff == 1.0
    assert t_high_scl.effective_limit == 15.0
    assert not t_high_scl.is_relevant(0.9)
    assert t_high_scl.is_relevant(1.0)
    assert not t_high_scl.triggers_classification(14.9)
    assert t_high_scl.triggers_classification(15.0)

    # C. SCL < cut-off (örn. CLP Madde 11(3) uyarınca SCL = 0.5% -> effective_cutoff SCL'e düşer)
    t_low_scl = HazardThreshold(hazard_class="Skin Irrit.", category="2", h_code="H315", cut_off=1.0, gcl=10.0, scl=0.5)
    assert t_low_scl.effective_cutoff == 0.5
    assert t_low_scl.effective_limit == 0.5
    assert not t_low_scl.is_relevant(0.4)
    assert t_low_scl.is_relevant(0.5)
    assert not t_low_scl.triggers_classification(0.4)
    assert t_low_scl.triggers_classification(0.5)

    # 2. RegulatoryThresholdProvider Fabrika Testleri:
    t_corr = RegulatoryThresholdProvider.get_skin_corr_threshold(category="1B")
    assert t_corr.hazard_class == "Skin Corr."
    assert t_corr.category == "1B"
    assert t_corr.cut_off == 1.0
    assert t_corr.gcl == 5.0

    t_irrit = RegulatoryThresholdProvider.get_skin_irrit_threshold()
    assert t_irrit.cut_off == 1.0
    assert t_irrit.gcl == 10.0

    t_eye = RegulatoryThresholdProvider.get_eye_dam_threshold()
    assert t_eye.cut_off == 1.0
    assert t_eye.gcl == 3.0

    t_code = RegulatoryThresholdProvider.get_threshold_by_code("H318")
    assert t_code.h_code == "H318"
    assert t_code.gcl == 3.0

    # 3. Kural Motoru Toplanabilirlik & Cut-off Denetimi:
    # A. Eşik altı birikimli safsızlıkların elenmesi (Accumulated sub-cutoff impurities excluded):
    # 15 farklı bileşen, her biri %0.8 H315 (toplam = %12.0 >= %10.0)
    # Saf toplanabilirlikte %12 >= %10 H315 verirdi; cut-off (%1.0) ile her biri elenmeli!
    sub_threshold_mixture = [
        {"ad": f"Safsızlık {i}", "konsantrasyon": "%0.8", "siniflandirma": "Skin Irrit. 2 H315"}
        for i in range(15)
    ]
    res_sub = ClassificationEngine.calculate_mixture_hazards(sub_threshold_mixture)
    assert "H315" not in res_sub["h_ifadeleri"]
    assert any("Kesme Sınırı (Cut-off)" in step for step in res_sub["calculation_steps"])
    assert any("Safsızlık 0" in step and "toplanabilirlik havuzuna dahil edilmedi" in step for step in res_sub["calculation_steps"])

    # B. Cut-off üzerindeki ilgili bileşenlerin toplanması:
    # 2 bileşen, her biri %6.0 H315 (toplam = %12.0 >= %10.0). Her ikisi de %6 >= %1 cut-off.
    relevant_mixture = [
        {"ad": "Bileşen A", "konsantrasyon": "%6.0", "siniflandirma": "Skin Irrit. 2 H315"},
        {"ad": "Bileşen B", "konsantrasyon": "%6.0", "siniflandirma": "Skin Irrit. 2 H315"},
    ]
    res_rel = ClassificationEngine.calculate_mixture_hazards(relevant_mixture)
    assert "H315" in res_rel["h_ifadeleri"]

    # C. Düşük SCL ile Kesme Sınırının Otomatik Düşmesi (SCL = 0.5% < cut-off 1.0%):
    # Konsantrasyon %0.6 -> effective_cutoff (%0.5) üzerinde ve SCL (%0.5) üzerinde -> H315 tetiklenir
    comp_low_scl_active = [{
        "ad": "Hassas Tahriş Edici",
        "konsantrasyon": "%0.6",
        "siniflandirma": "Skin Irrit. 2 H315",
        "structured_scls": [{"hazard_class": "Skin Irrit.", "category": "2", "h_code": "H315", "scl": 0.5}]
    }]
    res_low_active = ClassificationEngine.calculate_mixture_hazards(comp_low_scl_active)
    assert "H315" in res_low_active["h_ifadeleri"]

    # Konsantrasyon %0.3 -> effective_cutoff (%0.5) altında -> Elenir, H315 tetiklenmez
    comp_low_scl_inactive = [{
        "ad": "Hassas Tahriş Edici",
        "konsantrasyon": "%0.3",
        "siniflandirma": "Skin Irrit. 2 H315",
        "structured_scls": [{"hazard_class": "Skin Irrit.", "category": "2", "h_code": "H315", "scl": 0.5}]
    }]
    res_low_inactive = ClassificationEngine.calculate_mixture_hazards(comp_low_scl_inactive)
    assert "H315" not in res_low_inactive["h_ifadeleri"]
    assert any("cut-off eşiğinin (%0.5) altında" in step for step in res_low_inactive["calculation_steps"])

    # D. Göz Hasarı (Eye Dam 1) eşik altı safsızlık denetimi:
    # 4 bileşen, her biri %0.8 H318 (toplam = %3.2 >= %3.0 GCL).
    # Her biri %0.8 < %1.0 cut-off olduğundan hiçbiri toplanmamalı ve H318 çıkmamalı.
    eye_sub_mixture = [
        {"ad": f"Göz Safsızlığı {i}", "konsantrasyon": "%0.8", "siniflandirma": "Eye Dam. 1 H318"}
        for i in range(4)
    ]
    res_eye = ClassificationEngine.calculate_mixture_hazards(eye_sub_mixture)
    assert "H318" not in res_eye["h_ifadeleri"]
    assert "H319" not in res_eye["h_ifadeleri"]
    assert any("Ciddi Göz Hasarı için ilgili cut-off eşiğinin (%1.0) altında" in step for step in res_eye["calculation_steps"])


def test_reg011_stot_se3_rti_ne_and_cutoff_abstraction():
    """
    REG-011: STOT SE 3 mekanizmalarının ayrıştırılması:
    - Solunum Yolu Tahrişi (RTI - H335) ve Narkotik Etkiler (NE - H336) bağımsız toplanabilirlik
    - İlgili Bileşen Kesme Sınırı (Cut-off %1.0) denetimi
    - Spesifik Konsantrasyon Sınırı (SCL) desteği
    - Uygulanabilirlik (Applicability) denetimi
    - STOT RE 2 GCL %10.0 kontrolü
    """
    from app.models.regulatory import STOTSE3Effect, HazardThreshold, StructuredSubstance, ConcentrationValue, HazardEntry, CalculationContext
    from app.services.regulatory_engine.thresholds import RegulatoryThresholdProvider
    from app.services.classification_engine import ClassificationEngine
    from app.services.rules.stot_rule import STOTRule

    # 1. RegulatoryThresholdProvider STOT eşik testleri
    t_rti = RegulatoryThresholdProvider.get_stot_se_threshold("3", effect_type="respiratory_tract_irritation")
    assert t_rti.h_code == "H335"
    assert t_rti.cut_off == 1.0
    assert t_rti.gcl == 20.0

    t_ne = RegulatoryThresholdProvider.get_stot_se_threshold("3", effect_type="narcotic_effects")
    assert t_ne.h_code == "H336"
    assert t_ne.cut_off == 1.0
    assert t_ne.gcl == 20.0

    t_re2 = RegulatoryThresholdProvider.get_stot_re_threshold("2")
    assert t_re2.h_code == "H373"
    assert t_re2.gcl == 10.0

    # 2. STOT SE 3 Kesme Sınırı (Cut-off) Denetimi:
    # 25 adet safsızlık bileşeni, her biri %0.8 H336 (toplam = %20.0 >= %20.0 GCL).
    # Her biri %0.8 < %1.0 cut-off olduğundan toplanmamalı ve H336 tetiklenmemelidir!
    sub_cutoff_ne = [
        {"ad": f"Solvent Safsızlığı {i}", "konsantrasyon": "%0.8", "siniflandirma": "STOT SE 3 H336"}
        for i in range(25)
    ]
    res_cutoff = ClassificationEngine.calculate_mixture_hazards(sub_cutoff_ne)
    assert "H336" not in res_cutoff["h_ifadeleri"]
    assert any("Narkotik Etkiler - H336" in step and "toplanabilirlik havuzuna dahil edilmedi" in step for step in res_cutoff["calculation_steps"])

    # 3. RTI (H335) ve NE (H336) Birbirinden Bağımsız Toplanabilirlik:
    # %15 H335 + %15 H336 -> Toplam %30 olmasına rağmen iki etki ayrı toplanmalıdır; her ikisi de %15 < %20 olduğundan ne H335 ne de H336 tetiklenmelidir!
    independent_mixture = [
        {"ad": "Tahriş Edici Gaz", "konsantrasyon": "%15", "siniflandirma": "STOT SE 3 H335"},
        {"ad": "Narkotik Solvent", "konsantrasyon": "%15", "siniflandirma": "STOT SE 3 H336"},
    ]
    res_indep = ClassificationEngine.calculate_mixture_hazards(independent_mixture)
    assert "H335" not in res_indep["h_ifadeleri"]
    assert "H336" not in res_indep["h_ifadeleri"]

    # B. Sadece biri eşiği aştığında (%22 H335 + %10 H336):
    mixed_active = [
        {"ad": "Tahriş Edici Gaz", "konsantrasyon": "%22", "siniflandirma": "STOT SE 3 H335"},
        {"ad": "Narkotik Solvent", "konsantrasyon": "%10", "siniflandirma": "STOT SE 3 H336"},
    ]
    res_active = ClassificationEngine.calculate_mixture_hazards(mixed_active)
    assert "H335" in res_active["h_ifadeleri"]
    assert "H336" not in res_active["h_ifadeleri"]

    # 4. STOT SE 3 Spesifik Konsantrasyon Sınırı (SCL) Desteği:
    # H335 için SCL = 5.0% olan bileşen %6 konsantrasyonda (genel sınır %20'nin altında ama SCL üzerinde)
    comp_scl_rti = [{
        "ad": "Yüksek Potensli Solunum Tahriş Edici",
        "konsantrasyon": "%6",
        "siniflandirma": "STOT SE 3 H335",
        "structured_scls": [{"hazard_class": "STOT SE", "category": "3", "h_code": "H335", "scl": 5.0}]
    }]
    res_scl = ClassificationEngine.calculate_mixture_hazards(comp_scl_rti)
    assert "H335" in res_scl["h_ifadeleri"]
    assert any("STOT SE 3 (RTI - SCL)" in step and "%6.0 >= SCL (%5.0)" in step for step in res_scl["calculation_steps"])

    # 5. Uygulanabilirlik (Applicability) Kısıtlaması:
    # Bileşen %25 H335 içeriyor ancak aerosol/solunabilir toz fazında olmadığı için uygulanabilir değil
    sub_non_applicable = StructuredSubstance(
        name="Granül Katı Madde",
        concentration=ConcentrationValue(value=25.0, qualifier="exact"),
        hazards=[
            HazardEntry(
                hazard_class="STOT SE",
                category="3",
                h_code="H335",
                stot_effect=STOTSE3Effect(
                    effect_type="respiratory_tract_irritation",
                    h_code="H335",
                    source="SUPPLIER_SDS",
                    is_applicable=False,
                    applicability_note="Büyük granül form, solunabilir toz oluşmaz"
                )
            )
        ],
        raw_h_codes=["H335"]
    )
    rule_res = STOTRule().evaluate(CalculationContext(), [sub_non_applicable])
    assert not any(h.h_kodu == "H335" for h in rule_res.hazards)
    assert any("uygulanabilirlik koşullarını sağlamadığından hariç tutuldu" in note for note in rule_res.calculation_notes)

    # 6. STOT RE 2 Eşik Düzeltmesi (GCL = %10.0):
    # %5 STOT RE 2 bileşeni (eski hatalı >= %1.0 mantığında yanlışlıkla çıkardı; artık çıkmamalıdır)
    comp_re2_sub = [{"ad": "Organ Zehiri B", "konsantrasyon": "%5", "siniflandirma": "STOT RE 2 H373"}]
    res_re2_sub = ClassificationEngine.calculate_mixture_hazards(comp_re2_sub)
    assert "H373" not in res_re2_sub["h_ifadeleri"]

    # %12 STOT RE 2 bileşeni (>= %10.0 olduğundan tetiklenmelidir)
    comp_re2_active = [{"ad": "Organ Zehiri B", "konsantrasyon": "%12", "siniflandirma": "STOT RE 2 H373"}]
    res_re2_active = ClassificationEngine.calculate_mixture_hazards(comp_re2_active)
    assert "H373" in res_re2_active["h_ifadeleri"]


def test_reg012_acute_toxicity_ate_provenance_audit_trail():
    """
    REG-012: Akut Toksisite ATE Provenance (Menşei / Denetim İzi) Modellemesi:
    - Sayısal ATE, value_source, source_type ve source_reference alanlarının doğrulanması
    - H-kodu dönüşümü (DERIVED, SEA_ANNEX_I, H302_CONVERSION)
    - Doğrudan deneysel veri (EXPERIMENTAL, EXPLICIT_TEST_DATA)
    - Yapılandırılmış ATE nesnesi ile girdi aktarımı
    - Soluma maruziyet formları (toz/sis, buhar, gaz) denetim izi
    """
    from app.models.regulatory import ATEProvenance
    from app.services.regulatory_engine.pipeline import RegulatoryPipeline
    from app.services.classification_engine import ClassificationEngine

    # 1. ATEProvenance model doğrudan doğrulama (Kullanıcı spesifikasyonuna tam uyum):
    prov = ATEProvenance(
        ate=500.0,
        value_source="H302_CONVERSION",
        source_type="DERIVED",
        source_reference="SEA_ANNEX_I",
        route="oral",
        unit="mg/kg"
    )
    dumped = prov.model_dump()
    assert dumped["ate"] == 500.0
    assert dumped["value_source"] == "H302_CONVERSION"
    assert dumped["source_type"] == "DERIVED"
    assert dumped["source_reference"] == "SEA_ANNEX_I"

    # 2. H302 dönüşümünün otomatik olarak provenance üretmesi ve calculation_steps içinde denetim izi:
    # Sayısal ATE verilmemiş, sadece H302 verilmiş bileşen:
    comp_derived = [{"ad": "Toksik Madde X", "konsantrasyon": "%50", "siniflandirma": "Acute Tox. 4 H302"}]
    res_derived = ClassificationEngine.calculate_mixture_hazards(comp_derived)
    assert "H302" in res_derived["h_ifadeleri"]
    assert any(
        "• Akut Toksisite (Oral Katkı): [Toksik Madde X] %50.0, ATE = 500.0 mg/kg (Kaynak: H302_CONVERSION, Tip: DERIVED, Ref: SEA_ANNEX_I)"
        in step for step in res_derived["calculation_steps"]
    )

    # 3. Açıkça girilmiş yapılandırılmış ATE nesnesi (Tedarikçi SDS / Laboratuvar Test Raporu):
    comp_explicit_struct = [{
        "ad": "Özel Kimyasal Y",
        "konsantrasyon": "%50",
        "siniflandirma": "Acute Tox. 4 H302",
        "akut_toksisite_oral": {
            "ate": 350.0,
            "value_source": "SUPPLIER_SDS",
            "source_type": "EXPERIMENTAL",
            "source_reference": "LAB_REPORT_2026_TEST_8"
        }
    }]
    subs = RegulatoryPipeline.adapt_raw_components(comp_explicit_struct)
    sub = subs[0]
    assert sub.ate_oral == 350.0
    assert sub.oral_ate_model.value_source == "SUPPLIER_SDS"
    assert sub.oral_ate_model.source_type == "EXPERIMENTAL"
    assert sub.oral_ate_model.source_reference == "LAB_REPORT_2026_TEST_8"

    res_explicit = ClassificationEngine.calculate_mixture_hazards(comp_explicit_struct)
    assert any(
        "• Akut Toksisite (Oral Katkı): [Özel Kimyasal Y] %50.0, ATE = 350.0 mg/kg (Kaynak: SUPPLIER_SDS, Tip: EXPERIMENTAL, Ref: LAB_REPORT_2026_TEST_8)"
        in step for step in res_explicit["calculation_steps"]
    )

    # 4. Soluma Toz/Sis yolu dönüşüm ve denetim izi:
    comp_dust = [{
        "ad": "İnce Toz Madde",
        "konsantrasyon": "%50",
        "siniflandirma": "Acute Tox. 4 H332",
        "akut_toksisite_soluma_formu": "toz_sis"
    }]
    res_dust = ClassificationEngine.calculate_mixture_hazards(comp_dust)
    assert any(
        "• Akut Toksisite (Soluma - Toz/Sis Katkı): [İnce Toz Madde] %50.0, ATE = 1.50 mg/L (Kaynak: H332_CONVERSION, Tip: DERIVED, Ref: SEA_ANNEX_I)"
        in step for step in res_dust["calculation_steps"]
    )


def test_reg013_parser_4stage_pipeline_and_validation():
    """
    REG-013: 4 Aşamalı Parser Mimarisi ve Regülatif Doğrulama Motoru
    Akış:
      raw text ➔ parsed assertion ➔ normalized regulatory data ➔ validated regulatory data ➔ classification engine
    """
    from app.services.regulatory_engine.parser import RegulatoryClassificationParser
    from app.services.classification_engine import ClassificationEngine
    from app.models.regulatory import ParsedHazardAssertion, NormalizedHazard, ValidatedHazard

    # 1. Aşama 1 -> Aşama 2: Ham metinden doğrudan iddiaların (ParsedHazardAssertion) çıkarılması
    raw = "Skin Corr. 1B H314 (SCL >= 1%), Eye Dam. 1 H318 (SCL >= 3%)"
    assertions = RegulatoryClassificationParser.parse_assertions(raw)
    assert len(assertions) == 2
    assert isinstance(assertions[0], ParsedHazardAssertion)
    assert assertions[0].asserted_class == "Skin Corr."
    assert assertions[0].asserted_category == "1B"
    assert assertions[0].asserted_codes == ["H314"]
    assert assertions[0].asserted_scl == 1.0

    # 2. Aşama 2 -> Aşama 3: İddianın kanonik terminolojiye dönüştürülmesi (NormalizedHazard)
    normalized_list = RegulatoryClassificationParser.normalize_assertion(assertions[0])
    assert len(normalized_list) == 1
    norm = normalized_list[0]
    assert isinstance(norm, NormalizedHazard)
    assert norm.canonical_class == "Skin Corr."
    assert norm.canonical_category == "1B"
    assert norm.canonical_code == "H314"
    assert norm.scl == 1.0

    # 3. Aşama 3 -> Aşama 4: Regülatif Doğrulama (ValidatedHazard) - Geçerli durum (VALID)
    validated = RegulatoryClassificationParser.validate_normalized(norm)
    assert isinstance(validated, ValidatedHazard)
    assert validated.status == "VALID"
    assert len(validated.issues) == 0
    hazard_entry = validated.to_hazard_entry()
    assert hazard_entry.validation_status == "VALID"
    assert hazard_entry.scl == 1.0

    # 4. Çelişki Denetimi (CONTRADICTORY - H-Kodu vs Zararlılık Sınıfı Uyuşmazlığı)
    # H302 Akut Toksisitedir; metinde Flam. Liq. iddia edilmişse çelişki tespit edilmelidir
    val_contradictory = RegulatoryClassificationParser.process_to_validated_hazards("Flam. Liq. 1 H302")
    assert len(val_contradictory) == 1
    assert val_contradictory[0].status == "CONTRADICTORY"
    assert any(i.code == "CLASS_CODE_MISMATCH" and i.severity == "ERROR" for i in val_contradictory[0].issues)

    # 5. Geçersiz SCL Sınır Denetimi (INVALID - SCL > 100%)
    val_invalid_scl = RegulatoryClassificationParser.process_to_validated_hazards("Skin Corr. 1B H314 (SCL >= 150%)")
    assert len(val_invalid_scl) == 1
    assert val_invalid_scl[0].status == "INVALID"
    assert any(i.code == "INVALID_SCL_BOUNDS" for i in val_invalid_scl[0].issues)
    # Geçersiz SCL motora taşınmamalı (None olmalıdır)
    assert val_invalid_scl[0].to_hazard_entry().scl is None

    # 6. Geçersiz M-Faktörü Denetimi (INVALID - M < 1.0)
    val_invalid_m = RegulatoryClassificationParser.process_to_validated_hazards("Aquatic Chronic 1 H410 (M=0)")
    assert len(val_invalid_m) == 1
    assert val_invalid_m[0].status == "INVALID"
    assert any(i.code == "INVALID_M_FACTOR" for i in val_invalid_m[0].issues)

    # 7. Uygulanamaz M-Faktörü Denetimi (CORRECTED / INAPPLICABLE)
    # Alevlenir sıvıya M-faktörü eklenemez
    val_inapp_m = RegulatoryClassificationParser.process_to_validated_hazards("Flam. Liq. 2 H225 (M=10)")
    assert len(val_inapp_m) == 1
    assert val_inapp_m[0].status == "CORRECTED"
    assert any(i.code == "INAPPLICABLE_M_FACTOR" for i in val_inapp_m[0].issues)

    # 8. Geçersiz Kategori Denetimi (CONTRADICTORY - Göz Tahrişi Kategori 1 Olamaz)
    val_invalid_cat = RegulatoryClassificationParser.process_to_validated_hazards("Eye Irrit. 1 H319")
    assert len(val_invalid_cat) == 1
    assert val_invalid_cat[0].status == "CONTRADICTORY"
    assert any(i.code == "INVALID_CATEGORY" for i in val_invalid_cat[0].issues)

    # 9. CMR Kategori Belirsizlik Denetimi (UNRESOLVED)
    val_unresolved = RegulatoryClassificationParser.process_to_validated_hazards("H350")
    assert len(val_unresolved) == 1
    assert val_unresolved[0].status == "UNRESOLVED"
    assert any(i.code == "CMR_CATEGORY_UNRESOLVED" for i in val_unresolved[0].issues)

    # 10. Karışım Hesaplama Motorunda Denetim İzi (Audit Trail)
    # Reçetede çelişkili girdi olduğunda calculation_steps içinde doğrulama uyarısı listelenmelidir
    res_audit = ClassificationEngine.calculate_mixture_hazards([
        {"ad": "Uyumsuz Çözelti", "konsantrasyon": "%10", "siniflandirma": "Flam. Liq. 1 H302"}
    ])
    assert any("⚠️ GİRDİ VERİ DOĞRULAMA VE MEVZUAT UYGUNLUK DENETİMİ:" in step for step in res_audit["calculation_steps"])
    assert any("Durum: CONTRADICTORY" in step and "CLASS_CODE_MISMATCH" not in step for step in res_audit["calculation_steps"])


def test_reg010_rule_result_evidence_based_model():
    """
    REG-010: RuleResult modelinin kanıta dayalı (evidence-based) karar ve denetim mimarisi:
    RuleResult
    ├── status: SUFFICIENT | INSUFFICIENT_DATA | INDETERMINATE | NOT_APPLICABLE
    ├── hazards: List[ClassifiedHazard]
    ├── evidence: Dict[str, Any]
    ├── calculations: List[Dict[str, Any]]
    ├── assumptions: List[str]
    ├── source_references: List[str]
    ├── decision: Optional[str]
    └── reason: Optional[str]
    """
    from app.models.regulatory import RuleResult, ClassifiedHazard
    from app.services.classification_engine import ClassificationEngine

    # 1. Kullanıcının belirttiği tam JSON şemasıyla başlatma ve senkronizasyon testi
    rr = RuleResult(
        rule="AspirationHazardRule",
        status="INDETERMINATE",
        evidence={
            "aspiration_category_1_sum": 12.0,
            "required_threshold": 10.0,
            "viscosity_40c": None,
            "viscosity_threshold": 20.5
        },
        decision=None,
        reason="Kinematik viskozite verisi eksik"
    )

    # İki yönlü alias ve geriye dönük uyumluluk doğrulaması
    assert rr.rule == "AspirationHazardRule"
    assert rr.rule_name == "AspirationHazardRule"
    assert rr.status == "INDETERMINATE"
    assert rr.data_status == "INDETERMINATE"
    assert rr.decision is None
    assert rr.reason == "Kinematik viskozite verisi eksik"
    assert rr.evidence["aspiration_category_1_sum"] == 12.0
    assert rr.evidence["viscosity_40c"] is None

    dumped = rr.model_dump()
    assert dumped["rule"] == "AspirationHazardRule"
    assert dumped["status"] == "INDETERMINATE"
    assert "evidence" in dumped
    assert "calculations" in dumped
    assert "assumptions" in dumped
    assert "source_references" in dumped

    # 2. Reçete icrasında AspirationHazardRule kanıt ve karar yapısı testi
    res = ClassificationEngine.calculate_mixture_hazards(
        [{"ad": "Çözücü Madde", "konsantrasyon": "%15", "siniflandirma": "Asp. Tox. 1 H304"}],
        kinematik_viskozite=None
    )
    asp_rule = next(r for r in res["rule_results"] if (r.get("rule") or r.get("rule_name")) == "AspirationHazardRule")
    assert asp_rule["status"] == "INDETERMINATE"
    assert asp_rule["evidence"]["aspiration_category_1_sum"] == 15.0
    assert asp_rule["evidence"]["viscosity_40c"] is None
    assert asp_rule["decision"] is None
    assert "Kinematik viskozite verisi eksik" in asp_rule["reason"]
    assert len(asp_rule["source_references"]) >= 1
    assert any("SEA Ek-1" in ref for ref in asp_rule["source_references"])

    # 3. FlammableLiquidRule kanıt ve karar yapısı testi
    res_flam = ClassificationEngine.calculate_mixture_hazards(
        [{"ad": "Aseton", "konsantrasyon": "%50", "siniflandirma": "Flam. Liq. 2 H225"}],
        parlama_noktasi=12.0,
        kaynama_noktasi=56.0
    )
    flam_rule = next(r for r in res_flam["rule_results"] if (r.get("rule") or r.get("rule_name")) == "FlammableLiquidRule")
    assert flam_rule["status"] == "SUFFICIENT"
    assert flam_rule["decision"] == "Flam. Liq. 2 H225"
    assert flam_rule["evidence"]["flash_point"] == 12.0
    assert flam_rule["evidence"]["boiling_point"] == 56.0
    assert len(flam_rule["calculations"]) >= 1

    # 4. SkinEyeRule ve AquaticRule kanıt yapısı testi
    res_multi = ClassificationEngine.calculate_mixture_hazards([
        {"ad": "Asit", "konsantrasyon": "%6", "siniflandirma": "Skin Corr. 1B H314"},
        {"ad": "Çevre Toksik", "konsantrasyon": "%30", "siniflandirma": "Aquatic Chronic 1 H410 (M=1)"},
    ])
    skin_rule = next(r for r in res_multi["rule_results"] if (r.get("rule") or r.get("rule_name")) == "SkinEyeRule")
    assert skin_rule["status"] == "SUFFICIENT"
    assert "total_skin_corr_1" in skin_rule["evidence"]
    assert skin_rule["evidence"]["total_skin_corr_1"] == 6.0
    assert len(skin_rule["calculations"]) >= 1

    aq_rule = next(r for r in res_multi["rule_results"] if (r.get("rule") or r.get("rule_name")) == "AquaticRule")
    assert aq_rule["status"] == "SUFFICIENT"
    assert "c_aq_chronic1_weighted" in aq_rule["evidence"]
    assert aq_rule["evidence"]["c_aq_chronic1_weighted"] == 30.0


def test_reg011_eight_stage_pipeline_and_data_quality_layer():
    """
    REG-011: 8 Aşamalı Mimari Akışı ve DATA QUALITY Katmanı:
    INPUT ➔ NORMALIZATION ➔ DATA QUALITY ➔ RULE ➔ EVIDENCE ➔ DECISION ➔ LABEL ➔ SDS

    Kullanıcı Senaryosu:
    Konsantrasyon = %10–25
    →
    DATA QUALITY = UNCERTAIN olmalı ve bu bilgi kural motoruna gitmelidir.
    """
    from app.services.regulatory_engine.pipeline import RegulatoryPipeline
    from app.services.regulatory_engine.data_quality import DataQualityAssessor
    from app.services.classification_engine import ClassificationEngine
    from app.models.regulatory import CalculationContext

    # 1. INPUT
    raw_components = [
        {
            "ad": "Hidrokarbon Çözücü",
            "konsantrasyon": "%10-25",
            "siniflandirma": "Asp. Tox. 1 H304; Flam. Liq. 3 H226"
        }
    ]

    # 2. NORMALIZATION
    substances = RegulatoryPipeline.adapt_raw_components(raw_components)
    sub = substances[0]
    assert sub.concentration.qualifier == "range"
    assert sub.concentration.min_val == 10.0
    assert sub.concentration.max_val == 25.0
    assert sub.concentration.value == 25.0

    # 3. DATA QUALITY (Bileşen ve Karışım Düzeyinde Değerlendirme)
    assert sub.data_quality is not None
    assert sub.data_quality.quality_level == "UNCERTAIN"
    assert sub.data_quality.concentration_quality == "UNCERTAIN"
    assert "CONCENTRATION_RANGE_UNCERTAINTY" in sub.data_quality.flags
    assert sub.data_quality.uncertainty_score > 0.0

    context = CalculationContext(parlama_noktasi=28.0, kinematik_viskozite_40c=None)
    mix_dq = DataQualityAssessor.assess_mixture(substances, context)
    assert mix_dq.has_uncertain_components is True
    assert "kinematik_viskozite_40c" in mix_dq.missing_physical_data
    assert mix_dq.overall_quality in ("INCOMPLETE", "UNCERTAIN")

    # 4. RULE & 5. EVIDENCE & 6. DECISION (Kural Motoruna Veri Kalitesinin İletilmesi)
    pipeline = RegulatoryPipeline()
    result = pipeline.execute(substances, context)

    # Aspiration kuralı kanıtında veri kalitesi ve eksik viskozite kaydı
    asp_rule = next(r for r in result.rule_results if r.rule_name == "AspirationHazardRule")
    assert asp_rule.evidence["has_uncertain_data"] is True
    assert asp_rule.evidence["component_data_qualities"]["Hidrokarbon Çözücü"] == "UNCERTAIN"
    assert asp_rule.status == "INDETERMINATE"
    assert any("DATA QUALITY" in a for a in asp_rule.assumptions)

    # 7. LABEL (Etiket Elemanları)
    assert "H226" in result.h_ifadeleri
    assert "GHS02" in result.piktogramlar
    assert result.uyari_kelimesi in ("Dikkat", "Tehlike")

    # 8. SDS & Çıktı Entegrasyonu
    res_engine = ClassificationEngine.calculate_mixture_hazards(
        raw_components,
        parlama_noktasi=28.0,
        kinematik_viskozite=None
    )
    assert res_engine["data_quality"] is not None
    assert res_engine["data_quality"]["has_uncertain_components"] is True
    assert "kinematik_viskozite_40c" in res_engine["data_quality"]["missing_physical_data"]
    assert any("VERİ KALİTESİ VE BELİRSİZLİK PROFİLİ" in step for step in res_engine["calculation_steps"])












