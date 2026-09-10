"""
Regulatory Decision ve Projeksiyon Ayrıştırma Test Paketi
(Regulatory Decision Decoupling & Projections Test Suite)

RegulatoryDecision, RegulatoryLabel, TransportClassification, SDSGenerator
ve RegulatoryAuditTrail katmanlarının birbirinden bağımsız çalıştığını doğrular.
"""

import pytest
from typing import Dict, Any, List

from app.models.regulatory import (
    RegulatoryDecision,
    RegulatoryLabel,
    TransportClassification,
    RegulatoryAuditTrail,
    CalculationContext
)
from app.services.classification_engine import ClassificationEngine
from app.services.regulatory_engine.sds_generator import SDSGenerator


def test_pure_regulatory_decision_evaluation():
    """
    evaluate_decision metodunun SDS veya etiket elemanlarından bağımsız,
    saf bir RegulatoryDecision nesnesi ürettiğini doğrular.
    """
    components = [
        {"ad": "Ksilen", "konsantrasyon": "%20", "siniflandirma": "Flam. Liq. 3 H226, Skin Irrit. 2 H315"},
        {"ad": "Toluen", "konsantrasyon": "%15", "siniflandirma": "Asp. Tox. 1 H304, Flam. Liq. 2 H225"}
    ]
    context = CalculationContext(
        parlama_noktasi=18.0,
        kaynama_noktasi=110.0,
        kinematik_viskozite_40c=15.0
    )

    decision: RegulatoryDecision = ClassificationEngine.evaluate_decision(
        bilesenler=components,
        parlama_noktasi=18.0,
        kaynama_noktasi=110.0,
        kinematik_viskozite_40c=15.0
    )

    assert isinstance(decision, RegulatoryDecision)
    assert decision.decision_id.startswith("DEC-")
    assert decision.has_classification is True
    assert "H225" in decision.h_codes
    assert "H315" in decision.h_codes
    assert "H304" in decision.h_codes
    assert decision.data_quality is not None
    assert decision.data_quality.overall_quality == "CONFIRMED"
    assert len(decision.evidence_pack) > 0

    # RuleResult kanıt yapısı doğrulanmalı
    asp_rule = next((r for r in decision.evidence_pack if "Aspiration" in r.rule_name), None)
    assert asp_rule is not None
    assert asp_rule.status == "SUFFICIENT"
    assert asp_rule.decision is not None


def test_label_projection_and_special_packaging():
    """
    RegulatoryDecision üzerinden türetilen RegulatoryLabel projeksiyonunu ve
    SEA Madde 33 Özel Ambalaj Şartlarını (Dokunulabilir Uyarı, Çocuk Emniyetli Kapak) test eder.
    """
    # 1. Aşındırıcı + Aspirasyon Senaryosu (Her iki özel ambalaj şartını da tetiklemeli)
    components = [
        {"ad": "Sodyum Hidroksit", "konsantrasyon": "%8", "siniflandirma": "Skin Corr. 1A H314"},
        {"ad": "Hidrokarbon Çözücü", "konsantrasyon": "%12", "siniflandirma": "Asp. Tox. 1 H304"}
    ]
    decision = ClassificationEngine.evaluate_decision(
        bilesenler=components,
        kinematik_viskozite_40c=12.0
    )
    label: RegulatoryLabel = ClassificationEngine.generate_label(decision)

    assert isinstance(label, RegulatoryLabel)
    assert label.signal_word == "Tehlike"
    assert "GHS05" in label.pictograms
    assert "GHS08" in label.pictograms
    assert "H314" in label.hazard_statements
    assert "H304" in label.hazard_statements

    # SEA Madde 33 / CLP Ek-II gereklilikleri
    assert label.tactile_warning_required is True, "H314 ve H304 dokunulabilir tehlike uyarısı gerektirir"
    assert label.child_resistant_fastening_required is True, "H314 ve H304 çocuk emniyetli kapak gerektirir"

    # P-ifadeleri türetilmiş olmalı
    assert len(label.precautionary_statements) > 0


def test_transport_projection_decoupling():
    """
    Düzenleyici Karar ve fiziksel parametrelerden bağımsız TransportClassification
    projeksiyonunu test eder.
    """
    # Sınıf 3 Alevlenir Boya/Tiner
    components = [
        {"ad": "Aseton", "konsantrasyon": "%40", "siniflandirma": "Flam. Liq. 2 H225, Eye Irrit. 2 H319"}
    ]
    context = CalculationContext(parlama_noktasi=-18.0, kaynama_noktasi=56.0)
    decision = ClassificationEngine.evaluate_decision(
        bilesenler=components,
        parlama_noktasi=-18.0,
        kaynama_noktasi=56.0
    )

    transport: TransportClassification = ClassificationEngine.generate_transport(
        decision=decision,
        context=context,
        product_name="Poliüretan Tiner"
    )

    assert isinstance(transport, TransportClassification)
    assert transport.un_number == "UN 1263"
    assert transport.class_code == "3"
    assert transport.packing_group == "PG II"
    assert transport.tunnel_restriction_code == "(D/E)"
    assert transport.status == "SUGGESTION"


def test_sds_generator_projection():
    """
    SDSGenerator servisinin RegulatoryDecision, RegulatoryLabel ve TransportClassification
    nesnelerini 16 bölümlük SDS modeline doğru şekilde yansıttığını ve
    temel SDS verilerini koruduğunu doğrular.
    """
    components = [
        {"ad": "Ksilen", "konsantrasyon": "%25", "siniflandirma": "Flam. Liq. 3 H226, Skin Irrit. 2 H315"}
    ]
    context = CalculationContext(parlama_noktasi=25.0, kaynama_noktasi=138.0)

    decision = ClassificationEngine.evaluate_decision(
        bilesenler=components,
        parlama_noktasi=25.0,
        kaynama_noktasi=138.0
    )
    label = ClassificationEngine.generate_label(decision)
    transport = ClassificationEngine.generate_transport(decision, context, "Örnek Solvent")

    base_sds = {
        "b1_kimlik": {
            "b1_1": {"ticari_adi": "Örnek Solvent", "madde_karisim_adi": "Örnek Solvent"},
            "b1_3": {"sirket_adi": "Aypol Kimya A.Ş."}
        },
        "b3_bilesim": {
            "karisim": {"bilesenler": components}
        }
    }

    projected_sds = ClassificationEngine.project_to_sds(
        decision=decision,
        label=label,
        transport=transport,
        base_sds=base_sds
    )

    # 1. Temel SDS verileri korunmalı
    assert projected_sds["b1_kimlik"]["b1_3"]["sirket_adi"] == "Aypol Kimya A.Ş."

    # 2. Bölüm 2.1 Sınıflandırma
    b2_1 = projected_sds["b2_zarar_tanimi"]["b2_1"]
    assert b2_1["siniflandirilmamis"] is False
    assert len(b2_1["siniflandirmalar"]) >= 1

    # 3. Bölüm 2.2 Etiket Elemanları
    b2_2 = projected_sds["b2_zarar_tanimi"]["b2_2"]
    assert b2_2["uyari_kelimesi"] == label.signal_word
    assert b2_2["piktogramlar"] == label.pictograms
    assert b2_2["h_ifadeleri"] == label.hazard_statements

    # 4. Bölüm 14 Taşımacılık
    b14 = projected_sds["b14_tasimacilik"]
    assert b14["b14_1_un_numarasi"] == transport.un_number
    assert b14["b14_4_ambalajlama_grubu"] == transport.packing_group

    # 5. Metadata
    assert projected_sds["_regulatory_decision_id"] == decision.decision_id


def test_unified_audit_trail_completeness():
    """
    Bakanlık / KDU denetimleri için üretilen RegulatoryAuditTrail kaydının
    tüm aşamaları (INPUT -> DATA_QUALITY -> RULE_EXECUTION -> DECISION -> LABEL -> TRANSPORT)
    eksiksiz içerdiğini doğrular.
    """
    components = [
        {"ad": "Toluen", "konsantrasyon": "%30", "siniflandirma": "Flam. Liq. 2 H225, Asp. Tox. 1 H304"}
    ]
    res = ClassificationEngine.calculate_mixture_hazards(
        bilesenler=components,
        parlama_noktasi=4.0,
        kaynama_noktasi=110.0,
        kinematik_viskozite=10.0
    )

    audit_dict = res.get("audit_trail")
    assert audit_dict is not None, "ClassificationResult içerisinde audit_trail bulunmalıdır"
    audit_trail = RegulatoryAuditTrail.model_validate(audit_dict)

    stages = [entry.stage for entry in audit_trail.entries]
    assert "INPUT" in stages
    assert "DATA_QUALITY" in stages
    assert "RULE_EXECUTION" in stages
    assert "DECISION" in stages
    assert "LABEL" in stages
    assert "TRANSPORT" in stages

    # Yasal dayanak kontrolleri
    for entry in audit_trail.entries:
        assert entry.legislative_reference is not None, f"{entry.stage} aşamasında mevzuat atfı eksik"
