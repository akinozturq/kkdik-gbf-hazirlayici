"""
SDS Doküman Projeksiyon Motoru (SDS Document Generator / Projection)
KKDİK Ek-2 ve REACH Annex II standartlarına göre
RegulatoryDecision, RegulatoryLabel ve TransportClassification nesnelerini
16 bölümlük Güvenlik Bilgi Formu (SDS) veri modeline haritalar.
"""

import copy
from typing import Dict, Any, Optional
from app.models.regulatory import (
    RegulatoryDecision,
    RegulatoryLabel,
    TransportClassification
)


class SDSGenerator:
    """
    Düzenleyici Karar (Regulatory Decision), Etiket (Label) ve Taşımacılık (Transport)
    nesnelerini tüketerek 16 bölümlük SDS veri yapısına dönüştüren doküman projeksiyon servisidir.
    """

    @classmethod
    def project_to_sds_sections(
        cls,
        decision: RegulatoryDecision,
        label: RegulatoryLabel,
        transport: Optional[TransportClassification] = None,
        base_sds: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Saf karar ve projeksiyon nesnelerini 16 bölümlük SDS şemasına yansıtır.
        base_sds varsa mevcut kullanıcı girdilerini korur ve üzerine yazar.
        """
        sds = copy.deepcopy(base_sds or {})

        # ---------------------------------------------------------------------
        # 1. BÖLÜM 2: ZARARLILIK TANIMLANMASI (HAZARDS IDENTIFICATION)
        # ---------------------------------------------------------------------
        if "b2_zarar_tanimi" not in sds or not isinstance(sds["b2_zarar_tanimi"], dict):
            sds["b2_zarar_tanimi"] = {}

        b2 = sds["b2_zarar_tanimi"]
        if "b2_1" not in b2 or not isinstance(b2["b2_1"], dict):
            b2["b2_1"] = {}
        if "b2_2" not in b2 or not isinstance(b2["b2_2"], dict):
            b2["b2_2"] = {}

        # 2.1 Maddenin veya Karışımın Sınıflandırılması
        sinif_list = []
        for h in decision.hazards:
            sinif_list.append({
                "zararlilik_sinifi": h.zararlilik_sinifi,
                "kategori": h.kategori,
                "h_kodu": h.h_kodu,
                "status": h.status,
                "status_label": h.status_label,
                "range_details": h.range_details
            })

        b2["b2_1"]["siniflandirmalar"] = sinif_list
        b2["b2_1"]["siniflandirilmamis"] = len(sinif_list) == 0

        # Zararlılık metinlerini türet
        phys_hazards = [s["zararlilik_sinifi"] for s in sinif_list if any(c in s.get("h_kodu", "") for c in ["H220", "H221", "H222", "H224", "H225", "H226"])]
        health_hazards = [s["zararlilik_sinifi"] for s in sinif_list if s.get("h_kodu", "").startswith("H3")]
        env_hazards = [s["zararlilik_sinifi"] for s in sinif_list if s.get("h_kodu", "").startswith("H4")]

        b2["b2_1"]["fiziksel_zararlar_metni"] = ", ".join(phys_hazards) if phys_hazards else "Fiziksel zararlılık sınıfına girmez."
        b2["b2_1"]["saglik_zararlari_metni"] = ", ".join(health_hazards) if health_hazards else "İnsan sağlığı açısından zararlılık sınıfına girmez."
        b2["b2_1"]["cevresel_zararlar_metni"] = ", ".join(env_hazards) if env_hazards else "Çevre açısından zararlılık sınıfına girmez."

        # 2.2 Etiket Unsurları
        b2["b2_2"]["piktogramlar"] = list(label.pictograms)
        b2["b2_2"]["uyari_kelimesi"] = label.signal_word
        b2["b2_2"]["h_ifadeleri"] = list(label.hazard_statements)
        b2["b2_2"]["p_ifadeleri"] = list(label.precautionary_statements)
        b2["b2_2"]["euh_ifadeleri"] = list(label.supplemental_statements)
        b2["b2_2"]["dokunulabilir_uyari"] = label.tactile_warning_required
        b2["b2_2"]["cocuk_emniyetli_kapak"] = label.child_resistant_fastening_required

        # ---------------------------------------------------------------------
        # 2. BÖLÜM 14: TAŞIMACILIK BİLGİLERİ (TRANSPORT INFORMATION)
        # ---------------------------------------------------------------------
        if transport is not None:
            if "b14_tasimacilik" not in sds or not isinstance(sds["b14_tasimacilik"], dict):
                sds["b14_tasimacilik"] = {}

            b14 = sds["b14_tasimacilik"]
            b14["b14_1_un_numarasi"] = transport.un_number or "—"
            b14["b14_2_un_tasimacilik_adi"] = transport.proper_shipping_name_tr or "—"
            b14["b14_2_un_tasimacilik_adi_en"] = transport.proper_shipping_name_en or "—"
            b14["b14_3_tasimacilik_sinifi"] = transport.class_label or transport.class_code or "—"
            b14["b14_4_ambalajlama_grubu"] = transport.packing_group or "—"
            b14["b14_5_cevresel_zararlar"] = transport.environmental_hazards_tr or ("Evet" if transport.environmental_hazards else "Hayır")
            b14["b14_5_cevresel_zararlar_en"] = transport.environmental_hazards_en or ("Yes" if transport.environmental_hazards else "No")
            b14["b14_6_kullanici_ozel_onlemler"] = transport.user_special_precautions or ""

        # ---------------------------------------------------------------------
        # 3. REGULATORY METADATA & AUDIT EXTENSION
        # ---------------------------------------------------------------------
        sds["_regulatory_decision_id"] = decision.decision_id
        sds["_regulatory_decision_timestamp"] = decision.created_at
        if decision.data_quality:
            sds["_data_quality_score"] = decision.data_quality.quality_score
            sds["_data_quality_status"] = decision.data_quality.overall_quality

        return sds
