import pytest
from app.services.classification_engine import ClassificationEngine

def test_parse_concentration():
    assert ClassificationEngine.parse_concentration("%20-30") == 30.0
    assert ClassificationEngine.parse_concentration("10 - 25%") == 25.0
    assert ClassificationEngine.parse_concentration("%15") == 15.0
    assert ClassificationEngine.parse_concentration("15.5%") == 15.5
    assert ClassificationEngine.parse_concentration("< 2.5%") == 2.5
    assert ClassificationEngine.parse_concentration(">= 50%") == 50.0
    assert ClassificationEngine.parse_concentration("") == 0.0

def test_extract_h_codes():
    codes = ClassificationEngine.extract_h_codes("Flam. Liq. 2 H225, Skin Irrit. 2 H315, Eye Dam. 1 H318, Repr. 2 H361d, EUH066")
    assert "H225" in codes
    assert "H315" in codes
    assert "H318" in codes
    assert "H361d" in codes
    assert "EUH066" in codes

def test_skin_and_eye_additivity():
    # Scenario: 20% Skin Irrit 2 (H315) + 15% Eye Irrit 2 (H319)
    components = [
        {"ad": "Bileşen A", "konsantrasyon": "%20", "siniflandirma": "Skin Irrit. 2 H315"},
        {"ad": "Bileşen B", "konsantrasyon": "%15", "siniflandirma": "Eye Irrit. 2 H319"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H315" in res["h_ifadeleri"]
    assert "H319" in res["h_ifadeleri"]
    assert "GHS07" in res["piktogramlar"]
    assert res["uyari_kelimesi"] == "Dikkat"

def test_skin_corrosion_override():
    # Scenario: 6% Skin Corr 1 (H314) -> Should trigger H314 + H318 + GHS05 + Tehlike
    components = [
        {"ad": "Asit / Baz", "konsantrasyon": "%6", "siniflandirma": "Skin Corr. 1B H314"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H314" in res["h_ifadeleri"]
    assert "GHS05" in res["piktogramlar"]
    assert res["uyari_kelimesi"] == "Tehlike"

def test_isocyanate_respiratory_sensitization():
    # Scenario: 2% HDI Oligomer with both Resp Sens 1 (H334 >= 0.2%) and Skin Sens 1 (H317 >= 1.0%)
    components = [
        {"ad": "İzosiyanat Oligomer", "konsantrasyon": "%2.0", "siniflandirma": "Resp. Sens. 1 H334, Skin Sens. 1 H317"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H334" in res["h_ifadeleri"]
    assert "H317" in res["h_ifadeleri"]
    assert "GHS08" in res["piktogramlar"]
    assert res["uyari_kelimesi"] == "Tehlike"

def test_thinner_solvent_mixture():
    # Scenario: Typical cellulosic thinner
    components = [
        {"ad": "Toluen", "konsantrasyon": "%30", "siniflandirma": "Flam. Liq. 2 H225, Repr. 2 H361d, Asp. Tox. 1 H304, STOT RE 2 H373, Skin Irrit. 2 H315, STOT SE 3 H336"},
        {"ad": "Aseton", "konsantrasyon": "%35", "siniflandirma": "Flam. Liq. 2 H225, Eye Irrit. 2 H319, STOT SE 3 H336, EUH066"},
        {"ad": "Butil Asetat", "konsantrasyon": "%25", "siniflandirma": "Flam. Liq. 3 H226, STOT SE 3 H336, EUH066"},
        {"ad": "Ksilen", "konsantrasyon": "%10", "siniflandirma": "Flam. Liq. 3 H226, Acute Tox. 4 H312, Acute Tox. 4 H332, Skin Irrit. 2 H315"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    
    assert "H225" in res["h_ifadeleri"]
    assert "H304" in res["h_ifadeleri"]
    assert "H315" in res["h_ifadeleri"]
    assert "H319" in res["h_ifadeleri"]
    assert "H336" in res["h_ifadeleri"]
    assert "H361d" in res["h_ifadeleri"]
    assert "H373" in res["h_ifadeleri"]
    
    assert "GHS02" in res["piktogramlar"]
    assert "GHS07" in res["piktogramlar"]
    assert "GHS08" in res["piktogramlar"]
    assert res["uyari_kelimesi"] == "Tehlike"

    # Verify P statements
    p_codes = res["p_ifadeleri"]
    assert "P210" in p_codes
    assert "P280" in p_codes
    assert "P301+P310" in p_codes
    assert "P331" in p_codes
    assert "P501" in p_codes

def test_h_to_p_deduplication():
    # P301+P310 should supersede P301+P312
    p_codes = ClassificationEngine.generate_p_statements(["H300", "H302"])
    assert "P301+P310" in p_codes
    assert "P301+P312" not in p_codes


# ==================== ATE_mix Harmonik Formül Testleri ====================

def test_ate_mix_oral_no_classification():
    """ATE_mix harmonik formül: %30 Toluen (LD50=5580) + %35 Aseton (LD50=5800) → ATE_mix > 2000 → sınıflandırma yok"""
    components = [
        {"ad": "Toluen", "konsantrasyon": "%30", "siniflandirma": "Flam. Liq. 2 H225", "akut_toksisite_oral": 5580},
        {"ad": "Aseton", "konsantrasyon": "%35", "siniflandirma": "Flam. Liq. 2 H225", "akut_toksisite_oral": 5800},
    ]
    # ATE_mix = 100 / (30/5580 + 35/5800) = 100 / 0.01141 ≈ 8765 > 2000
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H300" not in res["h_ifadeleri"]
    assert "H301" not in res["h_ifadeleri"]
    assert "H302" not in res["h_ifadeleri"]


def test_ate_mix_oral_high_toxicity():
    """ATE_mix harmonik formül: %50 bileşen (LD50=100) + %50 bileşen (LD50=200) → ATE_mix ~133 → H301 Kat 3"""
    components = [
        {"ad": "Toksik A", "konsantrasyon": "%50", "siniflandirma": "Acute Tox. 3 H301", "akut_toksisite_oral": 100},
        {"ad": "Toksik B", "konsantrasyon": "%50", "siniflandirma": "Acute Tox. 3 H301", "akut_toksisite_oral": 200},
    ]
    # ATE_mix = 100 / (50/100 + 50/200) = 100 / 0.75 ≈ 133.3 → Kategori 3 (H301)
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H301" in res["h_ifadeleri"]
    assert any(
        s["zararlilik_sinifi"] == "Akut Toksisite - Oral" and s["kategori"] == "Kategori 3"
        for s in res["siniflandirmalar"]
    )
    assert "GHS06" in res["piktogramlar"]
    assert res["uyari_kelimesi"] == "Tehlike"


def test_ate_mix_dermal_classification():
    """ATE_mix harmonik formül: %25 (dermal LD50=800) + %75 (dermal LD50=1500) → Kat 4 (H312)"""
    components = [
        {"ad": "Bileşen C", "konsantrasyon": "%25", "siniflandirma": "Acute Tox. 4 H312", "akut_toksisite_dermal": 800},
        {"ad": "Bileşen D", "konsantrasyon": "%75", "siniflandirma": "Acute Tox. 4 H312", "akut_toksisite_dermal": 1500},
    ]
    # ATE_mix = 100 / (25/800 + 75/1500) = 100 / 0.08125 ≈ 1230.8 → Kategori 4 (H312)
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H312" in res["h_ifadeleri"]
    assert any(
        s["zararlilik_sinifi"] == "Akut Toksisite - Dermal" and s["kategori"] == "Kategori 4"
        for s in res["siniflandirmalar"]
    )


def test_ate_mix_inhalation_classification():
    """ATE_mix harmonik formül: %60 (LC50=5.0 mg/L) + %40 (LC50=15 mg/L) → Kat 3 (H331)"""
    components = [
        {"ad": "Buhar E", "konsantrasyon": "%60", "siniflandirma": "Acute Tox. 3 H331", "akut_toksisite_soluma": 5.0},
        {"ad": "Buhar F", "konsantrasyon": "%40", "siniflandirma": "Acute Tox. 4 H332", "akut_toksisite_soluma": 15.0},
    ]
    # ATE_mix = 100 / (60/5 + 40/15) = 100 / 14.667 ≈ 6.82 → Kategori 3 (H331)
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H331" in res["h_ifadeleri"]
    assert any(
        s["zararlilik_sinifi"] == "Akut Toksisite - Soluma" and s["kategori"] == "Kategori 3"
        for s in res["siniflandirmalar"]
    )
    assert "GHS06" in res["piktogramlar"]


def test_ate_mix_conversion_table_fallback():
    """H kodu varken sayısal ATE yoksa SEA Ek-1 Tablo 3.1.2 dönüşüm değerleri kullanılır"""
    components = [
        {"ad": "Akut Toksik", "konsantrasyon": "%60", "siniflandirma": "Acute Tox. 4 H302"},
    ]
    # No explicit ATE → conversion table: H302 → 500 mg/kg
    # ATE_mix = 100 / (60/500) = 100 / 0.12 = 833.3 → Kategori 4 (H302)
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H302" in res["h_ifadeleri"]
    assert any(
        s["zararlilik_sinifi"] == "Akut Toksisite - Oral" and s["kategori"] == "Kategori 4"
        for s in res["siniflandirmalar"]
    )


def test_ate_mix_no_acute_components():
    """Akut toksik olmayan bileşenlerle ATE hesaplaması tetiklenmemeli"""
    components = [
        {"ad": "Güvenli", "konsantrasyon": "%100", "siniflandirma": "Eye Irrit. 2 H319"},
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    acute_h_codes = {"H300", "H301", "H302", "H310", "H311", "H312", "H330", "H331", "H332"}
    assert not acute_h_codes.intersection(set(res["h_ifadeleri"]))


def test_ate_mix_all_three_routes():
    """Üç maruziyet yolu birden sınıflandırılabilir"""
    components = [
        {
            "ad": "Çok Toksik",
            "konsantrasyon": "%100",
            "siniflandirma": "Acute Tox. 3 H301, Acute Tox. 3 H311, Acute Tox. 3 H331",
            "akut_toksisite_oral": 200,
            "akut_toksisite_dermal": 800,
            "akut_toksisite_soluma": 8.0
        },
    ]
    # Oral: ATE_mix = 100/(100/200) = 200 → Kat 3 (H301)
    # Dermal: ATE_mix = 100/(100/800) = 800 → Kat 3 (H311)
    # Soluma: ATE_mix = 100/(100/8) = 8 → Kat 3 (H331)
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H301" in res["h_ifadeleri"]
    assert "H311" in res["h_ifadeleri"]
    assert "H331" in res["h_ifadeleri"]
    assert "GHS06" in res["piktogramlar"]
    assert res["uyari_kelimesi"] == "Tehlike"
    oral = [s for s in res["siniflandirmalar"] if s["zararlilik_sinifi"] == "Akut Toksisite - Oral"]
    dermal = [s for s in res["siniflandirmalar"] if s["zararlilik_sinifi"] == "Akut Toksisite - Dermal"]
    inhal = [s for s in res["siniflandirmalar"] if s["zararlilik_sinifi"] == "Akut Toksisite - Soluma"]
    assert len(oral) == 1
    assert len(dermal) == 1
    assert len(inhal) == 1


# ==================== Sucul Çevre Zararları (H400 & M-Faktörü) Testleri ====================

def test_aquatic_acute1_h400_classification():
    """%30 Aquatic Acute 1 (H400) içeren karışım -> H400 Kategori 1 + GHS09 + Dikkat"""
    components = [
        {"ad": "Biyosit A", "konsantrasyon": "%30", "siniflandirma": "Aquatic Acute 1 H400"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H400" in res["h_ifadeleri"]
    assert "GHS09" in res["piktogramlar"]
    assert res["uyari_kelimesi"] == "Dikkat"
    assert any(
        s["zararlilik_sinifi"] == "Sucul Ortama Zararlı - Akut" and s["kategori"] == "Akut Kategori 1"
        for s in res["siniflandirmalar"]
    )


def test_aquatic_acute1_below_threshold():
    """%20 Aquatic Acute 1 (H400) (< %25) içeren karışım -> H400 olarak sınıflandırılmaz"""
    components = [
        {"ad": "Biyosit A", "konsantrasyon": "%20", "siniflandirma": "Aquatic Acute 1 H400"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H400" not in res["h_ifadeleri"]
    assert "GHS09" not in res["piktogramlar"]


def test_aquatic_acute1_and_chronic_independent():
    """%30 H400 ve %30 H410 içeren karışım -> Hem Akut 1 hem Kronik 1 sınıflandırılır"""
    components = [
        {"ad": "Madde X", "konsantrasyon": "%30", "siniflandirma": "Aquatic Acute 1 H400"},
        {"ad": "Madde Y", "konsantrasyon": "%30", "siniflandirma": "Aquatic Chronic 1 H410"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H400" in res["h_ifadeleri"]
    assert "H410" in res["h_ifadeleri"]
    assert "GHS09" in res["piktogramlar"]
    sinif_adlari = [s["zararlilik_sinifi"] for s in res["siniflandirmalar"]]
    assert "Sucul Ortama Zararlı - Akut" in sinif_adlari
    assert "Sucul Ortama Zararlı - Kronik" in sinif_adlari


def test_m_factor_aquatic_acute1():
    """%5 H400 bileşen M=10 faktörüyle 5*10=%50 >= %25 -> Akut 1 (H400) olarak sınıflandırılır"""
    components = [
        {
            "ad": "Yüksek Toksik Biyosit",
            "konsantrasyon": "%5",
            "siniflandirma": "Aquatic Acute 1 H400",
            "m_faktoru_akut": 10.0
        }
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H400" in res["h_ifadeleri"]
    assert "GHS09" in res["piktogramlar"]


def test_m_factor_aquatic_chronic1():
    """%3 H410 bileşen M_kronik=10 faktörüyle 3*10=%30 >= %25 -> Kronik 1 (H410) olarak sınıflandırılır"""
    components = [
        {
            "ad": "Yüksek Toksik Kronik Biyosit",
            "konsantrasyon": "%3",
            "siniflandirma": "Aquatic Chronic 1 H410",
            "m_faktoru_kronik": 10.0
        }
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H410" in res["h_ifadeleri"]
    assert "GHS09" in res["piktogramlar"]


def test_m_factor_default_one():
    """M-faktörü verilmediğinde varsayılan 1 olarak hesaplanır"""
    components = [
        {"ad": "Normal Biyosit", "konsantrasyon": "%15", "siniflandirma": "Aquatic Acute 1 H400"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "H400" not in res["h_ifadeleri"]


def test_ghs06_suppresses_ghs07_for_acute_only():
    """GHS06 mevcut ve GHS07 sadece H302'den geliyorsa GHS07 elenmeli"""
    components = [
        {"ad": "Toksik Oral 3", "konsantrasyon": "%80", "siniflandirma": "Acute Tox. 3 H301", "akut_toksisite_oral": 100},
        {"ad": "Zararlı Oral 4", "konsantrasyon": "%20", "siniflandirma": "Acute Tox. 4 H302", "akut_toksisite_oral": 500}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "GHS06" in res["piktogramlar"]
    assert "GHS07" not in res["piktogramlar"]


def test_ghs06_does_not_suppress_ghs07_if_skin_irritation():
    """GHS06 mevcut ancak H315 (Cilt Tahrişi) de varsa GHS07 korunmalı"""
    components = [
        {"ad": "Toksik Madde", "konsantrasyon": "%50", "siniflandirma": "Acute Tox. 3 H301", "akut_toksisite_oral": 100},
        {"ad": "Cilt Tahriş Edici", "konsantrasyon": "%50", "siniflandirma": "Skin Irrit. 2 H315"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(components)
    assert "GHS06" in res["piktogramlar"]
    assert "GHS07" in res["piktogramlar"]

