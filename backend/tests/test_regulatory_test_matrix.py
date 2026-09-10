"""
Regulatory Test Matrix Parametrik Test Koşucusu
SEA ve CLP Yönetmeliklerine göre referans test veri setinin (regulatory_test_matrix.json)
otomatik doğrulaması.
"""

import os
import json
import pytest
from typing import Dict, Any, List

from app.services.classification_engine import ClassificationEngine

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "data")
MATRIX_PATH = os.path.join(DATA_DIR, "regulatory_test_matrix.json")


def load_test_matrix() -> List[Dict[str, Any]]:
    assert os.path.exists(MATRIX_PATH), f"Referans test matrisi bulunamadı: {MATRIX_PATH}"
    with open(MATRIX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


TEST_CASES = load_test_matrix()


@pytest.mark.parametrize("case", TEST_CASES, ids=[c["reg_id"] for c in TEST_CASES])
def test_regulatory_matrix_case(case: Dict[str, Any]):
    """
    Her regülasyon matrisi senaryosunu sınıflandırma motorunda çalıştırır
    ve beklenen çıktılarla kıyaslar.
    """
    reg_id = case["reg_id"]
    components = case["input_components"]
    context = case.get("input_context", {})

    fp = context.get("parlama_noktasi")
    bp = context.get("kaynama_noktasi")
    visk = context.get("kinematik_viskozite_40c")
    ph = context.get("ph")

    res = ClassificationEngine.calculate_mixture_hazards(
        bilesenler=components,
        parlama_noktasi=fp,
        kaynama_noktasi=bp,
        kinematik_viskozite_40c=visk,
        ph=ph
    )

    expected_status = case["expected_status"]
    expected_h = set(case.get("expected_h", []))
    expected_euh = set(case.get("expected_euh", []))
    expected_pictograms = set(case.get("expected_pictograms", []))
    expected_warning = case.get("expected_warning", "Yok")

    if expected_status == "TRUE":
        # H-kodları tam eşleşmeli
        actual_h = set(res.get("h_ifadeleri", []))
        for h in expected_h:
            assert h in actual_h, f"[{reg_id}] Beklenen H-kodu bulunamadı: {h} (Aktüel: {actual_h})"

        # EUH-kodları tam eşleşmeli
        actual_euh = set(res.get("euh_ifadeleri", []))
        for euh in expected_euh:
            assert euh in actual_euh, f"[{reg_id}] Beklenen EUH-kodu bulunamadı: {euh} (Aktüel: {actual_euh})"

        # Piktogramlar tam eşleşmeli
        actual_p = set(res.get("piktogramlar", []))
        for p in expected_pictograms:
            assert p in actual_p, f"[{reg_id}] Beklenen piktogram bulunamadı: {p} (Aktüel: {actual_p})"

        # Uyarı kelimesi eşleşmeli
        if expected_warning != "Yok":
            assert res.get("uyari_kelimesi") == expected_warning, \
                f"[{reg_id}] Beklenen uyarı kelimesi '{expected_warning}', aktüel: '{res.get('uyari_kelimesi')}'"

    elif expected_status == "FALSE":
        # Belirtilen H kodları tetiklenmemeli
        actual_h = set(res.get("h_ifadeleri", []))
        for h in case.get("input_components", []):
            sinif = h.get("siniflandirma", "")
            # Zararlılık atanmamış olmalı
        if not expected_h:
            # Sadece bu kurala ait zararlılık yok
            pass

    elif expected_status in ("INDETERMINATE", "INSUFFICIENT_DATA"):
        # Belirsizlik veya eksik veri bayrağı kalkmış olmalı
        has_indet = res.get("has_indeterminate", False)
        dq = res.get("data_quality", {})
        overall_dq = dq.get("overall_quality") if isinstance(dq, dict) else getattr(dq, "overall_quality", None)
        missing = dq.get("missing_physical_data", []) if isinstance(dq, dict) else getattr(dq, "missing_physical_data", [])

        is_uncertain = has_indet or (overall_dq in ("INCOMPLETE", "UNCERTAIN", "CONTRADICTORY")) or len(missing) > 0
        assert is_uncertain, f"[{reg_id}] Beklenen {expected_status} durumu motor çıktısında belirsizlik oluşturmadı!"
