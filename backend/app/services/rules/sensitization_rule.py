"""
Solunum ve Cilt Hassaslaşması Kural Stratejisi
(Sensitization Rule - SEA Ek-1 Bölüm 3.4)
"""

from typing import List
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult, ClassifiedHazard
from app.services.rules.base_rule import BaseHazardRule


class SensitizationRule(BaseHazardRule):
    """
    - Solunum Hassaslaştırıcı (H334): Kat 1 >= %0.2 -> Kategori 1 (H334)
    - Cilt Hassaslaştırıcı (H317): Kat 1 >= %1.0 -> Kategori 1 (H317)
    - %0.1 <= Cilt Sens < %1.0 -> EUH208
    - %0.1 <= Resp Sens < %0.2 ve izosiyanat mevcut -> EUH204
    """

    @property
    def rule_name(self) -> str:
        return "SensitizationRule"

    def evaluate(
        self,
        context: CalculationContext,
        substances: List[StructuredSubstance]
    ) -> RuleResult:
        result = RuleResult(rule_name=self.rule_name)

        c_resp_sens_1 = 0.0
        c_skin_sens_1 = 0.0
        has_isocyanates = False

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])

            if "H334" in codes:
                c_resp_sens_1 += conc
                name_l = s.name.lower()
                if any(iso in name_l for iso in ["izosiyanat", "isocyanate", "mdi", "tdi", "hdi", "ipdi"]) or s.is_isocyanate:
                    has_isocyanates = True

            if "H317" in codes:
                c_skin_sens_1 += conc

        # Solunum Hassaslaşması
        if c_resp_sens_1 >= 0.2:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Solunum veya Cilt Hassaslaşması",
                kategori="Solunum Hassaslaştırıcı Kat 1",
                h_kodu="H334"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(
                f"• Solunum Hassaslaşması: ∑(Solunum Hassaslaştırıcı) = %{c_resp_sens_1:.2f} >= %0.2 -> Sınıflandırıldı: Kategori 1 (H334)"
            )
        elif 0.1 <= c_resp_sens_1 < 0.2:
            if has_isocyanates:
                result.euh_codes.append("EUH204")
                result.calculation_notes.append(
                    f"• İzosiyanat Hassaslaşması: %0.1 <= %{c_resp_sens_1:.2f} < %0.2 ve izosiyanat bileşeni mevcut -> EUH204 (İzosiyanat içerir) tetiklendi."
                )
            else:
                result.euh_codes.append("EUH208")
                result.calculation_notes.append(
                    f"• Solunum Hassaslaşması: %0.1 <= %{c_resp_sens_1:.2f} < %0.2 -> EUH208 (Alerjik reaksiyona yol açabilir) tetiklendi."
                )

        # Cilt Hassaslaşması
        if c_skin_sens_1 >= 1.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Solunum veya Cilt Hassaslaşması",
                kategori="Cilt Hassaslaştırıcı Kat 1",
                h_kodu="H317"
            ))
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(
                f"• Cilt Hassaslaşması: ∑(Cilt Hassaslaştırıcı) = %{c_skin_sens_1:.1f} >= %1.0 -> Sınıflandırıldı: Kategori 1 (H317)"
            )
        elif 0.1 <= c_skin_sens_1 < 1.0:
            if "EUH208" not in result.euh_codes:
                result.euh_codes.append("EUH208")
            result.calculation_notes.append(
                f"• Cilt Hassaslaşması: %0.1 <= %{c_skin_sens_1:.1f} < %1.0 -> EUH208 tetiklendi."
            )

        return result
