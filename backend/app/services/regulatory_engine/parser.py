"""
Zengin Regülatif Sınıflandırma Ayrıştırıcısı (Regulatory Classification Parser)
Ham metinlerden Zararlılık Sınıfı, Kategori, H-Kodu, SCL (Spesifik Konsantrasyon Sınırı)
ve M-Faktörü değerlerini ayrıştıran parser motoru.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from app.models.regulatory import HazardEntry


class RegulatoryClassificationParser:
    """
    CLP / SEA formatındaki zengin sınıflandırma metinlerini ayrıştırır.
    Örnek girdiler:
    - 'Skin Corr. 1B H314 (SCL >= 1%), Eye Dam. 1 H318 (SCL >= 3%)'
    - 'Flam. Liq. 2 H225; Repr. 1B H360FD: C >= 0.3%'
    - 'Aquatic Chronic 1 H410 (M=10), Aquatic Acute 1 H400 (M=10)'
    - 'Acute Tox. 4 H302, Skin Irrit. 2 H315'
    """

    # Bilinen SEA / GHS Zararlılık Sınıfları ve Regex Eşlemeleri
    CLASS_PATTERNS = [
        ("Skin Corr.", r"\b(?:Skin\s*Corr(?:\.|osion)?|Cilt\s*Aşın(?:\.|ması)?)\s*([1-3][A-Za-z]*)?\b"),
        ("Skin Irrit.", r"\b(?:Skin\s*Irrit(?:\.|ation)?|Cilt\s*Tahriş(?:\.|i)?)\s*([1-3][A-Za-z]*)?\b"),
        ("Eye Dam.", r"\b(?:Eye\s*Dam(?:\.|age)?|Göz\s*Hasar(?:\.|ı)?)\s*([1-3][A-Za-z]*)?\b"),
        ("Eye Irrit.", r"\b(?:Eye\s*Irrit(?:\.|ation)?|Göz\s*Tahriş(?:\.|i)?)\s*([1-3][A-Za-z]*)?\b"),
        ("Flam. Liq.", r"\b(?:Flam(?:\.|mable)?\s*Liq(?:\.|uid)?|Alev(?:\.|lenir)?\s*Sıvı)\s*([1-4])?\b"),
        ("Acute Tox.", r"\b(?:Acute\s*Tox(?:\.|icity)?|Akut\s*Toks(?:\.|isite)?)\s*([1-5])?\b"),
        ("Resp. Sens.", r"\b(?:Resp(?:\.|iratory)?\s*Sens(?:\.|itisation)?|Solunum\s*Hassas(?:\.|laşması)?)\s*([1-2][A-Za-z]*)?\b"),
        ("Skin Sens.", r"\b(?:Skin\s*Sens(?:\.|itisation)?|Cilt\s*Hassas(?:\.|laşması)?)\s*([1-2][A-Za-z]*)?\b"),
        ("Muta.", r"\b(?:Muta(?:\.|genicity)?|Mutajen(?:\.|ite)?)\s*([1-2][A-Za-z]*)?\b"),
        ("Carc.", r"\b(?:Carc(?:\.|inogenicity)?|Kanserojen(?:\.|ite)?)\s*([1-2][A-Za-z]*)?\b"),
        ("Repr.", r"\b(?:Repr(?:\.|oductive)?|Üreme(?:\s*Toks)?)\s*([1-2][A-Za-z]*)?\b"),
        ("STOT SE", r"\b(?:STOT\s*SE|BHOT\s*Tek)\s*([1-3])?\b"),
        ("STOT RE", r"\b(?:STOT\s*RE|BHOT\s*Tekrarlı)\s*([1-2])?\b"),
        ("Asp. Tox.", r"\b(?:Asp(?:\.|iration)?\s*Tox(?:\.|icity)?|Aspirasyon)\s*([1-2])?\b"),
        ("Aquatic Acute", r"\b(?:Aquatic\s*Acute|Sucul\s*Akut)\s*([1-3])?\b"),
        ("Aquatic Chronic", r"\b(?:Aquatic\s*Chronic|Sucul\s*Kronik)\s*([1-4])?\b"),
    ]

    # H-Kodları ve Varsayılan Eşleşmeleri
    H_CODE_TO_CLASS = {
        "H224": ("Flam. Liq.", "1"),
        "H225": ("Flam. Liq.", "2"),
        "H226": ("Flam. Liq.", "3"),
        "H300": ("Acute Tox.", "1"),
        "H301": ("Acute Tox.", "3"),
        "H302": ("Acute Tox.", "4"),
        "H310": ("Acute Tox.", "1"),
        "H311": ("Acute Tox.", "3"),
        "H312": ("Acute Tox.", "4"),
        "H314": ("Skin Corr.", "1"),
        "H315": ("Skin Irrit.", "2"),
        "H317": ("Skin Sens.", "1"),
        "H318": ("Eye Dam.", "1"),
        "H319": ("Eye Irrit.", "2"),
        "H330": ("Acute Tox.", "1"),
        "H331": ("Acute Tox.", "3"),
        "H332": ("Acute Tox.", "4"),
        "H334": ("Resp. Sens.", "1"),
        "H335": ("STOT SE", "3"),
        "H336": ("STOT SE", "3"),
        "H304": ("Asp. Tox.", "1"),
        "H340": ("Muta.", "CATEGORY_UNRESOLVED"),
        "H341": ("Muta.", "2"),
        "H350": ("Carc.", "CATEGORY_UNRESOLVED"),
        "H350i": ("Carc.", "CATEGORY_UNRESOLVED"),
        "H351": ("Carc.", "2"),
        "H360": ("Repr.", "CATEGORY_UNRESOLVED"),
        "H360F": ("Repr.", "CATEGORY_UNRESOLVED"),
        "H360D": ("Repr.", "CATEGORY_UNRESOLVED"),
        "H360FD": ("Repr.", "CATEGORY_UNRESOLVED"),
        "H360Fd": ("Repr.", "CATEGORY_UNRESOLVED"),
        "H360Df": ("Repr.", "CATEGORY_UNRESOLVED"),
        "H361": ("Repr.", "2"),
        "H361f": ("Repr.", "2"),
        "H361d": ("Repr.", "2"),
        "H361fd": ("Repr.", "2"),
        "H370": ("STOT SE", "1"),
        "H371": ("STOT SE", "2"),
        "H372": ("STOT RE", "1"),
        "H373": ("STOT RE", "2"),
        "H400": ("Aquatic Acute", "1"),
        "H410": ("Aquatic Chronic", "1"),
        "H411": ("Aquatic Chronic", "2"),
        "H412": ("Aquatic Chronic", "3"),
        "H413": ("Aquatic Chronic", "4"),
        "EUH066": ("EUH066", ""),
        "EUH204": ("EUH204", ""),
        "EUH208": ("EUH208", ""),
    }

    @classmethod
    def extract_scl(cls, text: str) -> Optional[float]:
        """
        Metin içindeki Spesifik Konsantrasyon Sınırını (SCL) çeker.
        Örn: 'SCL >= 1%', 'C >= 0.3%', 'SCL: 5 %', 'C >= 1.0 %', '1% <= C < 5%', 'SCL 2%'
        """
        if not text:
            return None

        # 1. '1% <= C' formatı (SEA / CLP Ek-6 aralık formatı)
        match_lower = re.search(r"(\d+(?:\.\d+)?)\s*%?\s*<=\s*C\b", text, re.IGNORECASE)
        if match_lower:
            try:
                return float(match_lower.group(1))
            except (ValueError, TypeError):
                pass

        # 2. 'SCL >= 1%', 'C >= 1%', 'SCL: 2%', 'SCL = 2%', 'SCL 2%' formatı
        match = re.search(r"(?:SCL\s*(?:>=|:|=|>|\s)|C\s*(?:>=|:|=|>))\s*(\d+(?:\.\d+)?)\s*%?", text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, TypeError):
                pass
        return None

    @classmethod
    def extract_m_factor(cls, text: str) -> Optional[float]:
        """
        Metin içindeki M-faktörünü çeker.
        Örn: 'M=10', 'M = 100', 'M_akut=10', 'M-faktörü: 10'
        """
        if not text:
            return None
        match = re.search(r"\bM(?:_akut|_kronik|\s*akut|\s*kronik)?\s*(?:=|\:)\s*(\d+(?:\.\d+)?)\b", text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, TypeError):
                pass
        return None

    @classmethod
    def _split_into_segments(cls, text: str) -> List[str]:
        """
        Parantez içindeki (örn. 'SCL >= 1%, M=10') virgülleri koruyarak
        metni ';' veya ',' ile ayrılmış segmentlere böler.
        """
        segments = []
        current = []
        paren_depth = 0

        for char in text:
            if char in "([":
                paren_depth += 1
                current.append(char)
            elif char in ")]":
                paren_depth = max(0, paren_depth - 1)
                current.append(char)
            elif (char == ";" or char == ",") and paren_depth == 0:
                seg = "".join(current).strip()
                if seg:
                    segments.append(seg)
                current = []
            else:
                current.append(char)

        if current:
            seg = "".join(current).strip()
            if seg:
                segments.append(seg)

        return segments

    @classmethod
    def parse_classification_string(cls, sinif_str: str) -> List[HazardEntry]:
        """
        Karmaşık bir sınıflandırma metnini ayrıştırarak tip güvenli HazardEntry listesi üretir.
        """
        if not sinif_str or not isinstance(sinif_str, str):
            return []

        entries: List[HazardEntry] = []
        clean_text = sinif_str.strip()
        segments = cls._split_into_segments(clean_text)

        for seg in segments:
            # Segmentteki H ve EUH kodlarını bul
            h_codes = re.findall(r"\bH[234]\d{2}[a-zA-Z]*\b", seg, re.IGNORECASE)
            euh_codes = re.findall(r"\bEUH\d{3}\b", seg, re.IGNORECASE)
            found_codes = [c.upper() for c in (h_codes + euh_codes)]

            # SCL ve M-Factor
            scl_val = cls.extract_scl(seg)
            m_factor = cls.extract_m_factor(seg)

            # Zararlılık sınıfı ve kategori tespiti
            detected_class = None
            detected_cat = ""

            for h_class, pattern in cls.CLASS_PATTERNS:
                match = re.search(pattern, seg, re.IGNORECASE)
                if match:
                    detected_class = h_class
                    detected_cat = match.group(1) or ""
                    break

            if found_codes:
                for code in found_codes:
                    # Normalize code (H361d vb.)
                    norm_code = code
                    if code.startswith("H361") and len(code) == 5:
                        norm_code = "H361" + code[4].lower()
                    elif code.startswith("H360") and len(code) > 4:
                        norm_code = "H360" + code[4:]

                    # Eğer class tespit edilmediyse varsayılan tablodan al
                    h_cls = detected_class or cls.H_CODE_TO_CLASS.get(norm_code, ("Genel", ""))[0]
                    h_cat = detected_cat or cls.H_CODE_TO_CLASS.get(norm_code, ("", ""))[1]

                    # REG-008: CMR 1A / 1B ayrımı
                    # H340, H350, H360 gibi kodlar kendi başlarına 1A/1B ayrımını taşımazlar.
                    # Girdi metninde açıkça '1A' veya '1B' belirtilmemişse kategori CATEGORY_UNRESOLVED olmalıdır.
                    if norm_code in ["H350", "H340", "H350i"] or norm_code.startswith("H360"):
                        if "1A" in seg.upper():
                            h_cat = "1A"
                        elif "1B" in seg.upper():
                            h_cat = "1B"
                        elif detected_cat in ["1A", "1B"]:
                            h_cat = detected_cat
                        else:
                            h_cat = "CATEGORY_UNRESOLVED"
                    elif norm_code == "H314":
                        if "1A" in seg.upper():
                            h_cat = "1A"
                        elif "1B" in seg.upper():
                            h_cat = "1B"
                        elif "1C" in seg.upper():
                            h_cat = "1C"

                    is_euh066 = (norm_code == "EUH066" or "EUH066" in seg.upper())
                    entries.append(HazardEntry(
                        hazard_class=h_cls,
                        category=h_cat,
                        h_code=norm_code,
                        scl=scl_val,
                        m_factor_acute=m_factor if "Acute" in h_cls or norm_code == "H400" else None,
                        m_factor_chronic=m_factor if "Chronic" in h_cls or norm_code == "H410" else None,
                        has_euh066=is_euh066,
                        euh066_source="explicit_code" if is_euh066 else None
                    ))
            elif detected_class:
                # H-kodu olmasa dahi sınıflandırma metni girilmişse (örn. 'Skin Corr. 1B', 'Carc. 1')
                cat = detected_cat
                if detected_class in ["Carc.", "Muta.", "Repr."] and cat in ["1", ""]:
                    cat = "CATEGORY_UNRESOLVED"
                entries.append(HazardEntry(
                    hazard_class=detected_class,
                    category=cat,
                    h_code="",
                    scl=scl_val
                ))

        return entries
