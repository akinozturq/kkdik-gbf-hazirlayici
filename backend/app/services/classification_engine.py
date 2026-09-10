"""
KKDİK / SEA Yönetmeliği Karışım Sınıflandırma Motoru Adaptörü (ClassificationEngine Adapter)
v2.0: Yeni modüler RegulatoryPipeline ve LabelGenerator mimarisini eski API ile uyumlu tutar.
"""

import os
import json
from typing import List, Dict, Any, Optional, Set

from app.models.regulatory import (
    CalculationContext,
    RegulatoryDecision,
    RegulatoryLabel,
    TransportClassification
)
from app.services.regulatory_engine.pipeline import RegulatoryPipeline

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
H_TO_P_PATH = os.path.join(DATA_DIR, "h_to_p_mapping.json")
H_STATEMENTS_PATH = os.path.join(DATA_DIR, "h_statements.json")
P_STATEMENTS_PATH = os.path.join(DATA_DIR, "p_statements.json")
PICTOGRAMS_PATH = os.path.join(DATA_DIR, "pictograms.json")


class ClassificationEngine:
    """
    SEA Yönetmeliği (RG: 28848) ve Ek-1 kurallarına dayalı Karışım Zararlılık Hesaplama
    ve H ➔ P Önlem İfadeleri Haritalama Motoru.
    v2.0: RegulatoryPipeline mimarisine delege eder.
    """

    _pipeline: Optional[RegulatoryPipeline] = None

    @classmethod
    def get_pipeline(cls) -> RegulatoryPipeline:
        if cls._pipeline is None:
            cls._pipeline = RegulatoryPipeline()
        return cls._pipeline

    @classmethod
    def parse_concentration(cls, conc_str: Any) -> float:
        """
        Bölüm 3.2'deki '%10-25', '15%', '< 2.5%', '>= 50%' gibi metinlerden
        nitelikli float konsantrasyonu çeker.
        """
        return RegulatoryPipeline.parse_concentration_model(conc_str).value

    @classmethod
    def parse_float_safe(
        cls,
        val: Any,
        default: Optional[float] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> Optional[float]:
        """
        Sayısal olmayan veya kirli metinlerden güvenli float çeker.
        İsteğe bağlı min_val ve max_val sınırlarını denetler.
        """
        return RegulatoryPipeline.parse_float_safe(val, default, min_val=min_val, max_val=max_val)

    @classmethod
    def resolve_repro_h_code(cls, found_codes: Set[str], prefix: str = "H360") -> str:
        """
        H360/H361 varyasyonlarında deterministik öncelik çözümlemesi yapar.
        """
        from app.services.rules.cmr_rule import CMRRule
        return CMRRule.resolve_repro_h_code(found_codes, prefix)

    @classmethod
    def generate_p_statements(cls, h_codes: List[str]) -> List[str]:
        """
        Verilen H-kodları listesinden SEA Ek-4 uyarınca P-kodlarını türetir ve eler.
        """
        from app.services.regulatory_engine.label_generator import LabelGenerator
        resolved = LabelGenerator.resolve_label_elements(
            raw_hazards=[],
            raw_h_codes=set(h_codes),
            raw_euh_codes=set(),
            raw_pictograms=set(),
            rule_warning_words=[]
        )
        return resolved["p_ifadeleri"]

    @classmethod
    def extract_h_codes(cls, text: str) -> List[str]:
        """
        Metin içerisindeki tüm H ve EUH kodlarını normalize ederek ayıklar.
        """
        return RegulatoryPipeline.extract_h_codes(text)

    @classmethod
    def calculate_mixture_hazards(
        cls,
        bilesenler: List[Dict[str, Any]],
        parlama_noktasi: Optional[float] = None,
        kaynama_noktasi: Optional[float] = None,
        kinematik_viskozite: Optional[float] = None,
        ph: Optional[float] = None,
        kinematik_viskozite_40c: Optional[float] = None,
        fiziksel_hal: Optional[str] = "Sıvı"
    ) -> Dict[str, Any]:
        """
        SEA Yönetmeliği Ek-1 toplanabilirlik ve eşik değer kurallarına göre
        karışımın sınıflandırmasını, H-kodlarını, Piktogramlarını, Uyarı Kelimesini
        ve adım adım hesaplama açıklamalarını üretir.
        """
        visk = kinematik_viskozite_40c if kinematik_viskozite_40c is not None else kinematik_viskozite
        pipeline = cls.get_pipeline()
        substances = pipeline.adapt_raw_components(bilesenler)
        context = CalculationContext(
            parlama_noktasi=parlama_noktasi,
            kaynama_noktasi=kaynama_noktasi,
            kinematik_viskozite_40c=visk,
            ph=ph,
            fiziksel_hal=fiziksel_hal
        )
        result = pipeline.execute(substances, context)
        return {
            "siniflandirmalar": result.siniflandirmalar,
            "h_ifadeleri": result.h_ifadeleri,
            "euh_ifadeleri": result.euh_ifadeleri,
            "piktogramlar": result.piktogramlar,
            "uyari_kelimesi": result.uyari_kelimesi,
            "p_ifadeleri": result.p_ifadeleri,
            "calculation_steps": result.calculation_steps,
            "rule_results": [r.model_dump() for r in result.rule_results],
            "data_status_summary": {r.rule_name: r.data_status for r in result.rule_results},
            "has_indeterminate": result.has_indeterminate,
            "indeterminate_hazards": result.indeterminate_hazards,
            "data_quality": result.data_quality.model_dump() if result.data_quality else None,
            "precedence_audit_log": result.precedence_audit_log,
            "decision": result.decision.model_dump() if result.decision else None,
            "label": result.label.model_dump() if result.label else None,
            "transport": result.transport.model_dump() if result.transport else None,
            "audit_trail": result.audit_trail.model_dump() if result.audit_trail else None
        }

    @classmethod
    def evaluate_decision(
        cls,
        bilesenler: List[Dict[str, Any]],
        parlama_noktasi: Optional[float] = None,
        kaynama_noktasi: Optional[float] = None,
        kinematik_viskozite: Optional[float] = None,
        ph: Optional[float] = None,
        kinematik_viskozite_40c: Optional[float] = None,
        fiziksel_hal: Optional[str] = "Sıvı"
    ) -> RegulatoryDecision:
        """
        SDS veya etiket üretiminden bağımsız olarak, sadece saf Düzenleyici Karar (RegulatoryDecision) üretir.
        """
        visk = kinematik_viskozite_40c if kinematik_viskozite_40c is not None else kinematik_viskozite
        pipeline = cls.get_pipeline()
        substances = pipeline.adapt_raw_components(bilesenler)
        context = CalculationContext(
            parlama_noktasi=parlama_noktasi,
            kaynama_noktasi=kaynama_noktasi,
            kinematik_viskozite_40c=visk,
            ph=ph,
            fiziksel_hal=fiziksel_hal
        )
        return pipeline.evaluate_decision(substances, context)

    @classmethod
    def generate_label(cls, decision: RegulatoryDecision) -> RegulatoryLabel:
        """
        Düzenleyici karardan bağımsız etiket projeksiyonu üretir.
        """
        from app.services.regulatory_engine.label_generator import LabelGenerator
        return LabelGenerator.generate_label(decision)

    @classmethod
    def generate_transport(
        cls,
        decision: RegulatoryDecision,
        context: Optional[CalculationContext] = None,
        product_name: str = ""
    ) -> TransportClassification:
        """
        Düzenleyici karardan bağımsız taşımacılık (ADR) projeksiyonu üretir.
        """
        from app.services.transport_engine import TransportSuggestionEngine
        return TransportSuggestionEngine.classify_from_decision(decision, context, product_name)

    @classmethod
    def project_to_sds(
        cls,
        decision: RegulatoryDecision,
        label: RegulatoryLabel,
        transport: Optional[TransportClassification] = None,
        base_sds: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Karar, etiket ve taşımacılık nesnelerini 16 bölümlük SDS şemasına haritalar.
        """
        from app.services.regulatory_engine.sds_generator import SDSGenerator
        return SDSGenerator.project_to_sds_sections(decision, label, transport, base_sds)
