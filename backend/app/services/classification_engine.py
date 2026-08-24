"""
KKDİK / SEA Yönetmeliği Karışım Sınıflandırma Motoru Adaptörü (ClassificationEngine Adapter)
v2.0: Yeni modüler RegulatoryPipeline ve LabelGenerator mimarisini eski API ile uyumlu tutar.
"""

import os
import json
from typing import List, Dict, Any, Optional, Set

from app.models.regulatory import CalculationContext
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
    def parse_float_safe(cls, val: Any, default: Optional[float] = None) -> Optional[float]:
        """
        Sayısal olmayan veya kirli metinlerden güvenli float çeker.
        """
        return RegulatoryPipeline.parse_float_safe(val, default)

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
        kinematik_viskozite: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        SEA Yönetmeliği Ek-1 toplanabilirlik ve eşik değer kurallarına göre
        karışımın sınıflandırmasını, H-kodlarını, Piktogramlarını, Uyarı Kelimesini
        ve adım adım hesaplama açıklamalarını üretir.
        """
        pipeline = cls.get_pipeline()
        substances = pipeline.adapt_raw_components(bilesenler)
        context = CalculationContext(
            parlama_noktasi=parlama_noktasi,
            kaynama_noktasi=kaynama_noktasi,
            kinematik_viskozite_40c=kinematik_viskozite
        )
        result = pipeline.execute(substances, context)
        return {
            "siniflandirmalar": result.siniflandirmalar,
            "h_ifadeleri": result.h_ifadeleri,
            "euh_ifadeleri": result.euh_ifadeleri,
            "piktogramlar": result.piktogramlar,
            "uyari_kelimesi": result.uyari_kelimesi,
            "p_ifadeleri": result.p_ifadeleri,
            "calculation_steps": result.calculation_steps
        }
