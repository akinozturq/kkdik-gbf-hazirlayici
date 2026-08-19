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
