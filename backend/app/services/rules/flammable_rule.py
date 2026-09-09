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
        fp = context.parlama_noktasi
        bp = context.kaynama_noktasi

        # Bileşenlerde alevlenir madde var mı kontrolü
        flam_components = [
            s for s in substances
            if any(h.hazard_class.startswith("Flam") or h.h_code in ["H224", "H225", "H226"] for h in s.hazards) or
               any(c in s.raw_h_codes for c in ["H224", "H225", "H226"])
        ]

        if fp is not None:
            if fp < 23.0:
                if bp is not None:
                    if bp <= 35.0:
                        result.data_status = "SUFFICIENT"
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
                        result.data_status = "SUFFICIENT"
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
                    result.data_status = "INSUFFICIENT_DATA"
                    result.calculation_notes.append(
                        f"• Alevlenir Sıvı: Parlama Noktası ({fp}°C < 23°C) ölçülmüş olmasına rağmen başlangıç kaynama noktası girilmediğinden (Bilinmiyor / UNKNOWN) Kategori 1 (H224, KN <= 35°C) ile Kategori 2 (H225, KN > 35°C) arasında kesin ayrım yapılamamıştır (INSUFFICIENT_DATA). SEA Ek-1 Tablo 2.6.1 uyarınca kaynama noktası test verisi girilmelidir."
                    )
            elif 23.0 <= fp <= 60.0:
                result.data_status = "SUFFICIENT"
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
                result.data_status = "SUFFICIENT"
                result.calculation_notes.append(
                    f"• Alevlenir Sıvı: Parlama Noktası ({fp}°C > 60°C) -> Alevlenir sınıflandırma kriterini karşılamıyor."
                )
        else:
            if flam_components:
                result.data_status = "INSUFFICIENT_DATA"
                comp_names = ", ".join([f"{s.name} (%{s.concentration.value:.1f})" for s in flam_components])
                result.calculation_notes.append(
                    f"• Alevlenir Sıvı: Karışımda alevlenir bileşenler ({comp_names}) bulunmasına rağmen ölçülmüş parlama noktası girilmediği için otomatik sınıflandırma yapılmamıştır (Fiziksel tehlikeler için test verisi zorunludur)."
                )
            else:
                result.data_status = "NOT_APPLICABLE"

        return result
