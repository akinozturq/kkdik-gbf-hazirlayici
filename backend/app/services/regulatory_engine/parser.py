"""
Zengin Regülatif Sınıflandırma Ayrıştırıcısı ve Doğrulama Motoru (Regulatory Classification Parser & Validator)

Mimari Akış (Pipeline):
  1. raw text (Ham girdi metni)
        ↓
  2. parsed assertion (Doğrudan metin iddiası - ParsedHazardAssertion)
        ↓
  3. normalized regulatory data (Standartlaştırılmış mevzuat verisi - NormalizedHazard)
        ↓
  4. validated regulatory data (Denetlenmiş ve doğrulanmış veri - ValidatedHazard)
        ↓
  5. classification engine (Karışım sınıflandırma motoru - HazardEntry / StructuredSubstance)
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Set
from app.models.regulatory import (
    HazardEntry,
    STOTSE3Effect,
    ParsedHazardAssertion,
    NormalizedHazard,
    ValidatedHazard,
    ValidationIssue
)


class RegulatoryClassificationParser:
    """
    CLP / SEA formatındaki zengin sınıflandırma metinlerini çok aşamalı
    güvenli bir mimariyle ayrıştırır, normalize eder ve doğrular.
    """

    # Bilinen SEA / GHS Zararlılık Sınıfları ve Regex Eşlemeleri
    CLASS_PATTERNS: List[Tuple[str, str]] = [
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

    # H-Kodları ve Varsayılan Kanonik Sınıflandırma Eşleşmeleri
    H_CODE_TO_CLASS: Dict[str, Tuple[str, str]] = {
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

    # Sınıf Bazında İzin Verilen Kategori Kümeleri (SEA Ek-1)
    VALID_CATEGORIES_PER_CLASS: Dict[str, Set[str]] = {
        "Skin Corr.": {"1", "1A", "1B", "1C"},
        "Skin Irrit.": {"2"},
        "Eye Dam.": {"1"},
        "Eye Irrit.": {"2"},
        "Flam. Liq.": {"1", "2", "3"},
        "Acute Tox.": {"1", "2", "3", "4", "5"},
        "Resp. Sens.": {"1", "1A", "1B"},
        "Skin Sens.": {"1", "1A", "1B"},
        "Muta.": {"1A", "1B", "2", "CATEGORY_UNRESOLVED"},
        "Carc.": {"1A", "1B", "2", "CATEGORY_UNRESOLVED"},
        "Repr.": {"1A", "1B", "2", "CATEGORY_UNRESOLVED"},
        "STOT SE": {"1", "2", "3"},
        "STOT RE": {"1", "2"},
        "Asp. Tox.": {"1"},
        "Aquatic Acute": {"1"},
        "Aquatic Chronic": {"1", "2", "3", "4"},
        "EUH066": {""},
        "EUH204": {""},
        "EUH208": {""},
    }

    # SCL Uygulanabilir Zararlılık Sınıfları (SEA / CLP Ek-1)
    SCL_APPLICABLE_CLASSES: Set[str] = {
        "Skin Corr.", "Skin Irrit.", "Eye Dam.", "Eye Irrit.",
        "Resp. Sens.", "Skin Sens.", "Muta.", "Carc.", "Repr.",
        "STOT SE", "STOT RE", "Aquatic Acute", "Aquatic Chronic"
    }

    # M-Faktörü Uygulanabilir Zararlılık Sınıfları
    M_FACTOR_APPLICABLE_CLASSES: Set[str] = {
        "Aquatic Acute", "Aquatic Chronic"
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

    # =========================================================================
    # AŞAMA 1 → AŞAMA 2: Ham Metin ➔ Ayrıştırılmış İddia (Parsed Assertion)
    # =========================================================================
    @classmethod
    def parse_assertions(cls, raw_text: str) -> List[ParsedHazardAssertion]:
        """
        Ham metni segmentlere bölerek metnin içerdiği doğrudan iddiaları (assertions) çıkarır.
        Mevzuat geçerliliği veya doğruluğu varsayımı yapmaz; yazarın ne yazdığını kayıt altına alır.
        """
        if not raw_text or not isinstance(raw_text, str):
            return []

        clean_text = raw_text.strip()
        segments = cls._split_into_segments(clean_text)
        assertions: List[ParsedHazardAssertion] = []

        for seg in segments:
            # H ve EUH kodlarını tespit et
            h_codes = re.findall(r"\bH[234]\d{2}[a-zA-Z]*\b", seg, re.IGNORECASE)
            euh_codes = re.findall(r"\bEUH\d{3}\b", seg, re.IGNORECASE)
            found_codes = [c.upper() for c in (h_codes + euh_codes)]

            # SCL ve M-Factor çek
            scl_val = cls.extract_scl(seg)
            m_factor = cls.extract_m_factor(seg)

            # Sınıf ve Kategori çek
            detected_class = None
            detected_cat = None
            for h_class, pattern in cls.CLASS_PATTERNS:
                match = re.search(pattern, seg, re.IGNORECASE)
                if match:
                    detected_class = h_class
                    detected_cat = match.group(1) or None
                    break

            has_euh066 = ("EUH066" in found_codes or "EUH066" in seg.upper())
            notes = []
            if len(found_codes) > 1:
                notes.append(f"Segmentte birden fazla ({len(found_codes)}) kod tespit edildi.")

            assertions.append(ParsedHazardAssertion(
                raw_text=seg,
                asserted_class=detected_class,
                asserted_category=detected_cat,
                asserted_codes=found_codes,
                asserted_scl=scl_val,
                asserted_m_factor=m_factor,
                has_euh066=has_euh066,
                parsing_notes=notes
            ))

        return assertions

    # =========================================================================
    # AŞAMA 2 → AŞAMA 3: İddia ➔ Standartlaştırılmış Regülatif Veri (Normalized)
    # =========================================================================
    @classmethod
    def normalize_assertion(cls, assertion: ParsedHazardAssertion) -> List[NormalizedHazard]:
        """
        Ham iddiayı (ParsedHazardAssertion) kanonik CLP / SEA terminolojisine dönüştürür.
        Yazım hataları, Türkçe varyantlar, alt-kod casing standardizasyonu ve
        kategori belirsizliklerini (CMR 1A/1B) çözümler.
        """
        normalized_list: List[NormalizedHazard] = []
        codes = assertion.asserted_codes
        seg_upper = assertion.raw_text.upper()

        if codes:
            for code in codes:
                norm_code = code
                if code.startswith("H361") and len(code) == 5:
                    norm_code = "H361" + code[4].lower()
                elif code.startswith("H360") and len(code) > 4:
                    norm_code = "H360" + code[4:]

                # Sınıf çözümleme (İddia edilen sınıf varsa onu kullan, yoksa H-kodundan çıkarsa)
                notes = []
                if assertion.asserted_class:
                    canonical_class = assertion.asserted_class
                else:
                    canonical_class = cls.H_CODE_TO_CLASS.get(norm_code, ("Genel", ""))[0]
                    notes.append(f"Zararlılık sınıfı belirtilmemiş; '{norm_code}' kodundan '{canonical_class}' olarak çıkarsandı.")

                # Kategori çözümleme
                canonical_cat = assertion.asserted_category or cls.H_CODE_TO_CLASS.get(norm_code, ("", ""))[1]

                # REG-008: CMR 1A / 1B ayrımı
                # H340, H350, H360 gibi kodlar tek başlarına 1A/1B ayrımını taşımazlar.
                if norm_code in ["H350", "H340", "H350i"] or norm_code.startswith("H360"):
                    if "1A" in seg_upper:
                        canonical_cat = "1A"
                    elif "1B" in seg_upper:
                        canonical_cat = "1B"
                    elif assertion.asserted_category in ["1A", "1B"]:
                        canonical_cat = assertion.asserted_category
                    else:
                        canonical_cat = "CATEGORY_UNRESOLVED"
                        notes.append("CMR 1A/1B kategori ayrımı netleştirilmedi, CATEGORY_UNRESOLVED olarak normalize edildi.")
                elif norm_code == "H314":
                    if "1A" in seg_upper:
                        canonical_cat = "1A"
                    elif "1B" in seg_upper:
                        canonical_cat = "1B"
                    elif "1C" in seg_upper:
                        canonical_cat = "1C"
                    elif assertion.asserted_category:
                        canonical_cat = assertion.asserted_category
                    else:
                        canonical_cat = "1"

                is_euh066 = (norm_code == "EUH066" or assertion.has_euh066)
                euh_src = "explicit_code" if is_euh066 else None

                normalized_list.append(NormalizedHazard(
                    raw_assertion=assertion,
                    canonical_class=canonical_class,
                    canonical_category=canonical_cat,
                    canonical_code=norm_code,
                    scl=assertion.asserted_scl,
                    m_factor=assertion.asserted_m_factor,
                    has_euh066=is_euh066,
                    euh066_source=euh_src,
                    normalization_notes=notes
                ))
        elif assertion.asserted_class:
            # H-kodu olmasa dahi sınıflandırma metni girilmişse (örn. 'Skin Corr. 1B', 'Carc. 1')
            cat = assertion.asserted_category or ""
            notes = []
            if assertion.asserted_class in ["Carc.", "Muta.", "Repr."] and cat in ["1", ""]:
                cat = "CATEGORY_UNRESOLVED"
                notes.append("CMR Kategori 1 için 1A / 1B ayrımı yapılmadı, CATEGORY_UNRESOLVED atandı.")

            normalized_list.append(NormalizedHazard(
                raw_assertion=assertion,
                canonical_class=assertion.asserted_class,
                canonical_category=cat,
                canonical_code="",
                scl=assertion.asserted_scl,
                m_factor=assertion.asserted_m_factor,
                has_euh066=assertion.has_euh066,
                normalization_notes=notes
            ))

        return normalized_list

    # =========================================================================
    # AŞAMA 3 → AŞAMA 4: Standart Veri ➔ Doğrulanmış Regülatif Veri (Validated)
    # =========================================================================
    @classmethod
    def validate_normalized(cls, normalized: NormalizedHazard) -> ValidatedHazard:
        """
        Normalize edilmiş regülatif veriyi CLP / SEA mevzuat kurallarına göre denetler.
        Çelişkileri, geçersiz sayısal sınırları (SCL, M-faktörü), uyumsuz kategorileri
        ve belirsizlikleri tespit ederek ValidatedHazard nesnesi üretir.
        """
        issues: List[ValidationIssue] = []
        status = "VALID"
        is_applicable = True

        h_code = normalized.canonical_code
        h_class = normalized.canonical_class
        h_cat = normalized.canonical_category

        # 1. H-Kodu vs Zararlılık Sınıfı Çelişki Denetimi (Cross-Consistency Check)
        if h_code and h_code in cls.H_CODE_TO_CLASS:
            expected_class, expected_cat = cls.H_CODE_TO_CLASS[h_code]
            if normalized.raw_assertion.asserted_class is not None:
                # Kullanıcı açıkça bir sınıf iddia etmiş ve bu sınıf H-kodunun gerçek sınıfıyla uyuşmuyor mu?
                if expected_class != "Genel" and h_class != expected_class:
                    issues.append(ValidationIssue(
                        code="CLASS_CODE_MISMATCH",
                        severity="ERROR",
                        message=f"Çelişki: '{h_code}' H-kodu '{expected_class}' sınıfına aittir; "
                                f"metinde iddia edilen '{h_class}' sınıfı ile uyuşmamaktadır."
                    ))
                    status = "CONTRADICTORY"

        # 2. Kategori Geçerlilik Denetimi
        if h_class in cls.VALID_CATEGORIES_PER_CLASS:
            valid_cats = cls.VALID_CATEGORIES_PER_CLASS[h_class]
            if h_cat and h_cat not in valid_cats:
                issues.append(ValidationIssue(
                    code="INVALID_CATEGORY",
                    severity="ERROR",
                    message=f"'{h_class}' sınıfı için '{h_cat}' geçerli bir kategori değildir "
                            f"(İzin verilenler: {', '.join(sorted(valid_cats))})."
                ))
                if status != "CONTRADICTORY":
                    status = "CONTRADICTORY"

        # 3. SCL Sınır ve Uygulanabilirlik Denetimi
        if normalized.scl is not None:
            if normalized.scl <= 0.0 or normalized.scl > 100.0:
                issues.append(ValidationIssue(
                    code="INVALID_SCL_BOUNDS",
                    severity="ERROR",
                    message=f"SCL değeri %0 ile %100 arasında olmalıdır (Tespit edilen: %{normalized.scl})."
                ))
                status = "INVALID"
                is_applicable = False
            elif h_class not in cls.SCL_APPLICABLE_CLASSES:
                issues.append(ValidationIssue(
                    code="INAPPLICABLE_SCL",
                    severity="WARNING",
                    message=f"'{h_class}' sınıfı için CLP / SEA uyarınca SCL uygulanamaz."
                ))
                if status == "VALID":
                    status = "CORRECTED"

        # 4. M-Faktörü Sınır ve Uygulanabilirlik Denetimi
        if normalized.m_factor is not None:
            if normalized.m_factor < 1.0:
                issues.append(ValidationIssue(
                    code="INVALID_M_FACTOR",
                    severity="ERROR",
                    message=f"M-faktörü en az 1.0 olmalıdır (Tespit edilen: {normalized.m_factor})."
                ))
                status = "INVALID"
                is_applicable = False
            elif h_class not in cls.M_FACTOR_APPLICABLE_CLASSES and h_code not in ("H400", "H410"):
                issues.append(ValidationIssue(
                    code="INAPPLICABLE_M_FACTOR",
                    severity="WARNING",
                    message=f"M-faktörü yalnızca Sucul Akut 1 ve Sucul Kronik 1 için geçerlidir; "
                            f"'{h_class}' sınıfı için uygulanamaz."
                ))
                if status == "VALID":
                    status = "CORRECTED"

        # 5. CMR Kategori Belirsizlik Denetimi (REG-008)
        if h_cat == "CATEGORY_UNRESOLVED":
            issues.append(ValidationIssue(
                code="CMR_CATEGORY_UNRESOLVED",
                severity="WARNING",
                message=f"CMR zararlılığı ({h_class} {h_code}) için 1A veya 1B kategori ayrımı netleştirilmemiştir."
            ))
            if status == "VALID":
                status = "UNRESOLVED"

        # 6. Çıkarsanan Sınıf Bilgisi (Inferred Class Info)
        if normalized.raw_assertion.asserted_class is None and h_code:
            issues.append(ValidationIssue(
                code="INFERRED_CLASS",
                severity="INFO",
                message=f"Zararlılık sınıfı metinde açıkça yazılmamış; '{h_code}' H-kodundan '{h_class}' olarak çözümlendi."
            ))
            if status == "VALID":
                status = "CORRECTED"

        return ValidatedHazard(
            normalized=normalized,
            status=status,
            issues=issues,
            is_applicable_for_classification=is_applicable
        )

    # =========================================================================
    # TÜM AŞAMALARI İCRA EDEN BORU HATTI
    # =========================================================================
    @classmethod
    def process_to_validated_hazards(cls, raw_text: str) -> List[ValidatedHazard]:
        """
        raw text ➔ parsed assertions ➔ normalized data ➔ validated data zincirini icra eder.
        """
        if not raw_text or not isinstance(raw_text, str):
            return []

        assertions = cls.parse_assertions(raw_text)
        validated_hazards: List[ValidatedHazard] = []

        for assertion in assertions:
            normalized_list = cls.normalize_assertion(assertion)
            for normalized in normalized_list:
                validated = cls.validate_normalized(normalized)
                validated_hazards.append(validated)

        return validated_hazards

    @classmethod
    def parse_classification_string(cls, sinif_str: str) -> List[HazardEntry]:
        """
        Geriye dönük tam uyumlu cephe metodu (Facade Pattern).
        Çok aşamalı boru hattını çalıştırır ve nihai tip güvenli HazardEntry listesi üretir.
        """
        validated = cls.process_to_validated_hazards(sinif_str)
        return [v.to_hazard_entry() for v in validated]
