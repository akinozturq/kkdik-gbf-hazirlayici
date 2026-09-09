"""
Aspirasyon Zararı Kural Stratejisi (Aspiration Hazard Rule - SEA Ek-1 Bölüm 3.10)
"""

from typing import List
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult, ClassifiedHazard
from app.services.rules.base_rule import BaseHazardRule


class AspirationHazardRule(BaseHazardRule):
    """
    SEA Ek-1 Bölüm 3.10.3.3:
    Toplam Kategori 1 Aspirasyon Toksik maddelerin konsantrasyonu >= %10 VE
    40°C'deki kinematik viskozite <= 20.5 mm²/s olmalıdır.
    """

    @property
    def rule_name(self) -> str:
        return "AspirationHazardRule"

    def evaluate(
        self,
        context: CalculationContext,
        substances: List[StructuredSubstance]
    ) -> RuleResult:
        result = RuleResult(rule_name=self.rule_name)

        c_asp_tox_1 = sum(
            s.concentration.value for s in substances
            if "H304" in s.raw_h_codes or any(h.h_code == "H304" or "Asp" in h.hazard_class for h in s.hazards)
        )

        visk = context.kinematik_viskozite_40c

        if c_asp_tox_1 >= 10.0:
            if visk is not None:
                result.data_status = "SUFFICIENT"
                if visk <= 20.5:
                    result.hazards.append(ClassifiedHazard(
                        zararlilik_sinifi="Aspirasyon Zararı",
                        kategori="Kategori 1",
                        h_kodu="H304"
                    ))
                    result.piktogramlar.append("GHS08")
                    result.uyari_kelimesi = "Tehlike"
                    result.calculation_notes.append(
                        f"• Aspirasyon Zararı: ∑(Asp. Tox. 1) = %{c_asp_tox_1:.1f} >= %10.0 ve 40°C kinematik viskozite ({visk:.1f} mm²/s <= 20.5 mm²/s) -> Sınıflandırıldı: Kategori 1 (H304)"
                    )
                else:
                    result.calculation_notes.append(
                        f"• Aspirasyon Zararı: Karışımda %{c_asp_tox_1:.1f} Asp. Tox. 1 bileşeni bulunmasına rağmen, 40°C kinematik viskozite ({visk:.1f} mm²/s > 20.5 mm²/s) eşiğin üzerinde olduğu için H304 olarak SINIFLANDIRILMAMIŞTIR (SEA Ek-1 Bölüm 3.10.3.3.1)."
                    )
            else:
                result.data_status = "INSUFFICIENT_DATA"
                result.calculation_notes.append(
                    f"• Aspirasyon Zararı: Karışımda ∑(Asp. Tox. 1) = %{c_asp_tox_1:.1f} >= %10.0 bileşen bulunmasına rağmen 40°C kinematik viskozite test verisi girilmediğinden (Bilinmiyor / UNKNOWN) sınıflandırma yapılamamıştır (INSUFFICIENT_DATA). ECHA ve SEA Ek-1 Bölüm 3.10 uyarınca kinematik viskozitenin <= 20.5 mm²/s olduğu test edilip doğrulanmalıdır."
                )
        elif c_asp_tox_1 > 0:
            result.data_status = "SUFFICIENT"
            result.calculation_notes.append(
                f"• Aspirasyon Zararı: ∑(Asp. Tox. 1) = %{c_asp_tox_1:.1f} < %10.0 -> Eşik değer aşılmadı."
            )
        else:
            result.data_status = "NOT_APPLICABLE"

        return result
