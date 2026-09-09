"""
Sucul Çevre Zararları Kural Stratejisi
(Aquatic Hazards Rule - SEA Ek-1 Bölüm 4.1)
"""

from typing import List
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult, ClassifiedHazard
from app.services.rules.base_rule import BaseHazardRule


class AquaticRule(BaseHazardRule):
    """
    SEA Ek-1 Tablo 4.1.1 & 4.1.2 Toplanabilirlik ve M-Faktörü Kuralları:
    - Akut Kategori 1 (H400): M x ∑Akut 1 >= %25
    - Kronik Kategori 1 (H410): M x ∑Kronik 1 >= %25
    - Kronik Kategori 2 (H411): (10 x M x ∑Kronik 1) + ∑Kronik 2 >= %25
    - Kronik Kategori 3 (H412): (100 x M x ∑Kronik 1) + (10 x ∑Kronik 2) + ∑Kronik 3 >= %25
    - Kronik Kategori 4 (H413): Toplam Kronik >= %25
    """

    @property
    def rule_name(self) -> str:
        return "AquaticRule"

    def evaluate(
        self,
        context: CalculationContext,
        substances: List[StructuredSubstance]
    ) -> RuleResult:
        result = RuleResult(rule_name=self.rule_name)

        c_aq_acute1 = 0.0
        c_aq_chronic1 = 0.0
        c_aq_chronic2 = 0.0
        c_aq_chronic3 = 0.0
        c_aq_chronic4 = 0.0

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])

            m_akut_obj = s.m_acute
            m_kronik_obj = s.m_chronic

            m_akut = m_akut_obj.effective_value
            m_kronik = m_kronik_obj.effective_value

            if "H400" in codes:
                c_aq_acute1 += conc * m_akut
                if m_akut_obj.source == "DEFAULT":
                    result.calculation_notes.append(
                        f"  ℹ️ [{s.name}] Sucul Akut 1 M-faktörü belirtilmediğinden denetim izi gereği "
                        f"varsayılan (value=null, effective_value=1.0, source='DEFAULT') uygulandı."
                    )
                else:
                    result.calculation_notes.append(
                        f"  ℹ️ [{s.name}] Sucul Akut 1 M-faktörü doğrulandı: "
                        f"(value={m_akut_obj.value:g}, effective_value={m_akut_obj.effective_value:g}, source='{m_akut_obj.source}')."
                    )

            if "H410" in codes:
                c_aq_chronic1 += conc * m_kronik
                if m_kronik_obj.source == "DEFAULT":
                    result.calculation_notes.append(
                        f"  ℹ️ [{s.name}] Sucul Kronik 1 M-faktörü belirtilmediğinden denetim izi gereği "
                        f"varsayılan (value=null, effective_value=1.0, source='DEFAULT') uygulandı."
                    )
                else:
                    result.calculation_notes.append(
                        f"  ℹ️ [{s.name}] Sucul Kronik 1 M-faktörü doğrulandı: "
                        f"(value={m_kronik_obj.value:g}, effective_value={m_kronik_obj.effective_value:g}, source='{m_kronik_obj.source}')."
                    )

            if "H411" in codes:
                c_aq_chronic2 += conc
            if "H412" in codes:
                c_aq_chronic3 += conc
            if "H413" in codes:
                c_aq_chronic4 += conc

        # H.1 - Akut Kategori 1 (H400)
        if c_aq_acute1 >= 25.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Sucul Ortama Zararlı - Akut",
                kategori="Akut Kategori 1",
                h_kodu="H400"
            ))
            result.piktogramlar.append("GHS09")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• Sucul Çevre (Akut): ∑(M x Akut 1) = %{c_aq_acute1:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Akut 1 (H400)")
        elif c_aq_acute1 > 0:
            result.calculation_notes.append(f"• Sucul Çevre (Akut): ∑(M x Akut 1) = %{c_aq_acute1:.1f} < %25.0 -> Eşik değer aşılmadı.")

        # H.2 - Kronik Kategoriler
        if c_aq_chronic1 >= 25.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Sucul Ortama Zararlı - Kronik",
                kategori="Kronik Kategori 1",
                h_kodu="H410"
            ))
            result.piktogramlar.append("GHS09")
            result.calculation_notes.append(f"• Sucul Çevre (Kronik): ∑(M x Kronik 1) = %{c_aq_chronic1:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 1 (H410)")
        elif (10.0 * c_aq_chronic1 + c_aq_chronic2) >= 25.0:
            chr2_sum = (10.0 * c_aq_chronic1 + c_aq_chronic2)
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Sucul Ortama Zararlı - Kronik",
                kategori="Kronik Kategori 2",
                h_kodu="H411"
            ))
            result.piktogramlar.append("GHS09")
            result.calculation_notes.append(f"• Sucul Çevre (Kronik): (10 x ∑M x Kronik 1) + ∑Kronik 2 = %{chr2_sum:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 2 (H411)")
        elif (100.0 * c_aq_chronic1 + 10.0 * c_aq_chronic2 + c_aq_chronic3) >= 25.0:
            chr3_sum = (100.0 * c_aq_chronic1 + 10.0 * c_aq_chronic2 + c_aq_chronic3)
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Sucul Ortama Zararlı - Kronik",
                kategori="Kronik Kategori 3",
                h_kodu="H412"
            ))
            result.calculation_notes.append(f"• Sucul Çevre (Kronik): (100 x ∑M x Kronik 1) + (10 x ∑Kronik 2) + ∑Kronik 3 = %{chr3_sum:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 3 (H412)")
        elif (c_aq_chronic1 + c_aq_chronic2 + c_aq_chronic3 + c_aq_chronic4) >= 25.0:
            chr4_sum = (c_aq_chronic1 + c_aq_chronic2 + c_aq_chronic3 + c_aq_chronic4)
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Sucul Ortama Zararlı - Kronik",
                kategori="Kronik Kategori 4",
                h_kodu="H413"
            ))
            result.calculation_notes.append(f"• Sucul Çevre (Kronik): Toplam Kronik = %{chr4_sum:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 4 (H413)")

        return result
