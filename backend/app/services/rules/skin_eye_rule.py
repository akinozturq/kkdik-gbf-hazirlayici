"""
Cilt Aşınması/Tahrişi ve Göz Hasarı/Tahrişi Kural Stratejisi
(Skin and Eye Corrosion/Irritation Rule - SEA Ek-1 Bölüm 3.2 & 3.3)
"""

from typing import List
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult, ClassifiedHazard
from app.services.rules.base_rule import BaseHazardRule


class SkinEyeRule(BaseHazardRule):
    """
    SEA Ek-1 Tablo 3.2.3 & 3.3.3 Toplanabilirlik Kuralları:
    - Skin Corr 1A / 1B / 1C ayrımı (Σ Skin Corr >= %5 -> Kat 1)
    - 10 x Σ Skin Corr 1 + Σ Skin Irrit 2 >= %10 -> Cilt Tahrişi Kat 2 (H315)
    - Σ Eye Dam 1 + Σ Skin Corr 1 >= %3 -> Göz Hasarı Kat 1 (H318)
    - 10 x (Σ Eye Dam 1 + Σ Skin Corr 1) + Σ Eye Irrit 2 >= %10 -> Göz Tahrişi Kat 2 (H319)
    """

    @property
    def rule_name(self) -> str:
        return "SkinEyeRule"

    def evaluate(
        self,
        context: CalculationContext,
        substances: List[StructuredSubstance]
    ) -> RuleResult:
        result = RuleResult(rule_name=self.rule_name)

        c_skin_corr_1a = 0.0
        c_skin_corr_1b = 0.0
        c_skin_corr_1c = 0.0
        c_skin_corr_1_gen = 0.0
        c_skin_irrit_2 = 0.0
        c_eye_dam_1 = 0.0
        c_eye_irrit_2 = 0.0

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])
            hazard_classes_str = " ".join([h.hazard_class for h in s.hazards])

            # Cilt Aşınması
            if "H314" in codes or "Skin Corr." in hazard_classes_str:
                if any("1A" in h.category.upper() for h in s.hazards) or "1A" in hazard_classes_str.upper():
                    c_skin_corr_1a += conc
                elif any("1B" in h.category.upper() for h in s.hazards) or "1B" in hazard_classes_str.upper():
                    c_skin_corr_1b += conc
                elif any("1C" in h.category.upper() for h in s.hazards) or "1C" in hazard_classes_str.upper():
                    c_skin_corr_1c += conc
                else:
                    c_skin_corr_1_gen += conc
                c_eye_dam_1 += conc  # Skin Corr 1 otomatik Eye Dam 1 sayılır

            # Cilt Tahrişi
            if "H315" in codes:
                c_skin_irrit_2 += conc

            # Göz Hasarı
            if "H318" in codes:
                c_eye_dam_1 += conc

            # Göz Tahrişi
            if "H319" in codes:
                c_eye_irrit_2 += conc

        # 1. CİLT AŞINMASI (SKIN CORROSION)
        total_skin_corr_1 = c_skin_corr_1a + c_skin_corr_1b + c_skin_corr_1c + c_skin_corr_1_gen
        is_skin_corr_1 = False
        is_skin_irrit_2 = False

        if total_skin_corr_1 >= 5.0:
            is_skin_corr_1 = True
            if c_skin_corr_1a >= 5.0:
                skin_cat = "Kategori 1A"
            elif (c_skin_corr_1a + c_skin_corr_1b) >= 5.0:
                skin_cat = "Kategori 1B"
            elif (c_skin_corr_1a + c_skin_corr_1b + c_skin_corr_1c) >= 5.0:
                skin_cat = "Kategori 1C"
            else:
                skin_cat = "Kategori 1"

            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Cilt Aşınması / Tahrişi",
                kategori=skin_cat,
                h_kodu="H314"
            ))
            result.piktogramlar.append("GHS05")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(
                f"• Cilt Aşınması: ∑(Skin Corr. 1) = %{total_skin_corr_1:.1f} >= %5.0 -> Sınıflandırıldı: {skin_cat} (H314)"
            )
        elif 1.0 <= total_skin_corr_1 < 5.0 or (10.0 * total_skin_corr_1 + c_skin_irrit_2) >= 10.0:
            is_skin_irrit_2 = True
            skin_sum = (10.0 * total_skin_corr_1 + c_skin_irrit_2)
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Cilt Aşınması / Tahrişi",
                kategori="Kategori 2",
                h_kodu="H315"
            ))
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(
                f"• Cilt Tahrişi: (10 x ∑Skin Corr. 1) + ∑Skin Irrit. 2 = %{skin_sum:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 2 (H315)"
            )

        # 2. GÖZ HASARI / TAHRİŞİ (EYE DAMAGE / IRRITATION)
        if not is_skin_corr_1:
            if c_eye_dam_1 >= 3.0:
                result.hazards.append(ClassifiedHazard(
                    zararlilik_sinifi="Ciddi Göz Hasarı / Göz Tahrişi",
                    kategori="Kategori 1",
                    h_kodu="H318"
                ))
                result.piktogramlar.append("GHS05")
                result.uyari_kelimesi = "Tehlike"
                result.calculation_notes.append(
                    f"• Göz Hasarı: ∑(Eye Dam. 1) = %{c_eye_dam_1:.1f} >= %3.0 -> Sınıflandırıldı: Kategori 1 (H318)"
                )
            elif (10.0 * c_eye_dam_1 + c_eye_irrit_2) >= 10.0 or (1.0 <= c_eye_dam_1 < 3.0):
                eye_sum = (10.0 * c_eye_dam_1 + c_eye_irrit_2)
                result.hazards.append(ClassifiedHazard(
                    zararlilik_sinifi="Ciddi Göz Hasarı / Göz Tahrişi",
                    kategori="Kategori 2",
                    h_kodu="H319"
                ))
                result.piktogramlar.append("GHS07")
                if result.uyari_kelimesi != "Tehlike":
                    result.uyari_kelimesi = "Dikkat"
                result.calculation_notes.append(
                    f"• Göz Tahrişi: (10 x ∑Eye Dam. 1) + ∑Eye Irrit. 2 = %{eye_sum:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 2 (H319)"
                )

        return result
