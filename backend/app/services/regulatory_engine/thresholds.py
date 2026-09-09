"""
CLP / SEA Eşik ve Kesme Değerleri Sağlayıcısı (Regulatory Threshold Provider)
SEA Ek-1 Tablo 1.1, Tablo 3.2.3, Tablo 3.3.3 uyarınca Cut-off, GCL ve SCL yönetimini sağlar.
"""

from typing import Optional, Dict, Any
from app.models.regulatory import HazardThreshold


class RegulatoryThresholdProvider:
    """
    SEA / CLP standart kesme (cut-off) ve genel konsantrasyon sınırları (GCL)
    sağlayıcısı ve Spesifik Konsantrasyon Sınırı (SCL) birleştiricisi.
    """

    DEFAULT_THRESHOLDS: Dict[str, Dict[str, Any]] = {
        "SKIN_CORR_1": {
            "hazard_class": "Skin Corr.",
            "category": "1",
            "h_code": "H314",
            "cut_off": 1.0,
            "gcl": 5.0,
        },
        "SKIN_CORR_1A": {
            "hazard_class": "Skin Corr.",
            "category": "1A",
            "h_code": "H314",
            "cut_off": 1.0,
            "gcl": 5.0,
        },
        "SKIN_CORR_1B": {
            "hazard_class": "Skin Corr.",
            "category": "1B",
            "h_code": "H314",
            "cut_off": 1.0,
            "gcl": 5.0,
        },
        "SKIN_CORR_1C": {
            "hazard_class": "Skin Corr.",
            "category": "1C",
            "h_code": "H314",
            "cut_off": 1.0,
            "gcl": 5.0,
        },
        "SKIN_IRRIT_2": {
            "hazard_class": "Skin Irrit.",
            "category": "2",
            "h_code": "H315",
            "cut_off": 1.0,
            "gcl": 10.0,
        },
        "EYE_DAM_1": {
            "hazard_class": "Eye Dam.",
            "category": "1",
            "h_code": "H318",
            "cut_off": 1.0,
            "gcl": 3.0,
        },
        "EYE_IRRIT_2": {
            "hazard_class": "Eye Irrit.",
            "category": "2",
            "h_code": "H319",
            "cut_off": 1.0,
            "gcl": 10.0,
        },
    }

    @classmethod
    def get_skin_corr_threshold(cls, scl: Optional[float] = None, category: str = "1") -> HazardThreshold:
        norm_cat = category.upper().replace("KATEGORI", "").replace("KAT", "").strip() if category else "1"
        key = f"SKIN_CORR_{norm_cat}"
        base = cls.DEFAULT_THRESHOLDS.get(key, cls.DEFAULT_THRESHOLDS["SKIN_CORR_1"])
        return HazardThreshold(
            hazard_class=base["hazard_class"],
            category=base["category"],
            h_code=base["h_code"],
            cut_off=base["cut_off"],
            gcl=base["gcl"],
            scl=scl,
        )

    @classmethod
    def get_skin_irrit_threshold(cls, scl: Optional[float] = None) -> HazardThreshold:
        base = cls.DEFAULT_THRESHOLDS["SKIN_IRRIT_2"]
        return HazardThreshold(
            hazard_class=base["hazard_class"],
            category=base["category"],
            h_code=base["h_code"],
            cut_off=base["cut_off"],
            gcl=base["gcl"],
            scl=scl,
        )

    @classmethod
    def get_eye_dam_threshold(cls, scl: Optional[float] = None) -> HazardThreshold:
        base = cls.DEFAULT_THRESHOLDS["EYE_DAM_1"]
        return HazardThreshold(
            hazard_class=base["hazard_class"],
            category=base["category"],
            h_code=base["h_code"],
            cut_off=base["cut_off"],
            gcl=base["gcl"],
            scl=scl,
        )

    @classmethod
    def get_eye_irrit_threshold(cls, scl: Optional[float] = None) -> HazardThreshold:
        base = cls.DEFAULT_THRESHOLDS["EYE_IRRIT_2"]
        return HazardThreshold(
            hazard_class=base["hazard_class"],
            category=base["category"],
            h_code=base["h_code"],
            cut_off=base["cut_off"],
            gcl=base["gcl"],
            scl=scl,
        )

    @classmethod
    def get_threshold_by_code(cls, h_code: str, scl: Optional[float] = None) -> Optional[HazardThreshold]:
        code = h_code.strip().upper()
        if code == "H314":
            return cls.get_skin_corr_threshold(scl=scl)
        elif code == "H315":
            return cls.get_skin_irrit_threshold(scl=scl)
        elif code == "H318":
            return cls.get_eye_dam_threshold(scl=scl)
        elif code == "H319":
            return cls.get_eye_irrit_threshold(scl=scl)
        return None
