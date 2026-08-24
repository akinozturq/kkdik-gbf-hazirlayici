"""
Belirli Hedef Organ Toksisitesi Kural Stratejisi
(STOT SE & STOT RE Rule - SEA Ek-1 Bölüm 3.8 & 3.9)
"""

from typing import List
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult, ClassifiedHazard
from app.services.rules.base_rule import BaseHazardRule


class STOTRule(BaseHazardRule):
    """
    STOT SE:
    - Kat 1 (H370): STOT SE 1 >= %10.0
    - Kat 2 (H371): STOT SE 2 >= %10.0 veya %1.0 <= STOT SE 1 < %10.0
    - Kat 3 (H335 / H336): STOT SE 3 >= %20.0

    STOT RE:
    - Kat 1 (H372): STOT RE 1 >= %10.0
    - Kat 2 (H373): STOT RE 2 >= %10.0 veya %1.0 <= STOT RE 1 < %10.0
    """

    @property
    def rule_name(self) -> str:
        return "STOTRule"

    def evaluate(
        self,
        context: CalculationContext,
        substances: List[StructuredSubstance]
    ) -> RuleResult:
        result = RuleResult(rule_name=self.rule_name)

        c_stot_se1 = 0.0
        c_stot_se2 = 0.0
        c_stot_se3_335 = 0.0
        c_stot_se3_336 = 0.0
        c_stot_re1 = 0.0
        c_stot_re2 = 0.0

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])

            if "H370" in codes:
                c_stot_se1 += conc
            if "H371" in codes:
                c_stot_se2 += conc
            if "H335" in codes:
                c_stot_se3_335 += conc
            if "H336" in codes:
                c_stot_se3_336 += conc
            if "H372" in codes:
                c_stot_re1 += conc
            if "H373" in codes:
                c_stot_re2 += conc

        # STOT SE
        if c_stot_se1 >= 10.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 1",
                h_kodu="H370"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(f"• STOT SE: ∑(STOT SE 1) = %{c_stot_se1:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 1 (H370)")
        elif c_stot_se2 >= 10.0 or (1.0 <= c_stot_se1 < 10.0):
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 2",
                h_kodu="H371"
            ))
            result.piktogramlar.append("GHS08")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT SE: ∑(STOT SE 2) = %{c_stot_se2:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 2 (H371)")

        if c_stot_se3_335 >= 20.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 3",
                h_kodu="H335"
            ))
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT SE: ∑(H335) = %{c_stot_se3_335:.1f} >= %20.0 -> Sınıflandırıldı: Kategori 3 (H335)")

        if c_stot_se3_336 >= 20.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 3",
                h_kodu="H336"
            ))
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT SE: ∑(H336) = %{c_stot_se3_336:.1f} >= %20.0 -> Sınıflandırıldı: Kategori 3 (H336)")

        # STOT RE
        if c_stot_re1 >= 10.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tekrarlı Maruz Kalma",
                kategori="Kategori 1",
                h_kodu="H372"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(f"• STOT RE: ∑(STOT RE 1) = %{c_stot_re1:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 1 (H372)")
        elif c_stot_re2 >= 1.0 or (1.0 <= c_stot_re1 < 10.0):
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tekrarlı Maruz Kalma",
                kategori="Kategori 2",
                h_kodu="H373"
            ))
            result.piktogramlar.append("GHS08")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT RE: ∑(STOT RE 2) = %{c_stot_re2:.1f} >= %1.0 -> Sınıflandırıldı: Kategori 2 (H373)")

        return result
