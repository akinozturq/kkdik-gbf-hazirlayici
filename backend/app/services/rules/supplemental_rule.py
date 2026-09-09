"""
İlave Zararlılık İfadeleri Kural Stratejisi (Supplemental Hazard Statements Rule)
(EUH066, vb. - SEA Ek-4 / CLP)
"""

from typing import List
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult
from app.services.rules.base_rule import BaseHazardRule


class SupplementalHazardRule(BaseHazardRule):
    """
    SEA Ek-4 / CLP Ek-2 Bölüm 1.1.7:
    - EUH066 ('Tekrarlı maruziyette ciltte kuruluğa ve çatlaklara yol açabilir'):
      Bileşenlerin resmi sınıflandırmasında açıkça EUH066 bulunması durumunda uygulanır.
      Sezgisel solvent tahmin yöntemi (H224/H225/H226/H304/H336) devre dışı bırakılmıştır;
      yalnızca açık (explicit) sınıflandırma verisine dayanır.
    - Karışım Cilt Aşınması (Kat 1 / H314) veya Cilt Tahrişi (Kat 2 / H315) olarak
      sınıflandırılmışsa, CLP Ek-2 uyarınca EUH066 etikete eklenmez (daha şiddetli zarar önceliklidir).
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

        euh066_substances: List[str] = []
        c_skin_corr_1 = 0.0
        c_skin_irrit_2 = 0.0

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])

            # Açık (explicit) EUH066 kontrolü
            has_sub_euh066 = (
                s.has_euh066 or
                "EUH066" in codes or
                any(h.has_euh066 or h.h_code == "EUH066" for h in s.hazards)
            )

            if has_sub_euh066:
                euh066_substances.append(f"{s.name} (%{conc:g})")

            if "H314" in codes:
                c_skin_corr_1 += conc
            if "H315" in codes:
                c_skin_irrit_2 += conc

        # Cilt tahrişi veya aşınması eşik kontrolü (CLP Ek-2 Madde 1.1.7)
        is_skin_corr_1 = (c_skin_corr_1 >= 5.0)
        is_skin_irrit_2 = (10.0 * c_skin_corr_1 + c_skin_irrit_2 >= 10.0) or (1.0 <= c_skin_corr_1 < 5.0)

        if euh066_substances:
            if is_skin_corr_1 or is_skin_irrit_2:
                result.calculation_notes.append(
                    f"• İlave Bilgi (EUH066): Karışımda açıkça EUH066 taşıyan bileşenler ({', '.join(euh066_substances)}) bulunmasına rağmen, "
                    "karışım Cilt Aşınması/Tahrişi olarak sınıflandırıldığından CLP Ek-2 uyarınca EUH066 etikete eklenmemiştir."
                )
            else:
                result.euh_codes.append("EUH066")
                result.calculation_notes.append(
                    f"• İlave Zararlılık (EUH066): Açıkça EUH066 ('Tekrarlı maruziyette ciltte kuruluğa ve çatlaklara yol açabilir') taşıyan "
                    f"bileşen(ler) tespit edildi: {', '.join(euh066_substances)}. Karışım Cilt Tahrişi/Aşınması kriterlerini karşılamadığından EUH066 etikete eklendi."
                )
        else:
            result.calculation_notes.append(
                "• İlave Zararlılık (EUH066): Karışımdaki bileşenlerde açıkça EUH066 zararlılığı bulunmadığından EUH066 atanmadı (Sezgisel solvent varsayımı devre dışıdır)."
            )

        return result
