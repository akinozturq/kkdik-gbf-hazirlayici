"""
Akut Toksisite Kural Stratejisi (Acute Toxicity Rule - SEA Ek-1 Bölüm 3.1)
Harmonik Formül: 100 / ATE_mix = Σ(Ci / ATEi)
"""

from typing import List
from app.models.regulatory import (
    StructuredSubstance,
    CalculationContext,
    RuleResult,
    ClassifiedHazard,
    ATEProvenance
)
from app.services.rules.base_rule import BaseHazardRule


class AcuteToxicityRule(BaseHazardRule):
    """
    Oral, Dermal ve Soluma (Buhar, Gaz, Toz/Sis) yolları için ATE_mix hesaplar.
    Her bileşenin ATE değeri ve menşei (ATEProvenance - deneysel vs dönüştürülmüş)
    denetim izinde açıkça raporlanır.
    """

    ATE_CONVERSION_ORAL = {"H300": 5.0, "H301": 50.0, "H302": 500.0}
    ATE_CONVERSION_DERMAL = {"H310": 50.0, "H311": 200.0, "H312": 1100.0}
    ATE_CONVERSION_INHAL_VAPOUR = {"H330": 0.5, "H331": 3.0, "H332": 11.0}
    ATE_CONVERSION_INHAL_GAS = {"H330": 100.0, "H331": 700.0, "H332": 4500.0}
    ATE_CONVERSION_INHAL_DUST = {"H330": 0.05, "H331": 0.5, "H332": 1.5}

    @property
    def rule_name(self) -> str:
        return "AcuteToxicityRule"

    def evaluate(
        self,
        context: CalculationContext,
        substances: List[StructuredSubstance]
    ) -> RuleResult:
        result = RuleResult(rule_name=self.rule_name)
        result.source_references = [
            "SEA Ek-1 Bölüm 3.1.3.6 (Karışımların ATE Formülü)",
            "CLP Annex I Table 3.1.1 & 3.1.2"
        ]
        result.assumptions = [
            "Harmonik Formül: 100 / ATE_mix = Σ(Ci / ATEi).",
            "Deneysel ATE girilmemiş bileşenlerde mevzuat dönüşüm değerleri (SEA Ek-1 Tablo 3.1.2) uygulanır."
        ]

        ate_oral_sum = 0.0
        ate_dermal_sum = 0.0
        ate_inhal_vapour_sum = 0.0
        ate_inhal_gas_sum = 0.0
        ate_inhal_dust_sum = 0.0

        has_oral_inputs = False
        has_dermal_inputs = False
        has_inhal_vapour_inputs = False
        has_inhal_gas_inputs = False
        has_inhal_dust_inputs = False

        for s in substances:
            conc = s.concentration.value
            if conc <= 0:
                continue

            codes = set(s.raw_h_codes + [h.h_code for h in s.hazards])

            # 1. ORAL
            prov_oral = s.oral_ate_model
            if prov_oral is None:
                for h_code, conv in self.ATE_CONVERSION_ORAL.items():
                    if h_code in codes:
                        prov_oral = ATEProvenance.create_derived_conversion(
                            conv, h_code, route="oral", unit="mg/kg", source_ref="SEA_ANNEX_I"
                        )
                        break

            if prov_oral is not None and prov_oral.ate > 0:
                ate_oral_sum += conc / prov_oral.ate
                has_oral_inputs = True
                result.calculation_notes.append(
                    f"• Akut Toksisite (Oral Katkı): [{s.name}] %{conc:.1f}, ATE = {prov_oral.ate:.1f} {prov_oral.unit} "
                    f"(Kaynak: {prov_oral.value_source}, Tip: {prov_oral.source_type}, Ref: {prov_oral.source_reference})"
                )

            # 2. DERMAL
            prov_dermal = s.dermal_ate_model
            if prov_dermal is None:
                for h_code, conv in self.ATE_CONVERSION_DERMAL.items():
                    if h_code in codes:
                        prov_dermal = ATEProvenance.create_derived_conversion(
                            conv, h_code, route="dermal", unit="mg/kg", source_ref="SEA_ANNEX_I"
                        )
                        break

            if prov_dermal is not None and prov_dermal.ate > 0:
                ate_dermal_sum += conc / prov_dermal.ate
                has_dermal_inputs = True
                result.calculation_notes.append(
                    f"• Akut Toksisite (Dermal Katkı): [{s.name}] %{conc:.1f}, ATE = {prov_dermal.ate:.1f} {prov_dermal.unit} "
                    f"(Kaynak: {prov_dermal.value_source}, Tip: {prov_dermal.source_type}, Ref: {prov_dermal.source_reference})"
                )

            # 3. SOLUMA (INHALATION)
            inhal_form = s.inhalation.form if s.inhalation else "buhar"
            prov_inhal = s.inhalation.provenance if s.inhalation and s.inhalation.provenance else None
            if prov_inhal is None and s.inhalation and s.inhalation.ate_val and s.inhalation.ate_val > 0:
                unit = "ppmV" if inhal_form == "gaz" else "mg/L"
                prov_inhal = ATEProvenance.create_experimental(
                    s.inhalation.ate_val, route=f"inhalation_{inhal_form}", unit=unit
                )

            if prov_inhal is None:
                for h_code in ["H330", "H331", "H332"]:
                    if h_code in codes:
                        if inhal_form == "gaz":
                            conv = self.ATE_CONVERSION_INHAL_GAS[h_code]
                            prov_inhal = ATEProvenance.create_derived_conversion(
                                conv, h_code, route="inhalation_gas", unit="ppmV", source_ref="SEA_ANNEX_I"
                            )
                        elif inhal_form in ["toz_sis", "toz", "sis"]:
                            conv = self.ATE_CONVERSION_INHAL_DUST[h_code]
                            prov_inhal = ATEProvenance.create_derived_conversion(
                                conv, h_code, route="inhalation_dust", unit="mg/L", source_ref="SEA_ANNEX_I"
                            )
                        else:
                            conv = self.ATE_CONVERSION_INHAL_VAPOUR[h_code]
                            prov_inhal = ATEProvenance.create_derived_conversion(
                                conv, h_code, route="inhalation_vapour", unit="mg/L", source_ref="SEA_ANNEX_I"
                            )
                        break

            if prov_inhal is not None and prov_inhal.ate > 0:
                if inhal_form == "gaz":
                    ate_inhal_gas_sum += conc / prov_inhal.ate
                    has_inhal_gas_inputs = True
                    lbl = "Soluma - Gaz"
                elif inhal_form in ["toz_sis", "toz", "sis"]:
                    ate_inhal_dust_sum += conc / prov_inhal.ate
                    has_inhal_dust_inputs = True
                    lbl = "Soluma - Toz/Sis"
                else:
                    ate_inhal_vapour_sum += conc / prov_inhal.ate
                    has_inhal_vapour_inputs = True
                    lbl = "Soluma - Buhar"

                result.calculation_notes.append(
                    f"• Akut Toksisite ({lbl} Katkı): [{s.name}] %{conc:.1f}, ATE = {prov_inhal.ate:.2f} {prov_inhal.unit} "
                    f"(Kaynak: {prov_inhal.value_source}, Tip: {prov_inhal.source_type}, Ref: {prov_inhal.source_reference})"
                )

        # Sınıflandırma Eşikleri Değerlendirmesi
        # Oral
        if has_oral_inputs and ate_oral_sum > 0:
            ate_oral_mix = 100.0 / ate_oral_sum
            self._classify_oral(ate_oral_mix, result)

        # Dermal
        if has_dermal_inputs and ate_dermal_sum > 0:
            ate_dermal_mix = 100.0 / ate_dermal_sum
            self._classify_dermal(ate_dermal_mix, result)

        # Soluma - Buhar
        if has_inhal_vapour_inputs and ate_inhal_vapour_sum > 0:
            ate_vapour_mix = 100.0 / ate_inhal_vapour_sum
            self._classify_inhal_vapour(ate_vapour_mix, result)

        # Soluma - Gaz
        if has_inhal_gas_inputs and ate_inhal_gas_sum > 0:
            ate_gas_mix = 100.0 / ate_inhal_gas_sum
            self._classify_inhal_gas(ate_gas_mix, result)

        # Soluma - Toz/Sis
        if has_inhal_dust_inputs and ate_inhal_dust_sum > 0:
            ate_dust_mix = 100.0 / ate_inhal_dust_sum
            self._classify_inhal_dust(ate_dust_mix, result)

        oral_ate_val = (100.0 / ate_oral_sum) if (has_oral_inputs and ate_oral_sum > 0) else None
        dermal_ate_val = (100.0 / ate_dermal_sum) if (has_dermal_inputs and ate_dermal_sum > 0) else None
        vapour_ate_val = (100.0 / ate_inhal_vapour_sum) if (has_inhal_vapour_inputs and ate_inhal_vapour_sum > 0) else None
        gas_ate_val = (100.0 / ate_inhal_gas_sum) if (has_inhal_gas_inputs and ate_inhal_gas_sum > 0) else None
        dust_ate_val = (100.0 / ate_inhal_dust_sum) if (has_inhal_dust_inputs and ate_inhal_dust_sum > 0) else None

        uncertain_substances = [s for s in substances if s.data_quality and s.data_quality.quality_level == "UNCERTAIN"]
        component_qualities = {s.name: s.data_quality.quality_level for s in substances if s.data_quality}

        result.evidence = {
            "ate_oral_mix": round(oral_ate_val, 2) if oral_ate_val is not None else None,
            "ate_dermal_mix": round(dermal_ate_val, 2) if dermal_ate_val is not None else None,
            "ate_inhal_vapour_mix": round(vapour_ate_val, 2) if vapour_ate_val is not None else None,
            "ate_inhal_gas_mix": round(gas_ate_val, 2) if gas_ate_val is not None else None,
            "ate_inhal_dust_mix": round(dust_ate_val, 2) if dust_ate_val is not None else None,
            "component_data_qualities": component_qualities,
            "has_uncertain_data": len(uncertain_substances) > 0,
        }

        calcs = []
        if oral_ate_val is not None:
            calcs.append({"route": "oral", "formula": "100 / sum(Ci/ATEi)", "calculated_ate": round(oral_ate_val, 2)})
        if dermal_ate_val is not None:
            calcs.append({"route": "dermal", "formula": "100 / sum(Ci/ATEi)", "calculated_ate": round(dermal_ate_val, 2)})
        if vapour_ate_val is not None:
            calcs.append({"route": "inhal_vapour", "formula": "100 / sum(Ci/ATEi)", "calculated_ate": round(vapour_ate_val, 2)})
        if gas_ate_val is not None:
            calcs.append({"route": "inhal_gas", "formula": "100 / sum(Ci/ATEi)", "calculated_ate": round(gas_ate_val, 2)})
        if dust_ate_val is not None:
            calcs.append({"route": "inhal_dust", "formula": "100 / sum(Ci/ATEi)", "calculated_ate": round(dust_ate_val, 2)})
        result.calculations = calcs

        if result.hazards:
            result.status = "SUFFICIENT"
            result.decision = "; ".join(f"{h.zararlilik_sinifi} {h.kategori} ({h.h_kodu})" for h in result.hazards)
            result.reason = "Hesaplanan ATE_mix değerleri ilgili maruz kalma yollarında toksisite eşiklerini aştı."
        elif (has_oral_inputs or has_dermal_inputs or has_inhal_vapour_inputs or has_inhal_gas_inputs or has_inhal_dust_inputs):
            result.status = "SUFFICIENT"
            result.decision = None
            result.reason = "Akut toksik bileşenler için hesaplanan ATE_mix değerleri Kategori 1-4 aralıklarının üzerinde (zararsız aralıkta)."
        else:
            result.status = "NOT_APPLICABLE"
            result.decision = None
            result.reason = "Akut toksisite sınıflandırmasına sahip bileşen bulunmamaktadır."

        return result

    def _classify_oral(self, ate: float, result: RuleResult):
        if ate <= 5.0:
            cat, h = "Kategori 1", "H300"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 50.0:
            cat, h = "Kategori 2", "H300"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 300.0:
            cat, h = "Kategori 3", "H301"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 2000.0:
            cat, h = "Kategori 4", "H302"
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
        else:
            result.calculation_notes.append(f"• Akut Toksisite (Oral): ATE_mix = {ate:.1f} mg/kg > 2000 mg/kg -> Sınıflandırılmadı.")
            return

        result.hazards.append(ClassifiedHazard(zararlilik_sinifi="Akut Toksisite - Oral", kategori=cat, h_kodu=h))
        result.calculation_notes.append(f"• Akut Toksisite (Oral): ATE_mix = {ate:.1f} mg/kg -> Sınıflandırıldı: {cat} ({h})")

    def _classify_dermal(self, ate: float, result: RuleResult):
        if ate <= 50.0:
            cat, h = "Kategori 1", "H310"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 200.0:
            cat, h = "Kategori 2", "H310"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 1000.0:
            cat, h = "Kategori 3", "H311"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 2000.0:
            cat, h = "Kategori 4", "H312"
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
        else:
            result.calculation_notes.append(f"• Akut Toksisite (Dermal): ATE_mix = {ate:.1f} mg/kg > 2000 mg/kg -> Sınıflandırılmadı.")
            return

        result.hazards.append(ClassifiedHazard(zararlilik_sinifi="Akut Toksisite - Dermal", kategori=cat, h_kodu=h))
        result.calculation_notes.append(f"• Akut Toksisite (Dermal): ATE_mix = {ate:.1f} mg/kg -> Sınıflandırıldı: {cat} ({h})")

    def _classify_inhal_vapour(self, ate: float, result: RuleResult):
        if ate <= 0.5:
            cat, h = "Kategori 1", "H330"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 2.0:
            cat, h = "Kategori 2", "H330"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 10.0:
            cat, h = "Kategori 3", "H331"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 20.0:
            cat, h = "Kategori 4", "H332"
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
        else:
            result.calculation_notes.append(f"• Akut Toksisite (Soluma - Buhar): ATE_mix = {ate:.2f} mg/L > 20.0 mg/L -> Sınıflandırılmadı.")
            return

        result.hazards.append(ClassifiedHazard(zararlilik_sinifi="Akut Toksisite - Soluma (Buhar)", kategori=cat, h_kodu=h))
        result.calculation_notes.append(f"• Akut Toksisite (Soluma - Buhar): ATE_mix = {ate:.2f} mg/L -> Sınıflandırıldı: {cat} ({h})")

    def _classify_inhal_gas(self, ate: float, result: RuleResult):
        if ate <= 100.0:
            cat, h = "Kategori 1", "H330"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 500.0:
            cat, h = "Kategori 2", "H330"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 2500.0:
            cat, h = "Kategori 3", "H331"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 20000.0:
            cat, h = "Kategori 4", "H332"
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
        else:
            result.calculation_notes.append(f"• Akut Toksisite (Soluma - Gaz): ATE_mix = {ate:.1f} ppmV > 20000 ppmV -> Sınıflandırılmadı.")
            return

        result.hazards.append(ClassifiedHazard(zararlilik_sinifi="Akut Toksisite - Soluma (Gaz)", kategori=cat, h_kodu=h))
        result.calculation_notes.append(f"• Akut Toksisite (Soluma - Gaz): ATE_mix = {ate:.1f} ppmV -> Sınıflandırıldı: {cat} ({h})")

    def _classify_inhal_dust(self, ate: float, result: RuleResult):
        if ate <= 0.05:
            cat, h = "Kategori 1", "H330"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 0.5:
            cat, h = "Kategori 2", "H330"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 1.0:
            cat, h = "Kategori 3", "H331"
            result.piktogramlar.append("GHS06")
            result.uyari_kelimesi = "Tehlike"
        elif ate <= 5.0:
            cat, h = "Kategori 4", "H332"
            result.piktogramlar.append("GHS07")
            if result.uyari_kelimesi != "Tehlike":
                result.uyari_kelimesi = "Dikkat"
        else:
            result.calculation_notes.append(f"• Akut Toksisite (Soluma - Toz/Sis): ATE_mix = {ate:.3f} mg/L > 5.0 mg/L -> Sınıflandırılmadı.")
            return

        result.hazards.append(ClassifiedHazard(zararlilik_sinifi="Akut Toksisite - Soluma (Toz/Sis)", kategori=cat, h_kodu=h))
        result.calculation_notes.append(f"• Akut Toksisite (Soluma - Toz/Sis): ATE_mix = {ate:.3f} mg/L -> Sınıflandırıldı: {cat} ({h})")
