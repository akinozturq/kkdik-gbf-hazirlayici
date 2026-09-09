"""
Cilt Aşınması/Tahrişi ve Göz Hasarı/Tahrişi Kural Stratejisi
(Skin and Eye Corrosion/Irritation Rule - SEA Ek-1 Bölüm 3.2 & 3.3)
"""

from typing import List, Optional
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult, ClassifiedHazard
from app.services.rules.base_rule import BaseHazardRule
from app.services.regulatory_engine.thresholds import RegulatoryThresholdProvider


class SkinEyeRule(BaseHazardRule):
    """
    SEA Ek-1 Tablo 3.2.3 & 3.3.3 Toplanabilirlik Kuralları:
    - İlgili Bileşen Kesme Sınırı (Relevant Component Cut-off Limit: varsayılan %1.0, SCL < %1.0 ise SCL)
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
        result.source_references = [
            "SEA Ek-1 Bölüm 3.2 & 3.3",
            "CLP Annex I Table 3.2.3 & 3.3.3"
        ]
        result.assumptions = [
            "SEA Ek-1 additivity ilkesi uyarınca Skin Corr 1 bileşenleri Eye Dam 1 havuzuna %100 oranında katkı sağlar.",
            "İlgili bileşen kesme sınırı (Cut-off) altındaki bileşenler toplanabilirlik havuzuna dahil edilmez."
        ]
        c_skin_corr_1a = 0.0
        c_skin_corr_1b = 0.0
        c_skin_corr_1c = 0.0
        c_skin_corr_1_gen = 0.0
        c_skin_irrit_2 = 0.0
        c_eye_dam_1 = 0.0
        c_eye_irrit_2 = 0.0

        # SCL Tetikleyicileri
        scl_skin_corr = None
        scl_skin_irrit = None
        scl_eye_dam = None
        scl_eye_irrit = None

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])
            hazard_classes_str = " ".join([h.hazard_class for h in s.hazards])

            # Hedefli SCL kayıtları
            scl_corr_h = next((h for h in s.hazards if h.scl is not None and (h.h_code == "H314" or "Skin Corr" in h.hazard_class)), None)
            scl_irrit_h = next((h for h in s.hazards if h.scl is not None and (h.h_code == "H315" or "Skin Irrit" in h.hazard_class)), None)
            scl_eye_dam_h = next((h for h in s.hazards if h.scl is not None and (h.h_code == "H318" or "Eye Dam" in h.hazard_class)), None)
            scl_eye_irrit_h = next((h for h in s.hazards if h.scl is not None and (h.h_code == "H319" or "Eye Irrit" in h.hazard_class)), None)

            # 1. CİLT AŞINMASI (SKIN CORROSION)
            added_eye_dam_from_corr = False
            if "H314" in codes or "Skin Corr." in hazard_classes_str:
                corr_cat = scl_corr_h.category if scl_corr_h and scl_corr_h.category else "1"
                if any("1A" in (h.category or "").upper() for h in s.hazards) or "1A" in hazard_classes_str.upper():
                    corr_cat = "1A"
                elif any("1B" in (h.category or "").upper() for h in s.hazards) or "1B" in hazard_classes_str.upper():
                    corr_cat = "1B"
                elif any("1C" in (h.category or "").upper() for h in s.hazards) or "1C" in hazard_classes_str.upper():
                    corr_cat = "1C"

                thresh_corr = RegulatoryThresholdProvider.get_skin_corr_threshold(
                    scl=scl_corr_h.scl if scl_corr_h else None,
                    category=corr_cat
                )

                if not thresh_corr.is_relevant(conc):
                    result.calculation_notes.append(
                        f"• Kesme Sınırı (Cut-off): [{s.name}] %{conc:.2f} konsantrasyonu, Cilt Aşınması için ilgili cut-off eşiğinin (%{thresh_corr.effective_cutoff:.1f}) altında olduğundan toplanabilirlik havuzuna dahil edilmedi."
                    )
                else:
                    if scl_corr_h is not None:
                        if thresh_corr.triggers_classification(conc) and scl_skin_corr is None:
                            scl_skin_corr = (s.name, conc, scl_corr_h.scl, scl_corr_h.category or corr_cat)
                    else:
                        if corr_cat == "1A":
                            c_skin_corr_1a += conc
                        elif corr_cat == "1B":
                            c_skin_corr_1b += conc
                        elif corr_cat == "1C":
                            c_skin_corr_1c += conc
                        else:
                            c_skin_corr_1_gen += conc
                        c_eye_dam_1 += conc  # Skin Corr 1 genel havuzu otomatik Eye Dam 1 sayılır
                        added_eye_dam_from_corr = True

            # 2. CİLT TAHRİŞİ (SKIN IRRITATION)
            if "H315" in codes or "Skin Irrit" in hazard_classes_str:
                thresh_irrit = RegulatoryThresholdProvider.get_skin_irrit_threshold(
                    scl=scl_irrit_h.scl if scl_irrit_h else None
                )

                if not thresh_irrit.is_relevant(conc):
                    result.calculation_notes.append(
                        f"• Kesme Sınırı (Cut-off): [{s.name}] %{conc:.2f} konsantrasyonu, Cilt Tahrişi için ilgili cut-off eşiğinin (%{thresh_irrit.effective_cutoff:.1f}) altında olduğundan toplanabilirlik havuzuna dahil edilmedi."
                    )
                else:
                    if scl_irrit_h is not None:
                        if thresh_irrit.triggers_classification(conc) and scl_skin_irrit is None:
                            scl_skin_irrit = (s.name, conc, scl_irrit_h.scl)
                    else:
                        c_skin_irrit_2 += conc

            # 3. GÖZ HASARI (SERIOUS EYE DAMAGE)
            if "H318" in codes or "Eye Dam" in hazard_classes_str:
                thresh_eye_dam = RegulatoryThresholdProvider.get_eye_dam_threshold(
                    scl=scl_eye_dam_h.scl if scl_eye_dam_h else None
                )

                if not thresh_eye_dam.is_relevant(conc):
                    result.calculation_notes.append(
                        f"• Kesme Sınırı (Cut-off): [{s.name}] %{conc:.2f} konsantrasyonu, Ciddi Göz Hasarı için ilgili cut-off eşiğinin (%{thresh_eye_dam.effective_cutoff:.1f}) altında olduğundan toplanabilirlik havuzuna dahil edilmedi."
                    )
                else:
                    if scl_eye_dam_h is not None:
                        if thresh_eye_dam.triggers_classification(conc) and scl_eye_dam is None:
                            scl_eye_dam = (s.name, conc, scl_eye_dam_h.scl)
                    else:
                        if not added_eye_dam_from_corr:
                            c_eye_dam_1 += conc

            # 4. GÖZ TAHRİŞİ (EYE IRRITATION)
            if "H319" in codes or "Eye Irrit" in hazard_classes_str:
                thresh_eye_irrit = RegulatoryThresholdProvider.get_eye_irrit_threshold(
                    scl=scl_eye_irrit_h.scl if scl_eye_irrit_h else None
                )

                if not thresh_eye_irrit.is_relevant(conc):
                    result.calculation_notes.append(
                        f"• Kesme Sınırı (Cut-off): [{s.name}] %{conc:.2f} konsantrasyonu, Göz Tahrişi için ilgili cut-off eşiğinin (%{thresh_eye_irrit.effective_cutoff:.1f}) altında olduğundan toplanabilirlik havuzuna dahil edilmedi."
                    )
                else:
                    if scl_eye_irrit_h is not None:
                        if thresh_eye_irrit.triggers_classification(conc) and scl_eye_irrit is None:
                            scl_eye_irrit = (s.name, conc, scl_eye_irrit_h.scl)
                    else:
                        c_eye_irrit_2 += conc

        # 1. CİLT AŞINMASI (SKIN CORROSION)
        total_skin_corr_1 = c_skin_corr_1a + c_skin_corr_1b + c_skin_corr_1c + c_skin_corr_1_gen
        is_skin_corr_1 = False
        is_skin_irrit_2 = False

        if scl_skin_corr is not None:
            is_skin_corr_1 = True
            sub_name, sub_c, sub_scl, sub_cat = scl_skin_corr
            cat_name = f"Kategori {sub_cat}" if "Kategori" not in sub_cat else sub_cat
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Cilt Aşınması / Tahrişi",
                kategori=cat_name,
                h_kodu="H314"
            ))
            result.piktogramlar.append("GHS05")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(
                f"• Cilt Aşınması (SCL): [{sub_name}] %{sub_c:.1f} >= SCL (%{sub_scl:.1f}) -> Spesifik Konsantrasyon Sınırı ile sınıflandırıldı: {cat_name} (H314)"
            )
        elif total_skin_corr_1 >= 5.0:
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
        elif scl_skin_irrit is not None:
            is_skin_irrit_2 = True
            sub_name, sub_c, sub_scl = scl_skin_irrit
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Cilt Aşınması / Tahrişi",
                kategori="Kategori 2",
                h_kodu="H315"
            ))
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(
                f"• Cilt Tahrişi (SCL): [{sub_name}] %{sub_c:.1f} >= SCL (%{sub_scl:.1f}) -> Spesifik Konsantrasyon Sınırı ile sınıflandırıldı: Kategori 2 (H315)"
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
            if scl_eye_dam is not None:
                sub_name, sub_c, sub_scl = scl_eye_dam
                result.hazards.append(ClassifiedHazard(
                    zararlilik_sinifi="Ciddi Göz Hasarı / Göz Tahrişi",
                    kategori="Kategori 1",
                    h_kodu="H318"
                ))
                result.piktogramlar.append("GHS05")
                result.uyari_kelimesi = "Tehlike"
                result.calculation_notes.append(
                    f"• Göz Hasarı (SCL): [{sub_name}] %{sub_c:.1f} >= SCL (%{sub_scl:.1f}) -> Spesifik Konsantrasyon Sınırı ile sınıflandırıldı: Kategori 1 (H318)"
                )
            elif c_eye_dam_1 >= 3.0:
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
            elif scl_eye_irrit is not None:
                sub_name, sub_c, sub_scl = scl_eye_irrit
                result.hazards.append(ClassifiedHazard(
                    zararlilik_sinifi="Ciddi Göz Hasarı / Göz Tahrişi",
                    kategori="Kategori 2",
                    h_kodu="H319"
                ))
                result.piktogramlar.append("GHS07")
                if result.uyari_kelimesi != "Tehlike":
                    result.uyari_kelimesi = "Dikkat"
                result.calculation_notes.append(
                    f"• Göz Tahrişi (SCL): [{sub_name}] %{sub_c:.1f} >= SCL (%{sub_scl:.1f}) -> Spesifik Konsantrasyon Sınırı ile sınıflandırıldı: Kategori 2 (H319)"
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

        result.evidence = {
            "c_skin_corr_1a": round(c_skin_corr_1a, 2),
            "c_skin_corr_1b": round(c_skin_corr_1b, 2),
            "c_skin_corr_1c": round(c_skin_corr_1c, 2),
            "total_skin_corr_1": round(total_skin_corr_1, 2),
            "c_skin_irrit_2": round(c_skin_irrit_2, 2),
            "c_eye_dam_1": round(c_eye_dam_1, 2),
            "c_eye_irrit_2": round(c_eye_irrit_2, 2),
            "scl_skin_corr": scl_skin_corr,
            "scl_skin_irrit": scl_skin_irrit,
            "scl_eye_dam": scl_eye_dam,
            "scl_eye_irrit": scl_eye_irrit,
        }

        result.calculations = [
            {
                "parameter": "total_skin_corr_1",
                "description": "Toplam Cilt Aşınması Kat 1 Konsantrasyonu",
                "value": round(total_skin_corr_1, 2),
                "threshold": 5.0,
                "threshold_met": total_skin_corr_1 >= 5.0,
            },
            {
                "parameter": "skin_irrit_sum",
                "description": "(10 x ∑Skin Corr. 1) + ∑Skin Irrit. 2",
                "value": round(10.0 * total_skin_corr_1 + c_skin_irrit_2, 2),
                "threshold": 10.0,
                "threshold_met": (10.0 * total_skin_corr_1 + c_skin_irrit_2) >= 10.0,
            },
            {
                "parameter": "c_eye_dam_1",
                "description": "Toplam Ciddi Göz Hasarı Kat 1 Konsantrasyonu (Skin Corr dahil)",
                "value": round(c_eye_dam_1, 2),
                "threshold": 3.0,
                "threshold_met": c_eye_dam_1 >= 3.0,
            },
            {
                "parameter": "eye_irrit_sum",
                "description": "(10 x ∑Eye Dam. 1) + ∑Eye Irrit. 2",
                "value": round(10.0 * c_eye_dam_1 + c_eye_irrit_2, 2),
                "threshold": 10.0,
                "threshold_met": (10.0 * c_eye_dam_1 + c_eye_irrit_2) >= 10.0,
            },
        ]

        if result.hazards:
            result.status = "SUFFICIENT"
            result.decision = "; ".join(f"{h.zararlilik_sinifi} {h.kategori} ({h.h_kodu})" for h in result.hazards)
            result.reason = "Cilt/Göz toplanabilirlik veya SCL eşik değerleri aşıldı."
        elif (total_skin_corr_1 > 0 or c_skin_irrit_2 > 0 or c_eye_dam_1 > 0 or c_eye_irrit_2 > 0):
            result.status = "SUFFICIENT"
            result.decision = None
            result.reason = "Cilt/Göz bileşenleri mevcut ancak toplanabilirlik eşik değerleri aşılmadı."
        else:
            result.status = "NOT_APPLICABLE"
            result.decision = None
            result.reason = "Cilt veya göz zararlılığı taşıyan bileşen bulunmamaktadır."

        return result
