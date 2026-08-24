"""
İlave Zararlılık İfadeleri Kural Stratejisi (Supplemental Hazard Statements Rule)
(EUH066, vb. - SEA Ek-4 / CLP)
"""

from typing import List
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult
from app.services.rules.base_rule import BaseHazardRule


class SupplementalHazardRule(BaseHazardRule):
    """
    - EUH066: Anlamlı solvent içeriği (>= %10) veya açıkça EUH066 içeren bileşen bulunması,
      ancak karışımın Cilt Tahrişi Kat 2 veya Cilt Aşınması Kat 1 olmaması durumunda verilir.
    """

    @property
    def rule_name(self) -> str:
        return "SupplementalHazardRule"

    def evaluate(
        self,
        context: CalculationContext,
        substances: List[StructuredSubstance]
    ) -> RuleResult:
        result = RuleResult(rule_name=self.rule_name)

        c_solvent_total = 0.0
        has_explicit_euh066 = False

        c_skin_corr_1 = 0.0
        c_skin_irrit_2 = 0.0

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])

            # Solvent göstergeleri
            if any(c in codes for c in ["H224", "H225", "H226", "H304", "H336"]):
                c_solvent_total += conc

            if "EUH066" in codes:
                has_explicit_euh066 = True

            if "H314" in codes:
                c_skin_corr_1 += conc
            if "H315" in codes:
                c_skin_irrit_2 += conc

        # Cilt tahrişi veya aşınması eşik kontrolü
        is_skin_corr_1 = (c_skin_corr_1 >= 5.0)
        is_skin_irrit_2 = (10.0 * c_skin_corr_1 + c_skin_irrit_2 >= 10.0) or (1.0 <= c_skin_corr_1 < 5.0)

        if (has_explicit_euh066 or c_solvent_total >= 10.0) and not is_skin_irrit_2 and not is_skin_corr_1:
            result.euh_codes.append("EUH066")
            result.calculation_notes.append(
                f"• İlave Bilgi: Anlamlı solvent içeriği (%{c_solvent_total:.1f}) mevcut olup Cilt Tahrişi Kat 2 sınırının altında kaldığı için EUH066 eklendi."
            )

        return result
