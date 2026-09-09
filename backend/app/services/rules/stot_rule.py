"""
Belirli Hedef Organ Toksisitesi Kural Stratejisi
(STOT SE & STOT RE Rule - SEA Ek-1 Bölüm 3.8 & 3.9)
"""

from typing import List, Optional
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult, ClassifiedHazard
from app.services.rules.base_rule import BaseHazardRule
from app.services.regulatory_engine.thresholds import RegulatoryThresholdProvider


class STOTRule(BaseHazardRule):
    """
    SEA Ek-1 Bölüm 3.8 & 3.9 Eşik ve Toplanabilirlik Kuralları:
    - İlgili Bileşen Kesme Sınırı (Relevant Component Cut-off Limit: varsayılan %1.0, SCL < %1.0 ise SCL)
    - Spesifik Konsantrasyon Sınırı (SCL) önceliği
    - STOT SE 3: Solunum Yolu Tahrişi (RTI - H335) ve Narkotik Etkiler (NE - H336) bağımsız toplanır (GCL: %20.0)
    - STOT SE:
      - Kat 1 (H370): STOT SE 1 >= %10.0
      - Kat 2 (H371): STOT SE 2 >= %10.0 veya %1.0 <= STOT SE 1 < %10.0
      - Kat 3 (H335 / H336): ∑(H335) >= %20.0 (RTI) ve/veya ∑(H336) >= %20.0 (NE)
    - STOT RE:
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
        result.source_references = [
            "SEA Ek-1 Bölüm 3.8 & 3.9",
            "CLP Annex I Table 3.8.3 & 3.9.3"
        ]
        result.assumptions = [
            "STOT SE 3 (H335 RTI ve H336 NE) bağımsız olarak değerlendirilir ve birbirine eklenmez (GCL: %20.0).",
            "İlgili bileşen kesme sınırı (Cut-off) %1.0 altındaki bileşenler toplanabilirlik havuzuna dahil edilmez."
        ]

        c_stot_se1 = 0.0
        c_stot_se2 = 0.0
        c_stot_se3_335 = 0.0
        c_stot_se3_336 = 0.0
        c_stot_re1 = 0.0
        c_stot_re2 = 0.0

        # SCL Tetikleyicileri (Bileşen Adı, Konsantrasyon, SCL)
        scl_stot_se1 = None
        scl_stot_se2 = None
        scl_stot_se3_335 = None
        scl_stot_se3_336 = None
        scl_stot_re1 = None
        scl_stot_re2 = None

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])

            # Hedefli SCL kayıtları
            scl_se1_h = next((h for h in s.hazards if h.scl is not None and (h.h_code == "H370" or "STOT SE 1" in f"{h.hazard_class} {h.category}")), None)
            scl_se2_h = next((h for h in s.hazards if h.scl is not None and (h.h_code == "H371" or "STOT SE 2" in f"{h.hazard_class} {h.category}")), None)
            scl_se3_335_h = next((h for h in s.hazards if h.scl is not None and (h.h_code == "H335" or "335" in h.h_code)), None)
            scl_se3_336_h = next((h for h in s.hazards if h.scl is not None and (h.h_code == "H336" or "336" in h.h_code)), None)
            scl_re1_h = next((h for h in s.hazards if h.scl is not None and (h.h_code == "H372" or "STOT RE 1" in f"{h.hazard_class} {h.category}")), None)
            scl_re2_h = next((h for h in s.hazards if h.scl is not None and (h.h_code == "H373" or "STOT RE 2" in f"{h.hazard_class} {h.category}")), None)

            # 1. STOT SE 1 (H370)
            if "H370" in codes:
                thresh_se1 = RegulatoryThresholdProvider.get_stot_se_threshold("1", scl=scl_se1_h.scl if scl_se1_h else None)
                if not thresh_se1.is_relevant(conc):
                    result.calculation_notes.append(
                        f"• Kesme Sınırı (Cut-off): [{s.name}] %{conc:.2f} konsantrasyonu, STOT SE 1 için ilgili cut-off eşiğinin (%{thresh_se1.effective_cutoff:.1f}) altında olduğundan toplanabilirlik havuzuna dahil edilmedi."
                    )
                else:
                    if scl_se1_h is not None:
                        if thresh_se1.triggers_classification(conc) and scl_stot_se1 is None:
                            scl_stot_se1 = (s.name, conc, scl_se1_h.scl)
                    else:
                        c_stot_se1 += conc

            # 2. STOT SE 2 (H371)
            if "H371" in codes:
                thresh_se2 = RegulatoryThresholdProvider.get_stot_se_threshold("2", scl=scl_se2_h.scl if scl_se2_h else None)
                if not thresh_se2.is_relevant(conc):
                    result.calculation_notes.append(
                        f"• Kesme Sınırı (Cut-off): [{s.name}] %{conc:.2f} konsantrasyonu, STOT SE 2 için ilgili cut-off eşiğinin (%{thresh_se2.effective_cutoff:.1f}) altında olduğundan toplanabilirlik havuzuna dahil edilmedi."
                    )
                else:
                    if scl_se2_h is not None:
                        if thresh_se2.triggers_classification(conc) and scl_stot_se2 is None:
                            scl_stot_se2 = (s.name, conc, scl_se2_h.scl)
                    else:
                        c_stot_se2 += conc

            # 3. STOT SE 3 — Respiratory Tract Irritation (RTI - H335)
            if "H335" in codes:
                # Uygulanabilirlik (Applicability) denetimi
                effect_rti = next((h.stot_effect for h in s.hazards if h.stot_effect and h.stot_effect.h_code == "H335"), None)
                if effect_rti and not effect_rti.is_applicable:
                    result.calculation_notes.append(
                        f"• STOT SE 3 (RTI): [{s.name}] H335 uygulanabilirlik koşullarını sağlamadığından hariç tutuldu ({effect_rti.applicability_note or 'Uygulanamaz'})."
                    )
                else:
                    thresh_rti = RegulatoryThresholdProvider.get_stot_se_threshold(
                        "3", effect_type="respiratory_tract_irritation", scl=scl_se3_335_h.scl if scl_se3_335_h else None
                    )
                    if not thresh_rti.is_relevant(conc):
                        result.calculation_notes.append(
                            f"• Kesme Sınırı (Cut-off): [{s.name}] %{conc:.2f} konsantrasyonu, STOT SE 3 (Solunum Yolu Tahrişi - H335) için ilgili cut-off eşiğinin (%{thresh_rti.effective_cutoff:.1f}) altında olduğundan toplanabilirlik havuzuna dahil edilmedi."
                        )
                    else:
                        if scl_se3_335_h is not None:
                            if thresh_rti.triggers_classification(conc) and scl_stot_se3_335 is None:
                                scl_stot_se3_335 = (s.name, conc, scl_se3_335_h.scl)
                        else:
                            c_stot_se3_335 += conc

            # 4. STOT SE 3 — Narcotic Effects (NE - H336)
            if "H336" in codes:
                # Uygulanabilirlik (Applicability) denetimi
                effect_ne = next((h.stot_effect for h in s.hazards if h.stot_effect and h.stot_effect.h_code == "H336"), None)
                if effect_ne and not effect_ne.is_applicable:
                    result.calculation_notes.append(
                        f"• STOT SE 3 (NE): [{s.name}] H336 uygulanabilirlik koşullarını sağlamadığından hariç tutuldu ({effect_ne.applicability_note or 'Uygulanamaz'})."
                    )
                else:
                    thresh_ne = RegulatoryThresholdProvider.get_stot_se_threshold(
                        "3", effect_type="narcotic_effects", scl=scl_se3_336_h.scl if scl_se3_336_h else None
                    )
                    if not thresh_ne.is_relevant(conc):
                        result.calculation_notes.append(
                            f"• Kesme Sınırı (Cut-off): [{s.name}] %{conc:.2f} konsantrasyonu, STOT SE 3 (Narkotik Etkiler - H336) için ilgili cut-off eşiğinin (%{thresh_ne.effective_cutoff:.1f}) altında olduğundan toplanabilirlik havuzuna dahil edilmedi."
                        )
                    else:
                        if scl_se3_336_h is not None:
                            if thresh_ne.triggers_classification(conc) and scl_stot_se3_336 is None:
                                scl_stot_se3_336 = (s.name, conc, scl_se3_336_h.scl)
                        else:
                            c_stot_se3_336 += conc

            # 5. STOT RE 1 (H372)
            if "H372" in codes:
                thresh_re1 = RegulatoryThresholdProvider.get_stot_re_threshold("1", scl=scl_re1_h.scl if scl_re1_h else None)
                if not thresh_re1.is_relevant(conc):
                    result.calculation_notes.append(
                        f"• Kesme Sınırı (Cut-off): [{s.name}] %{conc:.2f} konsantrasyonu, STOT RE 1 için ilgili cut-off eşiğinin (%{thresh_re1.effective_cutoff:.1f}) altında olduğundan toplanabilirlik havuzuna dahil edilmedi."
                    )
                else:
                    if scl_re1_h is not None:
                        if thresh_re1.triggers_classification(conc) and scl_stot_re1 is None:
                            scl_stot_re1 = (s.name, conc, scl_re1_h.scl)
                    else:
                        c_stot_re1 += conc

            # 6. STOT RE 2 (H373)
            if "H373" in codes:
                thresh_re2 = RegulatoryThresholdProvider.get_stot_re_threshold("2", scl=scl_re2_h.scl if scl_re2_h else None)
                if not thresh_re2.is_relevant(conc):
                    result.calculation_notes.append(
                        f"• Kesme Sınırı (Cut-off): [{s.name}] %{conc:.2f} konsantrasyonu, STOT RE 2 için ilgili cut-off eşiğinin (%{thresh_re2.effective_cutoff:.1f}) altında olduğundan toplanabilirlik havuzuna dahil edilmedi."
                    )
                else:
                    if scl_re2_h is not None:
                        if thresh_re2.triggers_classification(conc) and scl_stot_re2 is None:
                            scl_stot_re2 = (s.name, conc, scl_re2_h.scl)
                    else:
                        c_stot_re2 += conc

        # STOT SE Sınıflandırma Değerlendirmesi
        if scl_stot_se1 is not None:
            sub_name, sub_c, sub_scl = scl_stot_se1
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 1",
                h_kodu="H370"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(f"• STOT SE (SCL): [{sub_name}] %{sub_c:.1f} >= SCL (%{sub_scl:.1f}) -> Spesifik Konsantrasyon Sınırı ile sınıflandırıldı: Kategori 1 (H370)")
        elif c_stot_se1 >= 10.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 1",
                h_kodu="H370"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(f"• STOT SE: ∑(STOT SE 1) = %{c_stot_se1:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 1 (H370)")
        elif scl_stot_se2 is not None:
            sub_name, sub_c, sub_scl = scl_stot_se2
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 2",
                h_kodu="H371"
            ))
            result.piktogramlar.append("GHS08")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT SE (SCL): [{sub_name}] %{sub_c:.1f} >= SCL (%{sub_scl:.1f}) -> Spesifik Konsantrasyon Sınırı ile sınıflandırıldı: Kategori 2 (H371)")
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

        # STOT SE 3 - Solunum Yolu Tahrişi (H335)
        if scl_stot_se3_335 is not None:
            sub_name, sub_c, sub_scl = scl_stot_se3_335
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 3",
                h_kodu="H335"
            ))
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT SE 3 (RTI - SCL): [{sub_name}] %{sub_c:.1f} >= SCL (%{sub_scl:.1f}) -> Spesifik Konsantrasyon Sınırı ile sınıflandırıldı: Kategori 3 (H335)")
        elif c_stot_se3_335 >= 20.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 3",
                h_kodu="H335"
            ))
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT SE: ∑(H335) = %{c_stot_se3_335:.1f} >= %20.0 -> Sınıflandırıldı: Kategori 3 (H335)")

        # STOT SE 3 - Narkotik Etkiler (H336)
        if scl_stot_se3_336 is not None:
            sub_name, sub_c, sub_scl = scl_stot_se3_336
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 3",
                h_kodu="H336"
            ))
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT SE 3 (NE - SCL): [{sub_name}] %{sub_c:.1f} >= SCL (%{sub_scl:.1f}) -> Spesifik Konsantrasyon Sınırı ile sınıflandırıldı: Kategori 3 (H336)")
        elif c_stot_se3_336 >= 20.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma",
                kategori="Kategori 3",
                h_kodu="H336"
            ))
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT SE: ∑(H336) = %{c_stot_se3_336:.1f} >= %20.0 -> Sınıflandırıldı: Kategori 3 (H336)")

        # STOT RE Sınıflandırma Değerlendirmesi
        if scl_stot_re1 is not None:
            sub_name, sub_c, sub_scl = scl_stot_re1
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tekrarlı Maruz Kalma",
                kategori="Kategori 1",
                h_kodu="H372"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(f"• STOT RE (SCL): [{sub_name}] %{sub_c:.1f} >= SCL (%{sub_scl:.1f}) -> Spesifik Konsantrasyon Sınırı ile sınıflandırıldı: Kategori 1 (H372)")
        elif c_stot_re1 >= 10.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tekrarlı Maruz Kalma",
                kategori="Kategori 1",
                h_kodu="H372"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(f"• STOT RE: ∑(STOT RE 1) = %{c_stot_re1:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 1 (H372)")
        elif scl_stot_re2 is not None:
            sub_name, sub_c, sub_scl = scl_stot_re2
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tekrarlı Maruz Kalma",
                kategori="Kategori 2",
                h_kodu="H373"
            ))
            result.piktogramlar.append("GHS08")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT RE (SCL): [{sub_name}] %{sub_c:.1f} >= SCL (%{sub_scl:.1f}) -> Spesifik Konsantrasyon Sınırı ile sınıflandırıldı: Kategori 2 (H373)")
        elif c_stot_re2 >= 10.0 or (1.0 <= c_stot_re1 < 10.0):
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Belirli Hedef Organ Toksisitesi - Tekrarlı Maruz Kalma",
                kategori="Kategori 2",
                h_kodu="H373"
            ))
            result.piktogramlar.append("GHS08")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• STOT RE: ∑(STOT RE 2) = %{c_stot_re2:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 2 (H373)")

        uncertain_substances = [s for s in substances if s.data_quality and s.data_quality.quality_level == "UNCERTAIN"]
        component_qualities = {s.name: s.data_quality.quality_level for s in substances if s.data_quality}

        result.evidence = {
            "c_stot_se1": round(c_stot_se1, 2),
            "c_stot_se2": round(c_stot_se2, 2),
            "c_stot_se3_335": round(c_stot_se3_335, 2),
            "c_stot_se3_336": round(c_stot_se3_336, 2),
            "c_stot_re1": round(c_stot_re1, 2),
            "c_stot_re2": round(c_stot_re2, 2),
            "scl_stot_se1": scl_stot_se1,
            "scl_stot_se2": scl_stot_se2,
            "scl_stot_se3_335": scl_stot_se3_335,
            "scl_stot_se3_336": scl_stot_se3_336,
            "scl_stot_re1": scl_stot_re1,
            "scl_stot_re2": scl_stot_re2,
            "component_data_qualities": component_qualities,
            "has_uncertain_data": len(uncertain_substances) > 0,
        }

        result.calculations = [
            {
                "parameter": "c_stot_se1",
                "description": "Toplam STOT SE 1 Konsantrasyonu",
                "value": round(c_stot_se1, 2),
                "threshold": 10.0,
                "threshold_met": c_stot_se1 >= 10.0,
            },
            {
                "parameter": "c_stot_se2",
                "description": "Toplam STOT SE 2 Konsantrasyonu",
                "value": round(c_stot_se2, 2),
                "threshold": 10.0,
                "threshold_met": c_stot_se2 >= 10.0,
            },
            {
                "parameter": "c_stot_se3_335",
                "description": "STOT SE 3 Solunum Yolu Tahrişi (RTI - H335)",
                "value": round(c_stot_se3_335, 2),
                "threshold": 20.0,
                "threshold_met": c_stot_se3_335 >= 20.0,
            },
            {
                "parameter": "c_stot_se3_336",
                "description": "STOT SE 3 Narkotik Etkiler (NE - H336)",
                "value": round(c_stot_se3_336, 2),
                "threshold": 20.0,
                "threshold_met": c_stot_se3_336 >= 20.0,
            },
            {
                "parameter": "c_stot_re1",
                "description": "Toplam STOT RE 1 Konsantrasyonu",
                "value": round(c_stot_re1, 2),
                "threshold": 10.0,
                "threshold_met": c_stot_re1 >= 10.0,
            },
            {
                "parameter": "c_stot_re2",
                "description": "Toplam STOT RE 2 Konsantrasyonu",
                "value": round(c_stot_re2, 2),
                "threshold": 10.0,
                "threshold_met": c_stot_re2 >= 10.0,
            },
        ]

        if result.hazards:
            result.status = "SUFFICIENT"
            result.decision = "; ".join(f"{h.zararlilik_sinifi} {h.kategori} ({h.h_kodu})" for h in result.hazards)
            result.reason = "STOT eşik veya SCL değerleri aşıldı."
        elif (c_stot_se1 > 0 or c_stot_se2 > 0 or c_stot_se3_335 > 0 or c_stot_se3_336 > 0 or c_stot_re1 > 0 or c_stot_re2 > 0):
            result.status = "SUFFICIENT"
            result.decision = None
            result.reason = "STOT bileşenleri mevcut ancak eşik değerler aşılmadı."
        else:
            result.status = "NOT_APPLICABLE"
            result.decision = None
            result.reason = "STOT zararlılığı taşıyan bileşen bulunmamaktadır."

        return result
