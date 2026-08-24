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

    @classmethod
    def _load_p_map(cls):
        if cls._H_TO_P_MAP is None and os.path.exists(H_TO_P_PATH):
            with open(H_TO_P_PATH, "r", encoding="utf-8") as f:
                cls._H_TO_P_MAP = json.load(f)

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

        # 2. GHS PİKTOGRAM ÖNCELİK VE ELEME KURALLARI (SEA Madde 26 & 28)
        filtered_piktogramlar = set(raw_pictograms)

        # Kural A: GHS06 (Kafatası) varsa, GHS07 (Ünlem) yalnızca akut toksisite nedeniyle verildiyse elenir.
        # Eğer GHS07 cilt tahrişi (H315), göz tahrişi (H319) veya STOT SE 3 (H335/H336) kaynaklıysa KORUNUR.
        if "GHS06" in filtered_piktogramlar:
            ghs07_exceptions = {"H315", "H319", "H317", "H335", "H336"}
            if not any(c in raw_h_codes for c in ghs07_exceptions):
                filtered_piktogramlar.discard("GHS07")

        # Kural B: GHS05 (Aşındırıcı - Cilt/Göz) varsa, cilt veya göz tahrişinden gelen GHS07 elenir.
        if "GHS05" in filtered_piktogramlar:
            ghs07_non_skin_eye = {"H302", "H312", "H332", "H317", "H335", "H336"}
            if not any(c in raw_h_codes for c in ghs07_non_skin_eye):
                filtered_piktogramlar.discard("GHS07")

        # Kural C: GHS08 (Sağlık Zararı - Solunum Hassaslaşması) varsa, cilt hassaslaşmasından (H317) gelen GHS07 elenir.
        if "GHS08" in filtered_piktogramlar and "H334" in raw_h_codes:
            ghs07_other = {"H302", "H312", "H332", "H315", "H319", "H335", "H336"}
            if not any(c in raw_h_codes for c in ghs07_other):
                filtered_piktogramlar.discard("GHS07")

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
            "p_ifadeleri": sorted_p
        }
