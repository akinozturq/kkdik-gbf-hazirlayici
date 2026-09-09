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
        result.source_references = [
            "SEA Ek-1 Bölüm 3.5, 3.6 & 3.7",
            "CLP Annex I Table 3.5.2, 3.6.2 & 3.7.2"
        ]
        result.assumptions = [
            "CMR tehlike sınıflarında toplanabilirlik uygulanmaz; her bileşenin genel veya özel konsantrasyon sınırını bağımsız olarak aşması gerekir.",
            "Bileşenin CMR alt kategorisi (1A/1B) teyit edilemiyorsa CATEGORY_UNRESOLVED olarak işaretlenir."
        ]

        c_muta1a = 0.0
        c_muta1b = 0.0
        c_muta2 = 0.0

        c_carc1a = 0.0
        c_carc1b = 0.0
        c_carc2 = 0.0

        c_muta1a = 0.0
        c_muta1b = 0.0
        c_muta1_unresolved = 0.0
        c_muta2 = 0.0

        c_carc1a = 0.0
        c_carc1b = 0.0
        c_carc1_unresolved = 0.0
        c_carc2 = 0.0

        c_repr1a = 0.0
        c_repr1b = 0.0
        c_repr1_unresolved = 0.0
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

            has_scl_muta = False
            has_scl_carc = False
            has_scl_repr = False

            # SCL Kontrolleri
            for h in s.hazards:
                if h.scl is not None:
                    cat_val = h.category if h.category and h.category != "CATEGORY_UNRESOLVED" else "CATEGORY_UNRESOLVED"
                    if h.h_code in ["H340", "H341"] or "Muta" in h.hazard_class:
                        has_scl_muta = True
                        if conc >= h.scl:
                            scl_muta = (s.name, conc, h.scl, cat_val, h.h_code or "H340")
                    elif h.h_code in ["H350", "H350i", "H351"] or "Carc" in h.hazard_class:
                        has_scl_carc = True
                        if conc >= h.scl:
                            scl_carc = (s.name, conc, h.scl, cat_val, h.h_code or "H350")
                    elif any(h.h_code.startswith(p) for p in ["H360", "H361"]) or "Repr" in h.hazard_class:
                        has_scl_repr = True
                        if conc >= h.scl:
                            scl_repr = (s.name, conc, h.scl, cat_val, h.h_code or "H360D")

            # Mutajenite
            if not has_scl_muta:
                if "H340" in codes or any("Muta" in h.hazard_class and ("1" in (h.category or "") or (h.category or "") == "CATEGORY_UNRESOLVED") for h in s.hazards):
                    if any("1A" in (h.category or "").upper() for h in s.hazards) or "1A" in hazard_classes_str.upper():
                        c_muta1a += conc
                    elif any("1B" in (h.category or "").upper() for h in s.hazards) or "1B" in hazard_classes_str.upper():
                        c_muta1b += conc
                    else:
                        c_muta1_unresolved += conc
                if "H341" in codes:
                    c_muta2 += conc

            # Kanserojenlik
            if not has_scl_carc:
                if "H350" in codes or "H350i" in codes or any("Carc" in h.hazard_class and ("1" in (h.category or "") or (h.category or "") == "CATEGORY_UNRESOLVED") for h in s.hazards):
                    if any("1A" in (h.category or "").upper() for h in s.hazards) or "1A" in hazard_classes_str.upper():
                        c_carc1a += conc
                    elif any("1B" in (h.category or "").upper() for h in s.hazards) or "1B" in hazard_classes_str.upper():
                        c_carc1b += conc
                    else:
                        c_carc1_unresolved += conc
                if "H351" in codes:
                    c_carc2 += conc

            # Üreme Toksisitesi
            if not has_scl_repr:
                if any(c.startswith("H360") for c in codes) or any("Repr" in h.hazard_class and ("1" in (h.category or "") or (h.category or "") == "CATEGORY_UNRESOLVED") for h in s.hazards):
                    if any("1A" in (h.category or "").upper() for h in s.hazards) or "1A" in hazard_classes_str.upper():
                        c_repr1a += conc
                    elif any("1B" in (h.category or "").upper() for h in s.hazards) or "1B" in hazard_classes_str.upper():
                        c_repr1b += conc
                    else:
                        c_repr1_unresolved += conc
                    for c in codes:
                        if c.startswith("H360"):
                            repr_h360_codes.add(c)
                if any(c.startswith("H361") for c in codes):
                    c_repr2 += conc
                    for c in codes:
                        if c.startswith("H361"):
                            repr_h361_codes.add(c)

        # 1. MUTAJENİTE
        total_muta1 = c_muta1a + c_muta1b + c_muta1_unresolved
        if scl_muta is not None:
            sub_name, sub_c, sub_scl, sub_cat, sub_h = scl_muta
            cat_name = "CATEGORY_UNRESOLVED" if sub_cat == "CATEGORY_UNRESOLVED" else (
                f"Kategori {sub_cat}" if "Kategori" not in sub_cat else sub_cat
            )
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Eşey Hücre Mutajenitesi",
                kategori=cat_name,
                h_kodu=sub_h
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            note_label = "1A/1B (CATEGORY_UNRESOLVED)" if cat_name == "CATEGORY_UNRESOLVED" else cat_name
            result.calculation_notes.append(f"• Mutajenite (SCL): [{sub_name}] %{sub_c:.2f} >= SCL (%{sub_scl:.2f}) -> {note_label} ({sub_h})")
        elif total_muta1 >= 0.1:
            if c_muta1a >= 0.1:
                muta_cat = "Kategori 1A"
            elif c_muta1b >= 0.1 and c_muta1_unresolved == 0:
                muta_cat = "Kategori 1B"
            else:
                muta_cat = "CATEGORY_UNRESOLVED"

            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Eşey Hücre Mutajenitesi",
                kategori=muta_cat,
                h_kodu="H340"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            if muta_cat == "CATEGORY_UNRESOLVED":
                result.calculation_notes.append(
                    f"• Mutajenite: ∑(Muta 1) = %{total_muta1:.1f} >= %0.1 -> Sınıflandırıldı: CATEGORY_UNRESOLVED (H340) "
                    "[Bileşen verisinde 1A/1B alt kategorisi belirtilmediğinden H340 üzerinden kesin alt kategori çözümlenemedi]"
                )
            else:
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
        total_carc1 = c_carc1a + c_carc1b + c_carc1_unresolved
        if scl_carc is not None:
            sub_name, sub_c, sub_scl, sub_cat, sub_h = scl_carc
            cat_name = "CATEGORY_UNRESOLVED" if sub_cat == "CATEGORY_UNRESOLVED" else (
                f"Kategori {sub_cat}" if "Kategori" not in sub_cat else sub_cat
            )
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Kanserojenite",
                kategori=cat_name,
                h_kodu=sub_h
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            note_label = "1A/1B (CATEGORY_UNRESOLVED)" if cat_name == "CATEGORY_UNRESOLVED" else cat_name
            result.calculation_notes.append(f"• Kanserojenite (SCL): [{sub_name}] %{sub_c:.2f} >= SCL (%{sub_scl:.2f}) -> {note_label} ({sub_h})")
        elif total_carc1 >= 0.1:
            if c_carc1a >= 0.1:
                carc_cat = "Kategori 1A"
            elif c_carc1b >= 0.1 and c_carc1_unresolved == 0:
                carc_cat = "Kategori 1B"
            else:
                carc_cat = "CATEGORY_UNRESOLVED"

            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Kanserojenite",
                kategori=carc_cat,
                h_kodu="H350"
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            if carc_cat == "CATEGORY_UNRESOLVED":
                result.calculation_notes.append(
                    f"• Kanserojenite: ∑(Carc 1) = %{total_carc1:.1f} >= %0.1 -> Sınıflandırıldı: CATEGORY_UNRESOLVED (H350) "
                    "[Bileşen verisinde 1A/1B alt kategorisi belirtilmediğinden H350 üzerinden kesin alt kategori çözümlenemedi]"
                )
            else:
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
        total_repr1 = c_repr1a + c_repr1b + c_repr1_unresolved
        if scl_repr is not None:
            sub_name, sub_c, sub_scl, sub_cat, sub_h = scl_repr
            cat_name = "CATEGORY_UNRESOLVED" if sub_cat == "CATEGORY_UNRESOLVED" else (
                f"Kategori {sub_cat}" if "Kategori" not in sub_cat else sub_cat
            )
            h_repr = sub_h
            if ("1" in cat_name or cat_name == "CATEGORY_UNRESOLVED") and repr_h360_codes:
                h_repr = self.resolve_repro_h_code(repr_h360_codes, "H360")
            elif "2" in cat_name and repr_h361_codes:
                h_repr = self.resolve_repro_h_code(repr_h361_codes, "H361")
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Üreme Sistemi Toksisitesi",
                kategori=cat_name,
                h_kodu=h_repr
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            note_label = "1A/1B (CATEGORY_UNRESOLVED)" if cat_name == "CATEGORY_UNRESOLVED" else cat_name
            result.calculation_notes.append(f"• Üreme Toksisitesi (SCL): [{sub_name}] %{sub_c:.2f} >= SCL (%{sub_scl:.2f}) -> {note_label} ({h_repr})")
        elif total_repr1 >= 0.3:
            if c_repr1a >= 0.3:
                repr_cat = "Kategori 1A"
            elif c_repr1b >= 0.3 and c_repr1_unresolved == 0:
                repr_cat = "Kategori 1B"
            else:
                repr_cat = "CATEGORY_UNRESOLVED"

            h_repr = self.resolve_repro_h_code(repr_h360_codes, "H360")
            result.hazards.append(ClassifiedHazard(
                zararlilik_sinifi="Üreme Sistemi Toksisitesi",
                kategori=repr_cat,
                h_kodu=h_repr
            ))
            result.piktogramlar.append("GHS08")
            result.uyari_kelimesi = "Tehlike"
            if repr_cat == "CATEGORY_UNRESOLVED":
                result.calculation_notes.append(
                    f"• Üreme Toksisitesi: ∑(Repr 1) = %{total_repr1:.1f} >= %0.3 -> Sınıflandırıldı: CATEGORY_UNRESOLVED ({h_repr}) "
                    "[Bileşen verisinde 1A/1B alt kategorisi belirtilmediğinden H360 üzerinden kesin alt kategori çözümlenemedi]"
                )
            else:
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

        result.evidence = {
            "c_muta1a": round(c_muta1a, 2),
            "c_muta1b": round(c_muta1b, 2),
            "c_muta1_unresolved": round(c_muta1_unresolved, 2),
            "c_muta2": round(c_muta2, 2),
            "c_carc1a": round(c_carc1a, 2),
            "c_carc1b": round(c_carc1b, 2),
            "c_carc1_unresolved": round(c_carc1_unresolved, 2),
            "c_carc2": round(c_carc2, 2),
            "c_repr1a": round(c_repr1a, 2),
            "c_repr1b": round(c_repr1b, 2),
            "c_repr1_unresolved": round(c_repr1_unresolved, 2),
            "c_repr2": round(c_repr2, 2),
        }

        result.calculations = [
            {"parameter": "muta1_sum", "value": round(c_muta1a + c_muta1b + c_muta1_unresolved, 2), "threshold": 0.1},
            {"parameter": "muta2_sum", "value": round(c_muta2, 2), "threshold": 1.0},
            {"parameter": "carc1_sum", "value": round(c_carc1a + c_carc1b + c_carc1_unresolved, 2), "threshold": 0.1},
            {"parameter": "carc2_sum", "value": round(c_carc2, 2), "threshold": 1.0},
            {"parameter": "repr1_sum", "value": round(c_repr1a + c_repr1b + c_repr1_unresolved, 2), "threshold": 0.3},
            {"parameter": "repr2_sum", "value": round(c_repr2, 2), "threshold": 3.0},
        ]

        has_unresolved = any(h.kategori == "CATEGORY_UNRESOLVED" for h in result.hazards)
        has_any_cmr = (
            (c_muta1a + c_muta1b + c_muta1_unresolved + c_muta2) > 0 or
            (c_carc1a + c_carc1b + c_carc1_unresolved + c_carc2) > 0 or
            (c_repr1a + c_repr1b + c_repr1_unresolved + c_repr2) > 0
        )

        if has_unresolved:
            result.status = "INDETERMINATE"
            result.decision = "; ".join(f"{h.zararlilik_sinifi} {h.kategori} ({h.h_kodu})" for h in result.hazards)
            result.reason = "CMR bileşeni eşiği aştı ancak alt kategori (1A/1B) veri kaynağında eksik olduğu için kesinleştirilemedi (CATEGORY_UNRESOLVED)."
        elif result.hazards:
            result.status = "SUFFICIENT"
            result.decision = "; ".join(f"{h.zararlilik_sinifi} {h.kategori} ({h.h_kodu})" for h in result.hazards)
            result.reason = "CMR konsantrasyon sınırları aşıldı."
        elif has_any_cmr:
            result.status = "SUFFICIENT"
            result.decision = None
            result.reason = "CMR bileşenleri mevcut ancak konsantrasyon sınırlarının altında."
        else:
            result.status = "NOT_APPLICABLE"
            result.decision = None
            result.reason = "CMR zararlılığı taşıyan bileşen bulunmamaktadır."

        return result
