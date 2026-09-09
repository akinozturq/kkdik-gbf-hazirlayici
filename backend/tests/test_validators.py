"""
KKDİK Ek-2 Doğrulama Kuralları Birim Testleri (Bölüm 4 & Bölüm 2.1)
"""

import pytest
from app.services.validator_service import validator_service
from app.schemas.sds_sections import SDSModel


def test_valid_sds_passes_validation(sample_valid_sds_dict):
    """Eksiksiz ve kurallara uygun doldurulmuş SDS hatasız doğrulanmalıdır."""
    result = validator_service.validate_sds(sample_valid_sds_dict)
    assert result.is_valid_for_export is True
    assert result.total_errors == 0
    assert result.overall_completion_percentage > 90.0


def test_rule_empty_subsections_forbidden(sample_valid_sds_dict):
    """Kural md. 0.4: Hiçbir alt bölüm tamamen boş bırakılamaz."""
    # Boş bir SDS nesnesi ile doğrula
    empty_sds = SDSModel()
    result = validator_service.validate_sds(empty_sds)
    assert result.is_valid_for_export is False
    assert result.total_errors > 0

    error_fields = [e.field_path for e in result.errors]
    assert "meta.hazirlama_tarihi" in error_fields
    assert "b1_kimlik.b1_1.madde_karisim_adi" in error_fields
    assert "b1_kimlik.b1_3.tedarikci_adi" in error_fields
    assert "b4_ilk_yardim.b4_1.soluma" in error_fields
    assert "b5_yangin_mucadele.b5_1.uygun_sondurucu" in error_fields


def test_rule_xor_substance_vs_mixture(sample_valid_sds_dict):
    """Kural md. 0.3.1 & 3. Bölüm: 3.1 / 3.2 karşılıklı dışlayıcıdır (XOR)."""
    sds_data = dict(sample_valid_sds_dict)

    # 1. Tip "madde" seçilmiş ama madde bilgisi boş
    sds_data["b3_bilesim"] = {
        "tip": "madde",
        "madde": {"kimyasal_kimlik": ""},
        "karisim": {"bilesenler": []}
    }
    res1 = validator_service.validate_sds(sds_data)
    assert any(e.section == "B3.1" for e in res1.errors)

    # 2. Tip "madde" seçilmiş ama aynı zamanda karışım bileşenleri de eklenmiş -> Uyarı üretilmeli
    sds_data["b3_bilesim"] = {
        "tip": "madde",
        "madde": {"kimyasal_kimlik": "Saf Toluen", "cas_no": "108-88-3"},
        "karisim": {"bilesenler": [{"ad": "Aseton", "konsantrasyon": "%50"}]}
    }
    res2 = validator_service.validate_sds(sds_data)
    assert any("hem madde (3.1) hem karışım bileşeni (3.2)" in w.message for w in res2.warnings)


def test_rule_forbidden_phrases_detected(sample_valid_sds_dict):
    """Kural md. 0.2.4: Zararlı olmadığını ima eden yasaklı ifadeler ('zararsız', 'sağlığa etkisi yok' vb.) tespit edilmeli ve uyarılmalıdır."""
    sds_data = dict(sample_valid_sds_dict)

    # Yasaklı ifadeleri farklı bölümlere yerleştirelim
    sds_data["b4_ilk_yardim"]["b4_2_belirtiler_etkiler"] = "Ürün tamamen zararsızdır ve sağlığa etkisi yok."
    sds_data["b7_ellecme_depolama"]["b7_1_guvenli_ellecleme"] = "Çoğu kullanım koşullarında güvenli bir üründür."
    sds_data["b11_toksikolojik"]["b11_1"]["akut_toksisite"] = "Toksik değildir, çevre dostu bir maddedir."

    res = validator_service.validate_sds(sds_data)
    warning_messages = [w.message for w in res.warnings if w.section == "B0.2.4"]

    assert any("zararsız" in msg for msg in warning_messages)
    assert any("sağlığa etkisi yok" in msg for msg in warning_messages)
    assert any("çoğu kullanım koşullarında güvenli" in msg for msg in warning_messages)
    assert any("toksik değil" in msg for msg in warning_messages)
    assert any("çevre dostu" in msg for msg in warning_messages)


def test_rule_preparation_date_required(sample_valid_sds_dict):
    """Kural md. 0.2.5: Hazırlama tarihi ilk sayfada zorunludur."""
    sds_data = dict(sample_valid_sds_dict)
    sds_data["meta"]["hazirlama_tarihi"] = ""

    res = validator_service.validate_sds(sds_data)
    assert any(e.section == "B0.2.5" and "Hazırlama tarihi" in e.message for e in res.errors)


def test_rule_h_codes_section16_reference(sample_valid_sds_dict):
    """Kural md. 2.1 & 16.d: Formda geçen H-kodlarının Bölüm 16'da tam metin referansı zorunludur."""
    sds_data = dict(sample_valid_sds_dict)

    # B2'de H314 (Cilt aşınması) ekleyelim ama B16 tam_h_ifadeleri'nde tanımlamayalım
    sds_data["b2_zarar_tanimi"]["b2_2"]["h_ifadeleri"].append("H314")

    res = validator_service.validate_sds(sds_data)
    h_warnings = [w for w in res.warnings if w.section == "B16"]
    assert len(h_warnings) > 0
    assert "H314" in h_warnings[0].message


def test_rule_unclassified_mixture_explanation(sample_valid_sds_dict):
    """Kural md. 2.1: Karışım sınıflandırma kriterlerini karşılamıyorsa bu açıkça gerekçelendirilmelidir."""
    sds_data = dict(sample_valid_sds_dict)

    # Sınıflandırma yok ve sınıflandırılmamış seçili ama gerekçe boş
    sds_data["b2_zarar_tanimi"]["b2_1"] = {
        "siniflandirmalar": [],
        "siniflandirilmamis": True,
        "siniflandirilmama_gerekcesi": ""
    }

    res = validator_service.validate_sds(sds_data)
    assert any(e.section == "B2.1" and "açıkça belirtilmelidir" in e.message for e in res.errors)

    # Gerekçe yazıldığında B2.1 hatası kalkmalı
    sds_data["b2_zarar_tanimi"]["b2_1"]["siniflandirilmama_gerekcesi"] = "SEA Yönetmeliği Ek-1 kriterlerine göre zararlı olarak sınıflandırılmamıştır."
    res2 = validator_service.validate_sds(sds_data)
    assert not any(e.section == "B2.1" and "açıkça belirtilmelidir" in e.message for e in res2.errors)


def test_section_progress_calculation(sample_valid_sds_dict):
    """Her bölümün ilerleme durumu ve overall completion skoru doğru hesaplanmalıdır."""
    result = validator_service.validate_sds(sample_valid_sds_dict)
    assert len(result.section_progress) == 16
    assert all(p.completion_percentage == 100.0 for p in result.section_progress)
    assert result.overall_completion_percentage == 100.0


def test_semantic_cross_validation_flammables_and_viscosity(sample_valid_sds_dict):
    """HIGH-04: B2'de H226 varsa B9.1 parlama noktası zorunludur; H304 varsa viskozite uyarısı verilmelidir."""
    sds_data = dict(sample_valid_sds_dict)
    sds_data["b2_zarar_tanimi"]["b2_2"]["h_ifadeleri"] = ["H226", "H304"]
    sds_data["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["parlama_noktasi"] = "Bilgi yok"
    sds_data["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["kinematik_viskozite"] = ""
    sds_data["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["akiskanlik"] = ""

    res = validator_service.validate_sds(sds_data)
    # H226 varken parlama noktası "Bilgi yok" -> Error B9.1
    assert any(e.section == "B9.1" and "parlama noktası" in e.message for e in res.errors)
    # H304 varken viskozite ve akiskanlik boş -> Warning B9.1
    assert any(w.section == "B9.1" and "kinematik viskozite" in w.message for w in res.warnings)


def test_cross_section_regulatory_validation_rules(sample_valid_sds_dict):
    """
    Kullanıcı İnceleme Kriterleri: Cross-Section Regulatory Validation
    1. B2 = H225 & B9.1 Flash point = 80°C -> HATA (ERROR)
    2. B2 = H304 & B9.1 viscosity = 35 mm²/s -> İNCELEME UYARISI (WARNING)
    3. B2 = H410 & B12 aquatic toxicity = "no supporting data" -> UYARI (WARNING)
    4. B2 = H224 & B9.1 boiling point = 40°C (>35°C) -> HATA (ERROR)
    5. B9.1 pH = 1.5 & no H314/H318 -> UYARI (WARNING)
    6. B2 = H314 & B14 transport class != 8 -> UYARI (WARNING)
    7. B2 = H410 & B14.5 marine pollutant = "Hayır" -> UYARI (WARNING)
    """
    # 1. B2 = H225 & B9.1 Flash point = 80°C -> HATA (ERROR)
    sds_h225 = dict(sample_valid_sds_dict)
    sds_h225["b2_zarar_tanimi"] = {
        "b2_1": {"siniflandirmalar": [{"zararlilik_sinifi": "Flam. Liq.", "kategori": "2", "h_kodu": "H225"}]},
        "b2_2": {"h_ifadeleri": ["H225"]}
    }
    sds_h225["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["parlama_noktasi"] = "80 °C"
    sds_h225["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["kaynama_noktasi"] = "110 °C"
    res1 = validator_service.validate_sds(sds_h225)
    assert any(
        e.section == "B9.1" and "H225" in e.message and "80" in e.message and e.severity == "ERROR"
        for e in res1.errors
    )

    # 2. B2 = H304 & B9.1 viscosity = 35 mm²/s -> İNCELEME UYARISI (WARNING)
    sds_h304 = dict(sample_valid_sds_dict)
    sds_h304["b2_zarar_tanimi"] = {
        "b2_1": {"siniflandirmalar": [{"zararlilik_sinifi": "Asp. Tox.", "kategori": "1", "h_kodu": "H304"}]},
        "b2_2": {"h_ifadeleri": ["H304"]}
    }
    sds_h304["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["kinematik_viskozite"] = "35 mm²/s"
    sds_h304["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["parlama_noktasi"] = "105 °C"
    res2 = validator_service.validate_sds(sds_h304)
    assert any(
        w.section == "B9.1" and "H304" in w.message and "35" in w.message and "20.5" in w.message and w.severity == "WARNING"
        for w in res2.warnings
    )

    # 3. B2 = H410 & B12 aquatic toxicity = "no supporting data" -> UYARI (WARNING)
    sds_h410 = dict(sample_valid_sds_dict)
    sds_h410["b2_zarar_tanimi"] = {
        "b2_1": {"siniflandirmalar": [{"zararlilik_sinifi": "Aquatic Chronic", "kategori": "1", "h_kodu": "H410"}]},
        "b2_2": {"h_ifadeleri": ["H410"]}
    }
    sds_h410["b12_ekolojik"] = {"b12_1_toksisite": "no supporting data (veri yok)"}
    sds_h410["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["parlama_noktasi"] = "120 °C"
    res3 = validator_service.validate_sds(sds_h410)
    assert any(
        w.section == "B12.1" and "Destekleyici Veri Eksikliği" in w.message and "H410" in w.message and w.severity == "WARNING"
        for w in res3.warnings
    )

    # 4. B2 = H224 & B9.1 Kaynama Noktası = 45°C (> 35°C) -> HATA (ERROR)
    sds_h224 = dict(sample_valid_sds_dict)
    sds_h224["b2_zarar_tanimi"] = {
        "b2_1": {"siniflandirmalar": [{"zararlilik_sinifi": "Flam. Liq.", "kategori": "1", "h_kodu": "H224"}]},
        "b2_2": {"h_ifadeleri": ["H224"]}
    }
    sds_h224["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["parlama_noktasi"] = "-10 °C"
    sds_h224["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["kaynama_noktasi"] = "45 °C"
    res4 = validator_service.validate_sds(sds_h224)
    assert any(
        e.section == "B9.1" and "H224" in e.message and "kaynama noktası" in e.message and e.severity == "ERROR"
        for e in res4.errors
    )

    # 5. B9.1 pH = 1.5 & No H314/H318 -> UYARI (WARNING)
    sds_ph = dict(sample_valid_sds_dict)
    sds_ph["b2_zarar_tanimi"]["b2_2"]["h_ifadeleri"] = ["H226"]
    sds_ph["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["ph"] = "1.5"
    res5 = validator_service.validate_sds(sds_ph)
    assert any(
        w.section == "B2.1" and "pH = 1.5" in w.message and "H314" in w.message and w.severity == "WARNING"
        for w in res5.warnings
    )

    # 6. B2 = H314 & B14 ADR Sınıfı != 8 -> UYARI (WARNING)
    sds_adr = dict(sample_valid_sds_dict)
    sds_adr["b2_zarar_tanimi"]["b2_2"]["h_ifadeleri"] = ["H314"]
    sds_adr["b14_tasimacilik"]["b14_3_tasimacilik_sinifi"] = "3"
    sds_adr["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["parlama_noktasi"] = "90 °C"
    res6 = validator_service.validate_sds(sds_adr)
    assert any(
        w.section == "B14.3" and "Aşındırıcı" in w.message and "8" in w.message and w.severity == "WARNING"
        for w in res6.warnings
    )

    # 7. B2 = H410 & B14.5 Marine Pollutant = "Hayır" -> UYARI (WARNING)
    sds_marine = dict(sample_valid_sds_dict)
    sds_marine["b2_zarar_tanimi"]["b2_2"]["h_ifadeleri"] = ["H410"]
    sds_marine["b14_tasimacilik"]["b14_5_cevresel_zararlar"] = "Deniz Kirletici değildir (Hayır)"
    sds_marine["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["parlama_noktasi"] = "95 °C"
    res7 = validator_service.validate_sds(sds_marine)
    assert any(
        w.section == "B14.5" and "Marine Pollutant" in w.message and w.severity == "WARNING"
        for w in res7.warnings
    )

