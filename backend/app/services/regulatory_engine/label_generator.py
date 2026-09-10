"""
Etiket Elemanları ve Öncelik Çözümleme Motoru (Label Generator)
SEA Yönetmeliği Madde 26, 28 ve 30(1) Hükümleri
"""

import os
import json
from typing import List, Dict, Set, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
H_TO_P_PATH = os.path.join(DATA_DIR, "h_to_p_mapping.json")


class LabelGenerator:
    """
    Kural stratejilerinden gelen ham zararlılık, H-kodu ve piktogram listesini
    SEA Madde 26 & 28 öncelik matrisine göre süzer, uyarı kelimesini belirler
    ve deterministik P-kodları listesi üretir.
    """

    _H_TO_P_MAP: Optional[Dict[str, List[str]]] = None
    _PRECEDENCE_MATRIX: Optional[Any] = None

    @classmethod
    def _load_p_map(cls):
        if cls._H_TO_P_MAP is None and os.path.exists(H_TO_P_PATH):
            with open(H_TO_P_PATH, "r", encoding="utf-8") as f:
                cls._H_TO_P_MAP = json.load(f)

    @classmethod
    def get_precedence_matrix(cls):
        if cls._PRECEDENCE_MATRIX is None:
            from app.services.regulatory_engine.precedence_matrix import PictogramPrecedenceMatrix
            cls._PRECEDENCE_MATRIX = PictogramPrecedenceMatrix()
        return cls._PRECEDENCE_MATRIX

    @classmethod
    def resolve_label_elements(
        cls,
        raw_hazards: List[Dict[str, str]],
        raw_h_codes: Set[str],
        raw_euh_codes: Set[str],
        raw_pictograms: Set[str],
        rule_warning_words: List[str]
    ) -> Dict[str, Any]:
        cls._load_p_map()

        # 1. UYARI KELİMESİ HİYERARŞİSİ (Danger > Warning > None)
        if any(w == "Tehlike" for w in rule_warning_words):
            final_warning = "Tehlike"
        elif any(w == "Dikkat" for w in rule_warning_words):
            final_warning = "Dikkat"
        else:
            final_warning = "Yok"

        # 2. GHS PİKTOGRAM ÖNCELİK VE ELEME MATRİSİ (SEA Madde 26 & CLP Article 26)
        matrix = cls.get_precedence_matrix()
        filtered_piktogramlar, precedence_audit_log = matrix.resolve(
            raw_pictograms=raw_pictograms,
            raw_h_codes=raw_h_codes
        )

        # 3. P-KODLARI HARİTALAMA & ELEME (SEA Ek-4 & Madde 30(1))
        p_set = set()
        if cls._H_TO_P_MAP:
            for h in raw_h_codes:
                for p in cls._H_TO_P_MAP.get(h, []):
                    p_set.add(p)

        # Mükerrer / Hiyerarşik P-Kodu Sadeleştirmesi
        # P301+P310 (Tehlike - Zehir Merkezi) varken P301+P312 (Dikkat) elenir
        if "P301+P310" in p_set:
            p_set.discard("P301+P312")

        # P301+P330+P331 (Kusturmayın) varken P330 veya P331 tekil elenir
        if "P301+P330+P331" in p_set:
            p_set.discard("P330")
            p_set.discard("P331")

        # P361+P364 (Hemen çıkarın ve yıkayın) varken P362 tekil elenir
        if "P361+P364" in p_set:
            p_set.discard("P362")
        if "P362+P364" in p_set:
            p_set.discard("P362")

        # Standart Sıralama (P1xx, P2xx, P3xx, P4xx, P5xx)
        sorted_p = sorted(list(p_set), key=lambda x: (x[:2], int(x[2:5]) if x[2:5].isdigit() else 999))
        sorted_h = sorted(list(raw_h_codes))
        sorted_euh = sorted(list(raw_euh_codes))
        sorted_piktograms = sorted(list(filtered_piktogramlar))

        return {
            "siniflandirmalar": raw_hazards,
            "h_ifadeleri": sorted_h,
            "euh_ifadeleri": sorted_euh,
            "piktogramlar": sorted_piktograms,
            "uyari_kelimesi": final_warning,
            "p_ifadeleri": sorted_p,
            "precedence_audit_log": precedence_audit_log
        }

    # SEA Madde 33 / CLP Ek-II Kapsamında Özel Ambalaj Şartları Tetikleyicileri
    TACTILE_WARNING_H_CODES = {
        "H300", "H301", "H310", "H311", "H330", "H331",
        "H314", "H334", "H304",
        "H340", "H341", "H350", "H351", "H360", "H361",
        "H370", "H371", "H372", "H373",
        "H224", "H225", "H220", "H221"
    }
    CHILD_RESISTANT_H_CODES = {
        "H300", "H301", "H310", "H311", "H330", "H331",
        "H314", "H304", "H370", "H372"
    }

    @classmethod
    def generate_label(cls, decision: Any) -> Any:
        """
        Saf RegulatoryDecision nesnesini tüketerek tip-güvenli RegulatoryLabel üretir.
        """
        from app.models.regulatory import RegulatoryLabel

        raw_hazards = [h.model_dump() if hasattr(h, "model_dump") else h for h in decision.hazards]
        raw_h_codes = set(decision.h_codes)
        raw_euh_codes = set(decision.euh_codes)

        raw_pictograms: Set[str] = set()
        warning_words: List[str] = []

        for rule_res in decision.evidence_pack:
            for pic in getattr(rule_res, "piktogramlar", []):
                raw_pictograms.add(pic)
            uw = getattr(rule_res, "uyari_kelimesi", None)
            if uw:
                warning_words.append(uw)

        resolved = cls.resolve_label_elements(
            raw_hazards=raw_hazards,
            raw_h_codes=raw_h_codes,
            raw_euh_codes=raw_euh_codes,
            raw_pictograms=raw_pictograms,
            rule_warning_words=warning_words
        )

        tactile = any(h in cls.TACTILE_WARNING_H_CODES for h in raw_h_codes)
        child_res = any(h in cls.CHILD_RESISTANT_H_CODES for h in raw_h_codes)

        return RegulatoryLabel(
            signal_word=resolved["uyari_kelimesi"],
            pictograms=resolved["piktogramlar"],
            hazard_statements=resolved["h_ifadeleri"],
            supplemental_statements=resolved["euh_ifadeleri"],
            precautionary_statements=resolved["p_ifadeleri"],
            precedence_audit_log=resolved["precedence_audit_log"],
            tactile_warning_required=tactile,
            child_resistant_fastening_required=child_res
        )

