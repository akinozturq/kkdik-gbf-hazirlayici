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
    """16 bölümün ilerleme oranları doğru hesaplanmalıdır."""
    res = validator_service.validate_sds(sample_valid_sds_dict)
    assert len(res.section_progress) == 16
    for sp in res.section_progress:
        assert 1 <= sp.section_number <= 16
        assert sp.completion_percentage >= 0.0
        assert sp.total_subsections > 0
