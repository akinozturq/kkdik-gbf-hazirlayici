"""
Regülatif Sınıflandırma Boru Hattı (Regulatory Engine Pipeline)
"""

import re
from typing import List, Dict, Any, Optional
from app.models.regulatory import (
    ConcentrationValue,
    HazardEntry,
    InhalationExposure,
    StructuredSubstance,
    CalculationContext,
    ClassificationResult,
    RuleResult
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
        """
        substances: List[StructuredSubstance] = []
        for comp in raw_bilesenler:
            name = comp.get("ad") or "Bileşen"
            conc_model = cls.parse_concentration_model(comp.get("konsantrasyon"))
            sinif_str = comp.get("siniflandirma") or ""
            codes = cls.extract_h_codes(sinif_str)

            # Zararlılık profilleri
            hazards: List[HazardEntry] = []
            for c in codes:
                hazards.append(HazardEntry(hazard_class=sinif_str, category="", h_code=c))

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

            substances.append(StructuredSubstance(
                name=name,
                cas_no=comp.get("cas_no"),
                ec_no=comp.get("ec_no"),
                concentration=conc_model,
                hazards=hazards,
                raw_h_codes=codes,
                ate_oral=ate_oral,
                ate_dermal=ate_dermal,
                inhalation=inhal_model,
                is_isocyanate=is_iso,
                m_factor_acute=m_akut,
                m_factor_chronic=m_kronik
            ))

        return substances

    def execute(
        self,
        substances: List[StructuredSubstance],
        context: CalculationContext
    ) -> ClassificationResult:
        """
        Boru hattındaki tüm kural stratejilerini sırayla çalıştırır ve
        etiket elemanlarını çözümleyerek ClassificationResult üretir.
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

        all_hazards: List[Dict[str, str]] = []
        all_h_codes: Set[str] = set()
        all_euh_codes: Set[str] = set()
        all_pictograms: Set[str] = set()
        warning_words: List[str] = []
        calculation_steps: List[str] = []
        rule_results: List[RuleResult] = []

        # Bileşen Özeti Başlığı
        calculation_steps.append("📋 GİRDİ BİLEŞENLERİ VE KONSANTRASYONLARI:")
        for s in substances:
            codes_str = ", ".join(s.raw_h_codes) if s.raw_h_codes else "Sınıflandırma yok"
            calculation_steps.append(f"• {s.name} (%{s.concentration.value:.1f}): {codes_str}")

        calculation_steps.append("\n⚖️ SEA EK-1 TOPLANABİLİRLİK VE EŞİK DEĞER DEĞERLENDİRMESİ:")

        # Kuralları İcra Et
        for rule in self.rules:
            res: RuleResult = rule.evaluate(context, substances)
            rule_results.append(res)

            for h in res.hazards:
                all_hazards.append({
                    "zararlilik_sinifi": h.zararlilik_sinifi,
                    "kategori": h.kategori,
                    "h_kodu": h.h_kodu
                })
                all_h_codes.add(h.h_kodu)

            for euh in res.euh_codes:
                all_euh_codes.add(euh)

            for pic in res.piktogramlar:
                all_pictograms.add(pic)

            if res.uyari_kelimesi:
                warning_words.append(res.uyari_kelimesi)

            for note in res.calculation_notes:
                calculation_steps.append(note)

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
            rule_results=rule_results
        )
