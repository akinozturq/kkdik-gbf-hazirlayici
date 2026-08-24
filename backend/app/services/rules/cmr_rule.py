"""
CMR Kural Stratejisi (Carc, Muta, Repr Rule - SEA Ek-1 Bölüm 3.5, 3.6 & 3.7)
"""

from typing import List, Set
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult, ClassifiedHazard
from app.services.rules.base_rule import BaseHazardRule


class CMRRule(BaseHazardRule):
    """
    - Mutajenite: Muta 1A/1B >= %0.1 -> Kat 1A/1B (H340), Muta 2 >= %1.0 -> Kat 2 (H341)
    - Kanserojenlik: Carc 1A/1B >= %0.1 -> Kat 1A/1B (H350), Carc 2 >= %1.0 -> Kat 2 (H351)
    - Üreme Toksisitesi: Repr 1A/1B >= %0.3 -> Kat 1A/1B (H360...), Repr 2 >= %3.0 -> Kat 2 (H361...)
    - Deterministik Repro H-kodu önceliği: H360FD > H360Fd > H360Df > H360F > H360D
    """

    @property
    def rule_name(self) -> str:
        return "CMRRule"

    @classmethod
    def resolve_repro_h_code(cls, found_codes: Set[str], prefix: str = "H360") -> str:
        if prefix == "H360":
            priority = ["H360FD", "H360Fd", "H360Df", "H360F", "H360D", "H360"]
        else:
            priority = ["H361fd", "H361f", "H361d", "H361"]

        for p in priority:
            for c in found_codes:
                if c.upper() == p.upper():
                    return p
        return "H360D" if prefix == "H360" else "H361d"

    def evaluate(
        self,
        context: CalculationContext,
        substances: List[StructuredSubstance]
    ) -> RuleResult:
        result = RuleResult(rule_name=self.rule_name)

        c_muta1a = 0.0
        c_muta1b = 0.0
        c_muta2 = 0.0

        c_carc1a = 0.0
        c_carc1b = 0.0
        c_carc2 = 0.0

        c_repr1a = 0.0
        c_repr1b = 0.0
        c_repr2 = 0.0

        repr_h360_codes: Set[str] = set()
        repr_h361_codes: Set[str] = set()

        scl_muta = None
        scl_carc = None
        scl_repr = None

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])
            hazard_classes_str = " ".join([h.hazard_class for h in s.hazards])

            # SCL Kontrolleri
            for h in s.hazards:
                if h.scl is not None:
                    if h.h_code in ["H340", "H341"] or "Muta" in h.hazard_class:
                        if conc >= h.scl:
                            scl_muta = (s.name, conc, h.scl, h.category or "1B", h.h_code or "H340")
                    elif h.h_code in ["H350", "H350i", "H351"] or "Carc" in h.hazard_class:
                        if conc >= h.scl:
                            scl_carc = (s.name, conc, h.scl, h.category or "1B", h.h_code or "H350")
                    elif any(h.h_code.startswith(p) for p in ["H360", "H361"]) or "Repr" in h.hazard_class:
                        if conc >= h.scl:
                            scl_repr = (s.name, conc, h.scl, h.category or "1B", h.h_code or "H360D")

            # Mutajenite
            if "H340" in codes:
                if any("1A" in h.category.upper() for h in s.hazards) or "1A" in hazard_classes_str.upper():
                    c_muta1a += conc
                else:
                    c_muta1b += conc
            if "H341" in codes:
                c_muta2 += conc

            # Kanserojenlik
            if "H350" in codes or "H350i" in codes:
                if any("1A" in h.category.upper() for h in s.hazards) or "1A" in hazard_classes_str.upper():
                    c_carc1a += conc
                else:
                    c_carc1b += conc
            if "H351" in codes:
                c_carc2 += conc

            # Üreme Toksisitesi
            if any(c.startswith("H360") for c in codes):
                if any("1A" in h.category.upper() for h in s.hazards) or "1A" in hazard_classes_str.upper():
                    c_repr1a += conc
                else:
                    c_repr1b += conc
                for c in codes:
                    if c.startswith("H360"):
                        repr_h360_codes.add(c)
            if any(c.startswith("H361") for c in codes):
                c_repr2 += conc
                for c in codes:
                    if c.startswith("H361"):
                        repr_h361_codes.add(c)

        # 1. MUTAJENİTE
        total_muta1 = c_muta1a + c_muta1b
        if scl_muta is not None:
            sub_name, sub_c, sub_scl, sub_cat, sub_h = scl_muta
            cat_name = f"Kategori {sub_cat}" if "Kategori" not in sub_cat else sub_cat
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Eşey Hücre Mutajenitesi",
                kategori=cat_name,
                h_kodu=sub_h
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike" if "1" in cat_name else "Dikkat"
            result.calculation_notes.append(f"• Mutajenite (SCL): [{sub_name}] %{sub_c:.2f} >= SCL (%{sub_scl:.2f}) -> {cat_name} ({sub_h})")
        elif total_muta1 >= 0.1:
            muta_cat = "Kategori 1A" if c_muta1a >= 0.1 else "Kategori 1B"
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Eşey Hücre Mutajenitesi",
                kategori=muta_cat,
                h_kodu="H340"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(f"• Mutajenite: ∑(Muta 1) = %{total_muta1:.1f} >= %0.1 -> Sınıflandırıldı: {muta_cat} (H340)")
        elif c_muta2 >= 1.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Eşey Hücre Mutajenitesi",
                kategori="Kategori 2",
                h_kodu="H341"
            ))
            result.piktogramlar.append("GHS08")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• Mutajenite: ∑(Muta 2) = %{c_muta2:.1f} >= %1.0 -> Sınıflandırıldı: Kategori 2 (H341)")

        # 2. KANSEROJENLİK
        total_carc1 = c_carc1a + c_carc1b
        if scl_carc is not None:
            sub_name, sub_c, sub_scl, sub_cat, sub_h = scl_carc
            cat_name = f"Kategori {sub_cat}" if "Kategori" not in sub_cat else sub_cat
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Kanserojenite",
                kategori=cat_name,
                h_kodu=sub_h
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike" if "1" in cat_name else "Dikkat"
            result.calculation_notes.append(f"• Kanserojenite (SCL): [{sub_name}] %{sub_c:.2f} >= SCL (%{sub_scl:.2f}) -> {cat_name} ({sub_h})")
        elif total_carc1 >= 0.1:
            carc_cat = "Kategori 1A" if c_carc1a >= 0.1 else "Kategori 1B"
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Kanserojenite",
                kategori=carc_cat,
                h_kodu="H350"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(f"• Kanserojenite: ∑(Carc 1) = %{total_carc1:.1f} >= %0.1 -> Sınıflandırıldı: {carc_cat} (H350)")
        elif c_carc2 >= 1.0:
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Kanserojenite",
                kategori="Kategori 2",
                h_kodu="H351"
            ))
            result.piktogramlar.append("GHS08")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• Kanserojenite: ∑(Carc 2) = %{c_carc2:.1f} >= %1.0 -> Sınıflandırıldı: Kategori 2 (H351)")

        # 3. ÜREME TOKSİSİTESİ
        total_repr1 = c_repr1a + c_repr1b
        if scl_repr is not None:
            sub_name, sub_c, sub_scl, sub_cat, sub_h = scl_repr
            cat_name = f"Kategori {sub_cat}" if "Kategori" not in sub_cat else sub_cat
            h_repr = sub_h
            if "1" in cat_name and repr_h360_codes:
                h_repr = self.resolve_repro_h_code(repr_h360_codes, "H360")
            elif "2" in cat_name and repr_h361_codes:
                h_repr = self.resolve_repro_h_code(repr_h361_codes, "H361")
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Üreme Sistemi Toksisitesi",
                kategori=cat_name,
                h_kodu=h_repr
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike" if "1" in cat_name else "Dikkat"
            result.calculation_notes.append(f"• Üreme Toksisitesi (SCL): [{sub_name}] %{sub_c:.2f} >= SCL (%{sub_scl:.2f}) -> {cat_name} ({h_repr})")
        elif total_repr1 >= 0.3:
            repr_cat = "Kategori 1A" if c_repr1a >= 0.3 else "Kategori 1B"
            h_repr = self.resolve_repro_h_code(repr_h360_codes, "H360")
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Üreme Sistemi Toksisitesi",
                kategori=repr_cat,
                h_kodu=h_repr
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            result.calculation_notes.append(f"• Üreme Toksisitesi: ∑(Repr 1) = %{total_repr1:.1f} >= %0.3 -> Sınıflandırıldı: {repr_cat} ({h_repr})")
        elif c_repr2 >= 3.0:
            h_repr = self.resolve_repro_h_code(repr_h361_codes, "H361")
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Üreme Sistemi Toksisitesi",
                kategori="Kategori 2",
                h_kodu=h_repr
            ))
            result.piktogramlar.append("GHS08")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
            result.calculation_notes.append(f"• Üreme Toksisitesi: ∑(Repr 2) = %{c_repr2:.1f} >= %3.0 -> Sınıflandırıldı: Kategori 2 ({h_repr})")

        return result
