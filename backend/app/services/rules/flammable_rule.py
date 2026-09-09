"""
Alevlenir Sıvılar Kural Stratejisi (Flammable Liquids Rule - SEA Ek-1 Bölüm 2.6)
"""

from typing import List
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult, ClassifiedHazard
from app.services.rules.base_rule import BaseHazardRule


class FlammableLiquidRule(BaseHazardRule):
    """
    SEA Ek-1 Tablo 2.6.1:
    - Kategori 1 (H224): Parlama noktası < 23°C VE Başlangıç kaynama noktası <= 35°C
    - Kategori 2 (H225): Parlama noktası < 23°C VE Başlangıç kaynama noktası > 35°C
    - Kategori 3 (H226): 23°C <= Parlama noktası <= 60°C
    Fiziksel test verisi (parlama noktası) yoksa otomatik miras yapılmaz.
    """

    @property
    def rule_name(self) -> str:
        return "FlammableLiquidRule"

    def evaluate(
        self,
        context: CalculationContext,
        substances: List[StructuredSubstance]
    ) -> RuleResult:
        result = RuleResult(rule_name=self.rule_name)
        result.source_references = ["SEA Ek-1 Tablo 2.6.1", "CLP Annex I Table 2.6.1"]
        result.assumptions = [
            "Fiziksel tehlikeler (Alevlenir Sıvılar) için kural bazlı sınıflandırma ölçülen parlama ve kaynama noktası test verilerine dayanır; formülasyondan otomatik miras yapılamaz."
        ]

        fp = context.parlama_noktasi
        bp = context.kaynama_noktasi

        # Bileşenlerde alevlenir madde var mı kontrolü
        flam_components = [
            s for s in substances
            if any(h.hazard_class.startswith("Flam") or h.h_code in ["H224", "H225", "H226"] for h in s.hazards) or
               any(c in s.raw_h_codes for c in ["H224", "H225", "H226"])
        ]

        uncertain_flam = [s for s in flam_components if s.data_quality and s.data_quality.quality_level == "UNCERTAIN"]
        flam_qualities = {s.name: s.data_quality.quality_level for s in flam_components if s.data_quality}

        result.evidence = {
            "flash_point": fp,
            "boiling_point": bp,
            "flammable_components_count": len(flam_components),
            "flammable_components": [f"{s.name} (%{s.concentration.value:g})" for s in flam_components],
            "component_data_qualities": flam_qualities,
            "has_uncertain_data": len(uncertain_flam) > 0,
        }

        result.calculations = [
            {
                "parameter": "parlama_noktasi",
                "description": "Ölçülen Parlama Noktası (°C)",
                "value": fp,
            },
            {
                "parameter": "kaynama_noktasi",
                "description": "Başlangıç Kaynama Noktası (°C)",
                "value": bp,
            }
        ]

        if fp is not None:
            if fp < 23.0:
                if bp is not None:
                    if bp <= 35.0:
                        result.status = "SUFFICIENT"
                        result.decision = "Flam. Liq. 1 H224"
                        result.reason = f"Parlama Noktası ({fp}°C < 23°C) ve Kaynama Noktası ({bp}°C <= 35°C) Kategori 1 kriterlerini sağlıyor."
                        result.hazards.append(ClassifiedHazard(
                            zararlilik_sinifi="Alevlenir Sıvılar",
                            kategori="Kategori 1",
                            h_kodu="H224"
                        ))
                        result.piktogramlar.append("GHS02")
                        result.uyari_kelimesi = "Tehlike"
                        result.calculation_notes.append(
                            f"• Alevlenir Sıvı: Parlama Noktası ({fp}°C < 23°C) ve Kaynama Noktası ({bp}°C <= 35°C) -> Kategori 1 (H224)"
                        )
                    else:
                        result.status = "SUFFICIENT"
                        result.decision = "Flam. Liq. 2 H225"
                        result.reason = f"Parlama Noktası ({fp}°C < 23°C) ve Kaynama Noktası ({bp}°C > 35°C) Kategori 2 kriterlerini sağlıyor."
                        result.hazards.append(ClassifiedHazard(
                            zararlilik_sinifi="Alevlenir Sıvılar",
                            kategori="Kategori 2",
                            h_kodu="H225"
                        ))
                        result.piktogramlar.append("GHS02")
                        result.uyari_kelimesi = "Tehlike"
                        result.calculation_notes.append(
                            f"• Alevlenir Sıvı: Parlama Noktası ({fp}°C < 23°C) ve Kaynama Noktası ({bp}°C > 35°C) -> Kategori 2 (H225)"
                        )
                else:
                    result.status = "INSUFFICIENT_DATA"
                    result.decision = None
                    result.reason = "Parlama noktası < 23°C ölçülmüş olmasına rağmen başlangıç kaynama noktası bilinmediğinden Kategori 1 ile Kategori 2 arasında kesin ayrım yapılamadı."
                    result.calculation_notes.append(
                        f"• Alevlenir Sıvı: Parlama Noktası ({fp}°C < 23°C) ölçülmüş olmasına rağmen başlangıç kaynama noktası girilmediğinden (Bilinmiyor / UNKNOWN) Kategori 1 (H224, KN <= 35°C) ile Kategori 2 (H225, KN > 35°C) arasında kesin ayrım yapılamamıştır (INSUFFICIENT_DATA). SEA Ek-1 Tablo 2.6.1 uyarınca kaynama noktası test verisi girilmelidir."
                    )
            elif 23.0 <= fp <= 60.0:
                result.status = "SUFFICIENT"
                result.decision = "Flam. Liq. 3 H226"
                result.reason = f"Parlama Noktası ({fp}°C, 23°C <= PN <= 60°C) Kategori 3 kriterlerini sağlıyor."
                result.hazards.append(ClassifiedHazard(
                    zararlilik_sinifi="Alevlenir Sıvılar",
                    kategori="Kategori 3",
                    h_kodu="H226"
                ))
                result.piktogramlar.append("GHS02")
                result.uyari_kelimesi = "Dikkat"
                result.calculation_notes.append(
                    f"• Alevlenir Sıvı: Parlama Noktası ({fp}°C, 23°C <= PN <= 60°C) -> Kategori 3 (H226)"
                )
            else:
                result.status = "SUFFICIENT"
                result.decision = None
                result.reason = f"Parlama Noktası ({fp}°C > 60°C) alevlenir sınıflandırma kriterini karşılamıyor."
                result.calculation_notes.append(
                    f"• Alevlenir Sıvı: Parlama Noktası ({fp}°C > 60°C) -> Alevlenir sınıflandırma kriterini karşılamıyor."
                )
        else:
            if flam_components:
                result.status = "INSUFFICIENT_DATA"
                result.decision = None
                result.reason = "Karışımda alevlenir bileşenler bulunmasına rağmen ölçülmüş parlama noktası test verisi girilmedi."
                comp_names = ", ".join([f"{s.name} (%{s.concentration.value:.1f})" for s in flam_components])
                result.calculation_notes.append(
                    f"• Alevlenir Sıvı: Karışımda alevlenir bileşenler ({comp_names}) bulunmasına rağmen ölçülmüş parlama noktası girilmediği için otomatik sınıflandırma yapılmamıştır (Fiziksel tehlikeler için test verisi zorunludur)."
                )
            else:
                result.status = "NOT_APPLICABLE"
                result.decision = None
                result.reason = "Alevlenir bileşen veya test verisi bulunmamaktadır."

        return result
