"""
Solunum ve Cilt Hassaslaşması Kural Stratejisi
(Sensitization Rule - SEA Ek-1 Bölüm 3.4)
"""

from typing import List
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult, ClassifiedHazard
from app.services.rules.base_rule import BaseHazardRule


class SensitizationRule(BaseHazardRule):
    """
    SEA Ek-1 Bölüm 3.4 & Ek-4 / CLP Ek-2 Bölüm 2.4:
    - İzosiyanat Varlığı (IsocyanatePresent) -> EUH204 ('İzosiyanat içerir. Alerjik reaksiyona yol açabilir')
      H334 konsantrasyon eşiğinden bağımsız olarak karışımdaki izosiyanat varlığına göre belirlenir.
    - Solunum Hassaslaştırıcı (H334): Kat 1 >= %0.2 -> Kategori 1 (H334)
    - %0.1 <= Resp Sens < %0.2 -> H334 sınıflandırılmaz; izosiyanat yoksa EUH208 etikete eklenir.
    - Cilt Hassaslaştırıcı (H317): Kat 1 >= %1.0 -> Kategori 1 (H317)
    - %0.1 <= Cilt Sens < %1.0 -> H317 sınıflandırılmaz; EUH208 etikete eklenir.
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
        iso_substances: List[str] = []

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])
            name_l = s.name.lower()

            # 1. İzosiyanat Varlığı Tespiti (Bağımsız Karar 1)
            is_iso = bool(
                s.is_isocyanate or
                "EUH204" in codes or
                any(h.h_code == "EUH204" for h in s.hazards) or
                any(iso in name_l for iso in ["izosiyanat", "isocyanate", "mdi", "tdi", "hdi", "ipdi"])
            )
            if is_iso:
                iso_substances.append(f"{s.name} (%{conc:g})")

            # 2. Solunum Hassaslaştırıcı Havuzu (Bağımsız Karar 2)
            if "H334" in codes:
                c_resp_sens_1 += conc

            # 3. Cilt Hassaslaştırıcı Havuzu
            if "H317" in codes:
                c_skin_sens_1 += conc

        # A. İZOSİYANAT DEĞERLENDİRMESİ (CLP Ek-2 Madde 2.4 / SEA Ek-4 - Bağımsız Karar)
        if iso_substances:
            if "EUH204" not in result.euh_codes:
                result.euh_codes.append("EUH204")
            result.calculation_notes.append(
                f"• İzosiyanat İçeriği (EUH204): Karışımda izosiyanat bileşeni ({', '.join(iso_substances)}) tespit edildiğinden "
                "CLP Ek-2 Bölüm 2.4 ve SEA Ek-4 uyarınca EUH204 ('İzosiyanat içerir. Alerjik reaksiyona yol açabilir.') etikete eklendi."
            )

        # B. SOLUNUM HASSASLAŞMASI (H334) DEĞERLENDİRMESİ (SEA Ek-1 Tablo 3.4.5 & 3.4.6 - Bağımsız Karar)
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
            if not iso_substances and "EUH208" not in result.euh_codes:
                result.euh_codes.append("EUH208")
                result.calculation_notes.append(
                    f"• Solunum Hassaslaşması: %0.1 <= ∑(Solunum Hassaslaştırıcı) = %{c_resp_sens_1:.2f} < %0.2 -> "
                    "H334 sınıflandırma eşiğinin altında ancak SEA Ek-4 uyarınca EUH208 ('Alerjik reaksiyona yol açabilir') etikete eklendi."
                )
            elif iso_substances:
                result.calculation_notes.append(
                    f"• Solunum Hassaslaşması: %0.1 <= ∑(Solunum Hassaslaştırıcı) = %{c_resp_sens_1:.2f} < %0.2 -> "
                    "H334 eşiği aşılmadı; alerjen uyarısı EUH204 tarafından kapsanmaktadır."
                )

        # C. CİLT HASSASLAŞMASI (H317) DEĞERLENDİRMESİ (SEA Ek-1 Tablo 3.4.5 & 3.4.6)
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
            if "EUH208" not in result.euh_codes and "EUH204" not in result.euh_codes:
                result.euh_codes.append("EUH208")
                result.calculation_notes.append(
                    f"• Cilt Hassaslaşması: %0.1 <= ∑(Cilt Hassaslaştırıcı) = %{c_skin_sens_1:.1f} < %1.0 -> "
                    "H317 eşiğinin altında ancak SEA Ek-4 uyarınca EUH208 etikete eklendi."
                )

        return result
