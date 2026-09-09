"""
Veri Kalitesi ve Regülatif Güvenilirlik Değerlendiricisi
(Regulatory Data Quality & Uncertainty Assessment Layer)

İş Akışı Konumu:
INPUT ➔ NORMALIZATION ➔ [DATA QUALITY] ➔ RULE ➔ EVIDENCE ➔ DECISION ➔ LABEL ➔ SDS

Görevleri:
1. Bileşenlerin konsantrasyon kesinliğini değerlendirir (örn. %10-25 -> UNCERTAIN, <%1 -> BOUNDED, %15 -> EXACT).
2. Zararlılık sınıfı ve H-kodu kalitesini (CMR alt kategori çözünürlüğü, çelişkili ifadeler vb.) doğrular.
3. Karışımdaki bileşenlerin zararlılık türlerine göre gerekli fiziksel test verilerinin (parlama noktası, 40°C viskozite vb.) eksikliğini tespit eder.
4. Karışım ve bileşen bazlı veri kalitesi skorunu (0-100) ve denetim izini oluşturur.
"""

from typing import List, Dict, Any, Optional
from app.models.regulatory import (
    StructuredSubstance,
    CalculationContext,
    ConcentrationValue,
    HazardEntry,
    SubstanceDataQuality,
    MixtureDataQuality,
)


class DataQualityAssessor:
    """
    Kural motorundan önce çalışan yapısal veri kalitesi denetim katmanı.
    Her bileşenin ve karışımın veri belirsizliklerini tespit eder.
    """

    @classmethod
    def assess_substance(
        cls,
        name: str,
        concentration: ConcentrationValue,
        hazards: List[HazardEntry],
        raw_h_codes: Optional[List[str]] = None
    ) -> SubstanceDataQuality:
        """
        Tek bir bileşenin girdi kalitesini değerlendirir.
        Örn: Konsantrasyon = %10-25 -> quality_level = 'UNCERTAIN', concentration_quality = 'UNCERTAIN'
        """
        flags: List[str] = []
        details: List[str] = []
        uncertainty_score = 0.0

        # 1. KONSANTRASYON KALİTESİ
        if concentration.qualifier == "range":
            concentration_quality = "UNCERTAIN"
            min_v = concentration.min_val if concentration.min_val is not None else 0.0
            max_v = concentration.max_val if concentration.max_val is not None else concentration.value
            spread = max(0.0, max_v - min_v)
            flags.append("CONCENTRATION_RANGE_UNCERTAINTY")
            details.append(
                f"Konsantrasyon aralık olarak belirtilmiş (%{min_v:g} - %{max_v:g}), kesinlik UNCERTAIN."
            )
            uncertainty_score += min(0.5, spread / 50.0)
        elif concentration.qualifier in ("less_than", "greater_than"):
            concentration_quality = "BOUNDED"
            flags.append(f"CONCENTRATION_{concentration.qualifier.upper()}")
            details.append(
                f"Konsantrasyon tek taraflı sınırla belirtilmiş ({concentration.qualifier} %{concentration.value:g}), kesinlik BOUNDED."
            )
            uncertainty_score += 0.2
        else:
            concentration_quality = "EXACT"

        # 2. ZARARLILIK SINIFLANDIRMA VE H-KODU KALİTESİ
        has_contradictory = any(h.validation_status == "CONTRADICTORY" for h in hazards)
        has_unresolved = any(
            h.validation_status == "UNRESOLVED" or
            "CATEGORY_UNRESOLVED" in (h.category or "").upper() or
            (h.validation_issues and any(i.code == "CMR_CATEGORY_UNRESOLVED" for i in h.validation_issues))
            for h in hazards
        )
        has_syntactic_only = any(h.validation_status == "SYNTACTIC_ONLY" for h in hazards)

        if has_contradictory:
            hazard_quality = "CONTRADICTORY"
            flags.append("HAZARD_CONTRADICTORY")
            details.append("Zararlılık sınıfı ile H-kodu arasında çelişki tespit edildi.")
            uncertainty_score += 0.5
        elif has_unresolved:
            hazard_quality = "CATEGORY_UNRESOLVED"
            flags.append("CMR_CATEGORY_UNRESOLVED")
            details.append("CMR alt kategorisi (1A/1B) veri kaynağında eksik olduğundan çözümlenemedi (CATEGORY_UNRESOLVED).")
            uncertainty_score += 0.3
        elif has_syntactic_only:
            hazard_quality = "SYNTACTIC_ONLY"
            flags.append("SYNTACTIC_ONLY_CLASSIFICATION")
            uncertainty_score += 0.1
        else:
            hazard_quality = "CONFIRMED"

        # 3. GENEL BİLEŞEN VERİ KALİTESİ SEVİYESİ
        if hazard_quality == "CONTRADICTORY":
            quality_level = "CONTRADICTORY"
        elif concentration_quality == "UNCERTAIN" or hazard_quality == "CATEGORY_UNRESOLVED":
            quality_level = "UNCERTAIN"
        elif concentration_quality == "BOUNDED":
            quality_level = "UNCERTAIN" if uncertainty_score >= 0.2 else "CONFIRMED"
        else:
            quality_level = "CONFIRMED"

        return SubstanceDataQuality(
            quality_level=quality_level,
            concentration_quality=concentration_quality,
            hazard_quality=hazard_quality,
            uncertainty_score=round(min(1.0, uncertainty_score), 2),
            flags=flags,
            details=details,
        )

    @classmethod
    def assess_mixture(
        cls,
        substances: List[StructuredSubstance],
        context: CalculationContext
    ) -> MixtureDataQuality:
        """
        Karışımın tüm bileşenlerini ve fiziksel parametre gereksinimlerini tarayarak
        bütünleşik veri kalitesi profilini (MixtureDataQuality) üretir.
        """
        component_qualities: Dict[str, SubstanceDataQuality] = {}
        missing_physical: List[str] = []
        audit_notes: List[str] = []

        has_uncertain = False
        has_unresolved = False
        has_contradictory = False

        total_penalty = 0.0

        for s in substances:
            dq = s.data_quality
            if dq is None or (dq.quality_level == "CONFIRMED" and s.concentration.qualifier == "range"):
                dq = cls.assess_substance(
                    name=s.name,
                    concentration=s.concentration,
                    hazards=s.hazards,
                    raw_h_codes=s.raw_h_codes
                )
                s.data_quality = dq

            component_qualities[s.name] = dq

            if dq.quality_level == "UNCERTAIN":
                has_uncertain = True
                total_penalty += (dq.uncertainty_score * 20.0)
            elif dq.quality_level == "CONTRADICTORY":
                has_contradictory = True
                total_penalty += 35.0

            if dq.hazard_quality == "CATEGORY_UNRESOLVED":
                has_unresolved = True
                total_penalty += 15.0

        # FİZİKSEL TEST VERİSİ GEREKSİNİMLERİ
        # 1. Aspirasyon Zararlılığı: H304 / Asp. Tox. varsa kinematik viskozite (40°C) gereklidir
        has_asp = any(
            "H304" in s.raw_h_codes or any(h.h_code == "H304" or "Asp" in h.hazard_class for h in s.hazards)
            for s in substances
        )
        if has_asp and context.kinematik_viskozite_40c is None:
            missing_physical.append("kinematik_viskozite_40c")
            audit_notes.append(
                "Aspirasyon toksisitesi taşıyan bileşen mevcut, ancak 40°C kinematik viskozite test verisi eksik."
            )
            total_penalty += 25.0

        # 2. Alevlenir Sıvılar: Flam. Liq. / H224-H226 varsa parlama noktası gereklidir
        has_flam = any(
            any(h.h_code in ["H224", "H225", "H226"] or h.hazard_class.startswith("Flam") for h in s.hazards) or
            any(c in s.raw_h_codes for c in ["H224", "H225", "H226"])
            for s in substances
        )
        if has_flam and context.parlama_noktasi is None:
            missing_physical.append("parlama_noktasi")
            audit_notes.append(
                "Alevlenir bileşen mevcut, ancak karışımın ölçülmüş parlama noktası test verisi eksik."
            )
            total_penalty += 30.0
        elif has_flam and context.parlama_noktasi is not None and context.parlama_noktasi < 23.0 and context.kaynama_noktasi is None:
            missing_physical.append("kaynama_noktasi")
            audit_notes.append(
                "Parlama noktası < 23°C olan alevlenir karışımda Kategori 1/2 ayrımı için kaynama noktası test verisi eksik."
            )
            total_penalty += 15.0

        # Genel Karışım Kalite Seviyesi
        if has_contradictory:
            overall = "CONTRADICTORY"
        elif missing_physical:
            overall = "INCOMPLETE"
        elif has_uncertain or has_unresolved:
            overall = "UNCERTAIN"
        else:
            overall = "CONFIRMED"

        quality_score = max(0.0, min(100.0, 100.0 - total_penalty))

        mixture_dq = MixtureDataQuality(
            overall_quality=overall,
            quality_score=round(quality_score, 1),
            has_uncertain_components=has_uncertain,
            has_unresolved_hazards=has_unresolved,
            missing_physical_data=missing_physical,
            component_qualities=component_qualities,
            audit_notes=audit_notes,
        )

        context.data_quality = mixture_dq
        return mixture_dq
