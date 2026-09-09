"""
Regülatif Sınıflandırma Boru Hattı (Regulatory Engine Pipeline)
"""

import re
from typing import List, Dict, Any, Optional, Set, Literal
from app.models.regulatory import (
    ConcentrationValue,
    HazardEntry,
    InhalationExposure,
    StructuredSubstance,
    CalculationContext,
    ClassificationResult,
    RuleResult,
    ClassifiedHazard
)
from app.services.rules import (
    BaseHazardRule,
    FlammableLiquidRule,
    AspirationHazardRule,
    AcuteToxicityRule,
    SkinEyeRule,
    SensitizationRule,
    STOTRule,
    CMRRule,
    AquaticRule,
    SupplementalHazardRule
)
from app.services.regulatory_engine.label_generator import LabelGenerator


class RegulatoryPipeline:
    """
    Tüm kural stratejilerini yöneten ve karışım sınıflandırma boru hattını
    (Pipeline Pattern) icra eden ana orkestratör sınıf.
    """

    def __init__(self, custom_rules: Optional[List[BaseHazardRule]] = None):
        self.rules: List[BaseHazardRule] = custom_rules or [
            FlammableLiquidRule(),
            SkinEyeRule(),
            SensitizationRule(),
            AspirationHazardRule(),
            STOTRule(),
            CMRRule(),
            AquaticRule(),
            SupplementalHazardRule(),
            AcuteToxicityRule()
        ]

    @classmethod
    def parse_concentration_model(cls, conc_str: Any) -> ConcentrationValue:
        """
        Ham konsantrasyon metnini nitelikli ConcentrationValue nesnesine dönüştürür.
        """
        if isinstance(conc_str, (int, float)):
            return ConcentrationValue(value=float(conc_str), qualifier="exact", raw_text=str(conc_str))
        if not conc_str or not isinstance(conc_str, str):
            return ConcentrationValue(value=0.0, qualifier="exact", raw_text="")

        clean = conc_str.replace("%", "").replace(",", ".").strip()
        is_strict_less = bool(re.search(r"<\s*(\d+(?:\.\d+)?)", clean) and "<=" not in clean)
        is_greater = bool(">" in clean or ">=" in clean)

        # Aralık kontrolü (örn. "10 - 25")
        range_match = re.findall(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", clean)
        if range_match:
            try:
                min_v = float(range_match[0][0])
                max_v = float(range_match[0][1])
                return ConcentrationValue(
                    value=max_v,
                    min_val=min_v,
                    max_val=max_v,
                    qualifier="range",
                    raw_text=conc_str
                )
            except (ValueError, TypeError):
                pass

        # Tekil sayı kontrolü
        num_matches = re.findall(r"\d+(?:\.\d+)?", clean)
        if num_matches:
            try:
                val = float(num_matches[-1])
                if is_strict_less:
                    return ConcentrationValue(
                        value=max(0.0, val - 0.0001),
                        max_val=val,
                        qualifier="less_than",
                        raw_text=conc_str
                    )
                qual = "greater_than" if is_greater else "exact"
                return ConcentrationValue(value=val, qualifier=qual, raw_text=conc_str)
            except (ValueError, TypeError):
                pass

        return ConcentrationValue(value=0.0, qualifier="exact", raw_text=conc_str)

    @classmethod
    def parse_float_safe(cls, val: Any, default: Optional[float] = None) -> Optional[float]:
        if val is None or val == "":
            return default
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            clean = val.replace(",", ".").strip()
            matches = re.findall(r"[-+]?\d+(?:\.\d+)?", clean)
            if matches:
                try:
                    return float(matches[0])
                except (ValueError, TypeError):
                    pass
        return default

    @classmethod
    def extract_h_codes(cls, text: str) -> List[str]:
        if not text:
            return []
        h_codes = re.findall(r"\bH[234]\d{2}[a-zA-Z]*\b", text, re.IGNORECASE)
        euh_codes = re.findall(r"\bEUH\d{3}\b", text, re.IGNORECASE)
        all_codes = [c.upper() for c in (h_codes + euh_codes)]
        normalized = []
        for c in all_codes:
            if c.startswith("H361") and len(c) == 5:
                normalized.append("H361" + c[4].lower())
            elif c.startswith("H360") and len(c) > 4:
                normalized.append("H360" + c[4:])
            else:
                normalized.append(c)
        return list(dict.fromkeys(normalized))

    @classmethod
    def adapt_raw_components(cls, raw_bilesenler: List[Dict[str, Any]]) -> List[StructuredSubstance]:
        """
        Bölüm 3.2 ham dict listesini yapılandırılmış StructuredSubstance listesine dönüştürür.
        Zengin sınıflandırma metinlerini RegulatoryClassificationParser ile ayrıştırır.
        """
        from app.services.regulatory_engine.parser import RegulatoryClassificationParser
        substances: List[StructuredSubstance] = []
        for comp in raw_bilesenler:
            name = comp.get("ad") or "Bileşen"
            conc_model = cls.parse_concentration_model(comp.get("konsantrasyon"))
            sinif_str = comp.get("siniflandirma") or ""

            # Yapılandırılmış Zararlılık Profilleri (SCL, M-Factor, Category dahil)
            parsed_hazards = RegulatoryClassificationParser.parse_classification_string(sinif_str)
            codes = [h.h_code for h in parsed_hazards if h.h_code]
            if not codes:
                codes = cls.extract_h_codes(sinif_str)

            # SCL açıkça comp dict içinde verilmişse ez
            explicit_scl = cls.parse_float_safe(comp.get("scl"))
            if explicit_scl is not None:
                for h in parsed_hazards:
                    if h.scl is None:
                        h.scl = explicit_scl

            # Akut toksisite & soluma
            ate_oral = cls.parse_float_safe(comp.get("akut_toksisite_oral"))
            ate_dermal = cls.parse_float_safe(comp.get("akut_toksisite_dermal"))
            ate_inhal = cls.parse_float_safe(comp.get("akut_toksisite_soluma"))
            inhal_form = (comp.get("akut_toksisite_soluma_formu") or "buhar").lower()

            inhal_model = None
            if ate_inhal is not None or any(h in codes for h in ["H330", "H331", "H332"]):
                inhal_model = InhalationExposure(
                    ate_val=ate_inhal,
                    form="gaz" if inhal_form == "gaz" else ("toz_sis" if inhal_form in ["toz_sis", "toz", "sis"] else "buhar"),
                    unit="ppmV" if inhal_form == "gaz" else "mg/L"
                )

            # İzosiyanat & M-faktörü
            is_iso = bool(
                comp.get("is_isocyanate") or
                any(x in name.lower() or x in sinif_str.lower() for x in ["izosiyanat", "isocyanate", "mdi", "tdi", "hdi", "ipdi"])
            )
            m_akut = cls.parse_float_safe(comp.get("m_faktoru_akut"))
            m_kronik = cls.parse_float_safe(comp.get("m_faktoru_kronik"))

            # Parsed hazard içinden M-factor desteği
            if m_akut is None:
                for h in parsed_hazards:
                    if h.m_factor_acute is not None:
                        m_akut = h.m_factor_acute
                        break
            if m_kronik is None:
                for h in parsed_hazards:
                    if h.m_factor_chronic is not None:
                        m_kronik = h.m_factor_chronic
                        break

            substances.append(StructuredSubstance(
                name=name,
                cas_no=comp.get("cas_no"),
                ec_no=comp.get("ec_no"),
                concentration=conc_model,
                hazards=parsed_hazards,
                raw_h_codes=codes,
                ate_oral=ate_oral,
                ate_dermal=ate_dermal,
                inhalation=inhal_model,
                is_isocyanate=is_iso,
                m_factor_acute=m_akut,
                m_factor_chronic=m_kronik
            ))

        return substances

    @classmethod
    def project_substances(
        cls,
        substances: List[StructuredSubstance],
        bound: Literal["min", "max", "nominal"]
    ) -> List[StructuredSubstance]:
        """
        Bileşenlerin konsantrasyonlarını alt sınıra ('min'), üst sınıra ('max') veya
        nominal değere göre projeksiyonlar.
        """
        projected = []
        for s in substances:
            c = s.concentration
            if bound == "min":
                if c.qualifier == "range":
                    val = c.min_val if c.min_val is not None else c.value
                elif c.qualifier == "less_than":
                    val = 0.0
                elif c.qualifier == "greater_than":
                    val = c.value
                else:
                    val = c.value
            elif bound == "max":
                if c.qualifier == "range":
                    val = c.max_val if c.max_val is not None else c.value
                elif c.qualifier == "less_than":
                    val = c.value
                elif c.qualifier == "greater_than":
                    val = 100.0
                else:
                    val = c.value
            else:
                val = c.value

            new_conc = ConcentrationValue(
                value=float(val),
                min_val=c.min_val,
                max_val=c.max_val,
                qualifier=c.qualifier,
                raw_text=c.raw_text
            )
            sub_copy = s.model_copy(deep=True)
            sub_copy.concentration = new_conc
            projected.append(sub_copy)
        return projected

    def execute(
        self,
        substances: List[StructuredSubstance],
        context: CalculationContext
    ) -> ClassificationResult:
        """
        Boru hattındaki tüm kural stratejilerini sırayla çalıştırır ve
        etiket elemanlarını çözümleyerek ClassificationResult üretir.
        Konsantrasyon aralıklarını (min vs max) çift yönlü değerlendirerek
        DEFINITELY_TRUE, DEFINITELY_FALSE ve INDETERMINATE durumlarını belirler.
        """
        if not substances:
            return ClassificationResult(
                siniflandirmalar=[],
                h_ifadeleri=[],
                euh_ifadeleri=[],
                piktogramlar=[],
                uyari_kelimesi="Yok",
                p_ifadeleri=[],
                calculation_steps=["Karışım tablosunda (Bölüm 3.2) bileşen bulunamadı."],
                rule_results=[]
            )

        has_ranges = any(s.concentration.qualifier in ("range", "less_than") for s in substances)
        substances_max = self.project_substances(substances, "max")
        substances_min = self.project_substances(substances, "min")

        all_hazards: List[Dict[str, Any]] = []
        all_h_codes: Set[str] = set()
        all_euh_codes: Set[str] = set()
        all_pictograms: Set[str] = set()
        warning_words: List[str] = []
        calculation_steps: List[str] = []
        rule_results: List[RuleResult] = []
        indeterminate_hazards: List[Dict[str, Any]] = []

        # Bileşen Özeti Başlığı
        calculation_steps.append("📋 GİRDİ BİLEŞENLERİ VE KONSANTRASYONLARI:")
        for s in substances:
            codes_str = ", ".join(s.raw_h_codes) if s.raw_h_codes else "Sınıflandırma yok"
            if s.concentration.qualifier == "range":
                conc_display = f"%{s.concentration.min_val:g} - %{s.concentration.max_val:g} (Aralık)"
            elif s.concentration.qualifier == "less_than":
                conc_display = f"<%{s.concentration.value:g}"
            else:
                conc_display = f"%{s.concentration.value:g}"
            calculation_steps.append(f"• {s.name} ({conc_display}): {codes_str}")

        if has_ranges:
            calculation_steps.append("\n🔍 KONSANTRASYON ARALIĞI ÇİFT YÖNLÜ DENETİMİ (MIN / MAX BOUND CHECK):")
            calculation_steps.append("• Reçetede konsantrasyon aralığı tespit edildi. ECHA karışım rehberine uygun olarak kurallar hem minimum (en iyi durum) hem maksimum (en kötü durum) senaryolarıyla karşılaştırmalı değerlendirildi.")

        calculation_steps.append("\n⚖️ SEA EK-1 TOPLANABİLİRLİK VE EŞİK DEĞER DEĞERLENDİRMESİ:")

        # Kuralları İcra Et
        for rule in self.rules:
            # 1. Üst sınır değerlendirmesi (Worst-case)
            res_max: RuleResult = rule.evaluate(context, substances_max)

            # 2. Alt sınır değerlendirmesi (Best-case)
            if has_ranges:
                res_min: RuleResult = rule.evaluate(context, substances_min)
                min_keys = {(h.zararlilik_sinifi, h.kategori, h.h_kodu) for h in res_min.hazards}
            else:
                min_keys = {(h.zararlilik_sinifi, h.kategori, h.h_kodu) for h in res_max.hazards}

            evaluated_hazards: List[ClassifiedHazard] = []
            has_rule_indeterminate = False

            for h in res_max.hazards:
                key = (h.zararlilik_sinifi, h.kategori, h.h_kodu)
                if key in min_keys:
                    h_status = "DEFINITELY_TRUE"
                    status_lbl = "Kesin"
                    range_det = None
                else:
                    h_status = "INDETERMINATE"
                    status_lbl = "Belirsiz (Aralık Eşiği)"
                    range_det = "Konsantrasyon aralığı eşik değeri kapsıyor; minimum konsantrasyonda eşik aşılmazken maksimum konsantrasyonda aşılmaktadır."
                    has_rule_indeterminate = True
                    indeterminate_hazards.append({
                        "zararlilik_sinifi": h.zararlilik_sinifi,
                        "kategori": h.kategori,
                        "h_kodu": h.h_kodu,
                        "rule_name": rule.rule_name,
                        "details": range_det
                    })

                classified_h = ClassifiedHazard(
                    zararlilik_sinifi=h.zararlilik_sinifi,
                    kategori=h.kategori,
                    h_kodu=h.h_kodu,
                    status=h_status,
                    status_label=status_lbl,
                    range_details=range_det
                )
                evaluated_hazards.append(classified_h)

                all_hazards.append({
                    "zararlilik_sinifi": h.zararlilik_sinifi,
                    "kategori": h.kategori,
                    "h_kodu": h.h_kodu,
                    "status": h_status,
                    "status_label": status_lbl,
                    "range_details": range_det
                })
                all_h_codes.add(h.h_kodu)

            res_max.hazards = evaluated_hazards
            res_max.has_indeterminate = has_rule_indeterminate
            rule_results.append(res_max)

            for euh in res_max.euh_codes:
                all_euh_codes.add(euh)

            for pic in res_max.piktogramlar:
                all_pictograms.add(pic)

            if res_max.uyari_kelimesi:
                warning_words.append(res_max.uyari_kelimesi)

            for note in res_max.calculation_notes:
                calculation_steps.append(note)

            if has_rule_indeterminate:
                calculation_steps.append(
                    f"⚠️ [ARALIK BELİRSİZLİĞİ / INDETERMINATE] {rule.rule_name}: "
                    "Bileşenin konsantrasyon aralığı eşiği kapsadığı için minimum konsantrasyonda bu sınıflandırma oluşmamakta, "
                    "ancak maksimum konsantrasyonda oluşmaktadır. ECHA rehberi uyarınca GBF'de en güvenli (worst-case) yaklaşım olarak listelenmiştir."
                )

        # Etiket Elemanlarını Çözümle
        resolved_labels = LabelGenerator.resolve_label_elements(
            raw_hazards=all_hazards,
            raw_h_codes=all_h_codes,
            raw_euh_codes=all_euh_codes,
            raw_pictograms=all_pictograms,
            rule_warning_words=warning_words
        )

        return ClassificationResult(
            siniflandirmalar=resolved_labels["siniflandirmalar"],
            h_ifadeleri=resolved_labels["h_ifadeleri"],
            euh_ifadeleri=resolved_labels["euh_ifadeleri"],
            piktogramlar=resolved_labels["piktogramlar"],
            uyari_kelimesi=resolved_labels["uyari_kelimesi"],
            p_ifadeleri=resolved_labels["p_ifadeleri"],
            calculation_steps=calculation_steps,
            rule_results=rule_results,
            has_indeterminate=bool(indeterminate_hazards),
            indeterminate_hazards=indeterminate_hazards
        )

