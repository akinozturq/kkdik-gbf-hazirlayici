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
        result.source_references = ["SEA Ek-1 Bölüm 3.10.3.3", "CLP Annex I Table 3.10.1"]
        result.assumptions = [
            "SEA Ek-1 Bölüm 3.10.3.3: Karışımın Kategori 1 olarak sınıflandırılması için ∑(Asp. Tox. 1) >= %10.0 VE 40°C kinematik viskozite <= 20.5 mm²/s olmalıdır."
        ]

        c_asp_tox_1 = sum(
            s.concentration.value for s in substances
            if "H304" in s.raw_h_codes or any(h.h_code == "H304" or "Asp" in h.hazard_class for h in s.hazards)
        )

        visk = context.kinematik_viskozite_40c

        uncertain_substances = [s for s in substances if s.data_quality and s.data_quality.quality_level == "UNCERTAIN"]
        component_qualities = {s.name: s.data_quality.quality_level for s in substances if s.data_quality}

        if uncertain_substances:
            names = ", ".join(f"{s.name} (UNCERTAIN)" for s in uncertain_substances)
            result.assumptions.append(
                f"Veri Kalitesi (DATA QUALITY): Karışımdaki {names} konsantrasyon aralığına bağlı olarak belirsiz (UNCERTAIN) kabul edilmiştir."
            )

        result.evidence = {
            "aspiration_category_1_sum": round(c_asp_tox_1, 2),
            "required_threshold": 10.0,
            "viscosity_40c": visk,
            "viscosity_threshold": 20.5,
            "component_data_qualities": component_qualities,
            "has_uncertain_data": len(uncertain_substances) > 0,
        }

        result.calculations = [
            {
                "parameter": "c_asp_tox_1",
                "description": "Toplam Kategori 1 Aspirasyon Toksisitesi Bileşenleri Konsantrasyonu",
                "value": round(c_asp_tox_1, 2),
                "threshold": 10.0,
                "threshold_met": c_asp_tox_1 >= 10.0,
            },
            {
                "parameter": "kinematik_viskozite_40c",
                "description": "40°C Kinematik Viskozite (mm²/s)",
                "value": visk,
                "threshold": 20.5,
                "criteria_met": (visk <= 20.5) if visk is not None else None,
            }
        ]

        if c_asp_tox_1 >= 10.0:
            if visk is not None:
                result.status = "SUFFICIENT"
                if visk <= 20.5:
                    result.decision = "Asp. Tox. 1 H304"
                    result.reason = f"∑(Asp. Tox. 1) = %{c_asp_tox_1:.1f} >= %10.0 ve 40°C kinematik viskozite ({visk:.1f} mm²/s <= 20.5 mm²/s) kriterlerini sağlıyor."
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
                    result.decision = None
                    result.reason = f"Karışımda %{c_asp_tox_1:.1f} Asp. Tox. 1 bileşeni bulunmasına rağmen, 40°C kinematik viskozite ({visk:.1f} mm²/s > 20.5 mm²/s) eşiğin üzerindedir."
                    result.calculation_notes.append(
                        f"• Aspirasyon Zararı: Karışımda %{c_asp_tox_1:.1f} Asp. Tox. 1 bileşeni bulunmasına rağmen, 40°C kinematik viskozite ({visk:.1f} mm²/s > 20.5 mm²/s) eşiğin üzerinde olduğu için H304 olarak SINIFLANDIRILMAMIŞTIR (SEA Ek-1 Bölüm 3.10.3.3.1)."
                    )
            else:
                result.status = "INDETERMINATE"
                result.decision = None
                result.reason = "Kinematik viskozite verisi eksik"
                result.calculation_notes.append(
                    f"• Aspirasyon Zararı: Karışımda ∑(Asp. Tox. 1) = %{c_asp_tox_1:.1f} >= %10.0 bileşen bulunmasına rağmen 40°C kinematik viskozite test verisi girilmediğinden (Bilinmiyor / UNKNOWN) sınıflandırma yapılamamıştır (INDETERMINATE / INSUFFICIENT_DATA). ECHA ve SEA Ek-1 Bölüm 3.10 uyarınca kinematik viskozitenin <= 20.5 mm²/s olduğu test edilip doğrulanmalıdır."
                )
        elif c_asp_tox_1 > 0:
            result.status = "SUFFICIENT"
            result.decision = None
            result.reason = f"∑(Asp. Tox. 1) = %{c_asp_tox_1:.1f} < %10.0 eşik değer aşılmadı."
            result.calculation_notes.append(
                f"• Aspirasyon Zararı: ∑(Asp. Tox. 1) = %{c_asp_tox_1:.1f} < %10.0 -> Eşik değer aşılmadı."
            )
        else:
            result.status = "NOT_APPLICABLE"
            result.decision = None
            result.reason = "Aspirasyon zararlılığı taşıyan bileşen bulunmamaktadır."

        return result
