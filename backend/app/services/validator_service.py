"""
KKDİK Ek-2 Doğrulama Motoru (Validator Service)
Spesifikasyon Bölüm 4 ve Bölüm 2.1'de tanımlanan tüm kuralları eksiksiz uygular.
"""

import re
from typing import List, Dict, Any, Tuple, Union, Set, Optional
from app.schemas.sds_sections import SDSModel
from app.schemas.validation import (
    ValidationItem,
    ValidationResult,
    SectionProgress,
    ValidationSeverity
)
from app.services.reference_service import reference_service


# KKDİK Ek-2 Madde 0.2.4 Yasaklı İfadeler Listesi
FORBIDDEN_PHRASES = [
    "zararsız",
    "zararlı değildir",
    "sağlığa etkisi yok",
    "sağlığa zararsız",
    "çoğu kullanım koşullarında güvenli",
    "tamamen güvenli",
    "tehlikesiz",
    "toksik değildir",
    "toksik değil",
    "non-toxic",
    "çevre dostu",
    "eko-dostu",
    "hiçbir zararı yoktur",
    "risk içermez",
    "zararlı olabilir",  # Kesin olmayan / muğlak ifade yasağı
]


SECTION_METADATA = [
    {"num": 1, "code": "B1", "title": "Maddenin / Karışımın ve Şirketin / Dağıtıcının Kimliği"},
    {"num": 2, "code": "B2", "title": "Zararlılık Tanımlanması"},
    {"num": 3, "code": "B3", "title": "Bileşimi / İçindekiler Hakkında Bilgi"},
    {"num": 4, "code": "B4", "title": "İlk Yardım Önlemleri"},
    {"num": 5, "code": "B5", "title": "Yangınla Mücadele Önlemleri"},
    {"num": 6, "code": "B6", "title": "Kaza Sonucu Yayılmaya Karşı Önlemler"},
    {"num": 7, "code": "B7", "title": "Elleçleme ve Depolama"},
    {"num": 8, "code": "B8", "title": "Maruz Kalma Kontrolleri / Kişisel Korunma"},
    {"num": 9, "code": "B9", "title": "Fiziksel ve Kimyasal Özellikler"},
    {"num": 10, "code": "B10", "title": "Kararlılık ve Tepkime"},
    {"num": 11, "code": "B11", "title": "Toksikolojik Bilgiler"},
    {"num": 12, "code": "B12", "title": "Ekolojik Bilgiler"},
    {"num": 13, "code": "B13", "title": "Bertaraf Etme Bilgileri"},
    {"num": 14, "code": "B14", "title": "Taşımacılık Bilgisi"},
    {"num": 15, "code": "B15", "title": "Mevzuat Bilgisi"},
    {"num": 16, "code": "B16", "title": "Diğer Bilgiler"},
]


def _get_nested(data: Any, *keys: str, default: Any = None) -> Any:
    """İç içe sözlük yapılarında None-safe güvenli okuma yapar."""
    current = data
    for k in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(k)
        if current is None:
            return default
    return current


class ValidatorService:
    def __init__(self):
        self.compiled_forbidden = [
            (phrase, re.compile(rf'(?:\b|\A){re.escape(phrase)}', re.IGNORECASE))
            for phrase in FORBIDDEN_PHRASES
        ]

    def _is_filled(self, value: Any) -> bool:
        """Değerin doldurulup doldurulmadığını kontrol eder"""
        if value is None:
            return False
        if isinstance(value, str):
            return len(value.strip()) > 0
        if isinstance(value, (list, dict, set, tuple)):
            return len(value) > 0
        if isinstance(value, bool):
            return True
        return True

    def validate_sds(self, sds: Union[SDSModel, Dict[str, Any]]) -> ValidationResult:
        """
        SDS nesnesini KKDİK Ek-2 kurallarına göre detaylı doğrulamadan geçirir.
        """
        if isinstance(sds, dict):
            sds_dict = sds
            try:
                sds_model = SDSModel(**sds)
                sds_dict = sds_model.model_dump()
            except Exception:
                sds_model = None
                sds_dict = sds
        else:
            sds_model = sds
            sds_dict = sds.model_dump()

        errors: List[ValidationItem] = []
        warnings: List[ValidationItem] = []

        # -------------------------------------------------------------
        # KURAL 3: Yasaklı İfadeler Taraması (md. 0.2.4)
        # -------------------------------------------------------------
        self._check_forbidden_phrases(sds_dict, warnings)

        # -------------------------------------------------------------
        # KURAL 4: Hazırlama Tarihi İlk Sayfada Zorunlu (md. 0.2.5)
        # -------------------------------------------------------------
        hazirlama_tarihi = _get_nested(sds_dict, "meta", "hazirlama_tarihi")
        if not self._is_filled(hazirlama_tarihi):
            errors.append(ValidationItem(
                section="B0.2.5",
                field_path="meta.hazirlama_tarihi",
                message="Hazırlama tarihi zorunludur ve ilk sayfada yer almalıdır.",
                regulation_ref="KKDİK Ek-2 md. 0.2.5",
                severity="ERROR"
            ))

        # -------------------------------------------------------------
        # BÖLÜM 1 DOĞRULAMALARI (md. 0.4)
        # -------------------------------------------------------------
        madde_karisim_adi = _get_nested(sds_dict, "b1_kimlik", "b1_1", "madde_karisim_adi")
        if not self._is_filled(madde_karisim_adi):
            errors.append(ValidationItem(
                section="B1.1",
                field_path="b1_kimlik.b1_1.madde_karisim_adi",
                message="1.1 Madde / Karışım kimliği adı boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 1.1",
                severity="ERROR"
            ))

        tanimlanmis_kullanimlar = _get_nested(sds_dict, "b1_kimlik", "b1_2", "tanimlanmis_kullanimlar")
        if not self._is_filled(tanimlanmis_kullanimlar):
            warnings.append(ValidationItem(
                section="B1.2",
                field_path="b1_kimlik.b1_2.tanimlanmis_kullanimlar",
                message="1.2 Belirlenmiş ilgili kullanımlar belirtilmelidir.",
                regulation_ref="KKDİK Ek-2 md. 1.2",
                severity="WARNING"
            ))

        tedarikci_adi = _get_nested(sds_dict, "b1_kimlik", "b1_3", "tedarikci_adi")
        if not self._is_filled(tedarikci_adi):
            errors.append(ValidationItem(
                section="B1.3",
                field_path="b1_kimlik.b1_3.tedarikci_adi",
                message="1.3 Tedarikçi şirket adı boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 1.3",
                severity="ERROR"
            ))

        eposta = _get_nested(sds_dict, "b1_kimlik", "b1_3", "eposta")
        if not self._is_filled(eposta):
            errors.append(ValidationItem(
                section="B1.3",
                field_path="b1_kimlik.b1_3.eposta",
                message="1.3 GBF'den sorumlu yetkili e-posta adresi zorunludur.",
                regulation_ref="KKDİK Ek-2 md. 1.3",
                severity="ERROR"
            ))

        acil_telefon = _get_nested(sds_dict, "b1_kimlik", "b1_4", "acil_telefon")
        if not self._is_filled(acil_telefon):
            errors.append(ValidationItem(
                section="B1.4",
                field_path="b1_kimlik.b1_4.acil_telefon",
                message="1.4 Acil durum telefon numarası (ör. UZEM 114 veya şirket acil hattı) zorunludur.",
                regulation_ref="KKDİK Ek-2 md. 1.4",
                severity="ERROR"
            ))

        # -------------------------------------------------------------
        # BÖLÜM 2 DOĞRULAMALARI (md. 2.1, 2.2, 2.3)
        # -------------------------------------------------------------
        siniflandirmalar = _get_nested(sds_dict, "b2_zarar_tanimi", "b2_1", "siniflandirmalar", default=[])
        siniflandirilmamis = _get_nested(sds_dict, "b2_zarar_tanimi", "b2_1", "siniflandirilmamis", default=False)
        gerekce = _get_nested(sds_dict, "b2_zarar_tanimi", "b2_1", "siniflandirilmama_gerekcesi", default="")

        # Kural: Karışım sınıflandırma kriterlerini karşılamıyorsa bu açıkça belirtilmeli
        if not siniflandirmalar and not siniflandirilmamis:
            errors.append(ValidationItem(
                section="B2.1",
                field_path="b2_zarar_tanimi.b2_1.siniflandirmalar",
                message="2.1 Maddenin/karışımın sınıflandırması girilmeli veya 'Sınıflandırılmamış' seçilerek gerekçesi belirtilmelidir.",
                regulation_ref="KKDİK Ek-2 md. 2.1",
                severity="ERROR"
            ))
        elif siniflandirilmamis and not self._is_filled(gerekce):
            errors.append(ValidationItem(
                section="B2.1",
                field_path="b2_zarar_tanimi.b2_1.siniflandirilmama_gerekcesi",
                message="2.1 Karışım zararlı olarak sınıflandırılmamışsa, mevzuat kriterlerini karşılamadığı açıkça belirtilmelidir.",
                regulation_ref="KKDİK Ek-2 md. 2.1",
                severity="ERROR"
            ))

        if siniflandirmalar:
            uyari_kelimesi = _get_nested(sds_dict, "b2_zarar_tanimi", "b2_2", "uyari_kelimesi")
            if not self._is_filled(uyari_kelimesi):
                warnings.append(ValidationItem(
                    section="B2.2",
                    field_path="b2_zarar_tanimi.b2_2.uyari_kelimesi",
                    message="2.2 Zararlı ürünler için Uyarı Kelimesi ('Tehlike' veya 'Dikkat') seçilmelidir.",
                    regulation_ref="KKDİK Ek-2 md. 2.2",
                    severity="WARNING"
                ))

        # -------------------------------------------------------------
        # KURAL 2: BÖLÜM 3 (3.1 XOR 3.2 Kuralı - md. 0.3.1, 3. Bölüm)
        # -------------------------------------------------------------
        b3_tip = _get_nested(sds_dict, "b3_bilesim", "tip", default="karisim")
        madde_kimlik = _get_nested(sds_dict, "b3_bilesim", "madde", "kimyasal_kimlik")
        madde_cas = _get_nested(sds_dict, "b3_bilesim", "madde", "cas_no")
        madde_filled = self._is_filled(madde_kimlik) or self._is_filled(madde_cas)

        bilesenler = _get_nested(sds_dict, "b3_bilesim", "karisim", "bilesenler", default=[])
        karisim_filled = len(bilesenler) > 0

        if b3_tip == "madde":
            if not madde_filled:
                errors.append(ValidationItem(
                    section="B3.1",
                    field_path="b3_bilesim.madde.kimyasal_kimlik",
                    message="Bölüm 3 'Madde' (3.1) olarak seçilmiştir; kimyasal kimlik veya CAS/EC numarası girilmelidir.",
                    regulation_ref="KKDİK Ek-2 md. 3.1",
                    severity="ERROR"
                ))
            if karisim_filled:
                warnings.append(ValidationItem(
                    section="B3",
                    field_path="b3_bilesim.karisim.bilesenler",
                    message="3. Bölüm'de hem madde (3.1) hem karışım bileşeni (3.2) birlikte yer alamaz. Sadece 3.1 geçerli olacaktır.",
                    regulation_ref="KKDİK Ek-2 md. 0.3.1, 3. Bölüm (XOR)",
                    severity="WARNING"
                ))
        elif b3_tip == "karisim":
            if not karisim_filled and not siniflandirilmamis:
                errors.append(ValidationItem(
                    section="B3.2",
                    field_path="b3_bilesim.karisim.bilesenler",
                    message="Bölüm 3 'Karışım' (3.2) olarak seçilmiştir; en az bir bileşen bilgisi girilmelidir.",
                    regulation_ref="KKDİK Ek-2 md. 3.2",
                    severity="ERROR"
                ))
            if madde_filled:
                warnings.append(ValidationItem(
                    section="B3",
                    field_path="b3_bilesim.madde.kimyasal_kimlik",
                    message="3. Bölüm'de hem madde (3.1) hem karışım bileşeni (3.2) birlikte yer alamaz. Sadece 3.2 geçerli olacaktır.",
                    regulation_ref="KKDİK Ek-2 md. 0.3.1, 3. Bölüm (XOR)",
                    severity="WARNING"
                ))

        # -------------------------------------------------------------
        # BÖLÜM 4 - 15 ALAN DOLULUK KONTROLLERİ (md. 0.4 Kuralı)
        # -------------------------------------------------------------
        # B4 İlk Yardım
        for sub_key, sub_label in [("soluma", "Soluma"), ("cilt_temasi", "Cilt Teması"), ("goz_temasi", "Göz Teması"), ("yutma", "Yutma")]:
            val = _get_nested(sds_dict, "b4_ilk_yardim", "b4_1", sub_key)
            if not self._is_filled(val):
                errors.append(ValidationItem(
                    section="B4.1",
                    field_path=f"b4_ilk_yardim.b4_1.{sub_key}",
                    message=f"4.1 İlk yardım önlemleri ({sub_label}) boş bırakılamaz. Gerekirse 'Özel bir önlem gerekmez' veya 'Bilgi yok' yazınız.",
                    regulation_ref="KKDİK Ek-2 md. 0.4, md. 4.1",
                    severity="ERROR"
                ))

        # B5 Yangınla Mücadele
        uygun_sondurucu = _get_nested(sds_dict, "b5_yangin_mucadele", "b5_1", "uygun_sondurucu")
        if not self._is_filled(uygun_sondurucu):
            errors.append(ValidationItem(
                section="B5.1",
                field_path="b5_yangin_mucadele.b5_1.uygun_sondurucu",
                message="5.1 Uygun yangın söndürücü maddeler boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 5.1",
                severity="ERROR"
            ))

        # B6 Kaza Sonucu Yayılma
        kisisel_acil_olmayan = _get_nested(sds_dict, "b6_kaza_sonucu_yayilma", "b6_1", "kisisel_onlemler_acil_olmayan")
        kisisel_acil_mudahale = _get_nested(sds_dict, "b6_kaza_sonucu_yayilma", "b6_1", "kisisel_onlemler_acil_mudahale")
        if not self._is_filled(kisisel_acil_olmayan) and not self._is_filled(kisisel_acil_mudahale):
            errors.append(ValidationItem(
                section="B6.1",
                field_path="b6_kaza_sonucu_yayilma.b6_1.kisisel_onlemler_acil_olmayan",
                message="6.1 Kişisel önlemler, koruyucu ekipman ve acil durum prosedürleri boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 6.1",
                severity="ERROR"
            ))

        cevresel_onlemler = _get_nested(sds_dict, "b6_kaza_sonucu_yayilma", "b6_2_cevresel_onlemler")
        if not self._is_filled(cevresel_onlemler):
            errors.append(ValidationItem(
                section="B6.2",
                field_path="b6_kaza_sonucu_yayilma.b6_2_cevresel_onlemler",
                message="6.2 Çevresel önlemler boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 6.2",
                severity="ERROR"
            ))

        temizleme_yontemleri = _get_nested(sds_dict, "b6_kaza_sonucu_yayilma", "b6_3_kontrol_temizleme_yontemleri")
        if not self._is_filled(temizleme_yontemleri):
            errors.append(ValidationItem(
                section="B6.3",
                field_path="b6_kaza_sonucu_yayilma.b6_3_kontrol_temizleme_yontemleri",
                message="6.3 Muhafaza etme ve temizleme yöntemleri boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 6.3",
                severity="ERROR"
            ))

        # B7 Elleçleme Depolama
        ellecleme = _get_nested(sds_dict, "b7_ellecme_depolama", "b7_1_guvenli_ellecleme")
        if not self._is_filled(ellecleme):
            errors.append(ValidationItem(
                section="B7.1",
                field_path="b7_ellecme_depolama.b7_1_guvenli_ellecleme",
                message="7.1 Güvenli elleçleme için önlemler boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 7.1",
                severity="ERROR"
            ))

        depolama = _get_nested(sds_dict, "b7_ellecme_depolama", "b7_2", "guvenli_depolama_kosullari")
        if not self._is_filled(depolama):
            errors.append(ValidationItem(
                section="B7.2",
                field_path="b7_ellecme_depolama.b7_2.guvenli_depolama_kosullari",
                message="7.2 Güvenli depolama koşulları boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 7.2",
                severity="ERROR"
            ))

        # B8 Maruz Kalma Kontrolleri
        muhendislik = _get_nested(sds_dict, "b8_maruz_kalma_kontrolu", "b8_2", "muhendislik_kontrolleri")
        if not self._is_filled(muhendislik):
            errors.append(ValidationItem(
                section="B8.2",
                field_path="b8_maruz_kalma_kontrolu.b8_2.muhendislik_kontrolleri",
                message="8.2 Uygun mühendislik kontrolleri boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 8.2",
                severity="ERROR"
            ))

        # B9 Fiziksel ve Kimyasal Özellikler
        for prop_key, prop_label in [
            ("gorunum", "Görünüm"),
            ("koku", "Koku"),
            ("ph", "pH"),
            ("parlama_noktasi", "Parlama Noktası"),
            ("cozunurluk", "Çözünürlük")
        ]:
            val = _get_nested(sds_dict, "b9_fiziksel_kimyasal_ozellikler", "b9_1", prop_key)
            if not self._is_filled(val):
                errors.append(ValidationItem(
                    section="B9.1",
                    field_path=f"b9_fiziksel_kimyasal_ozellikler.b9_1.{prop_key}",
                    message=f"9.1 Temel fiziksel ve kimyasal özellik ({prop_label}) boş bırakılamaz. Uygulanamıyorsa 'Uygulanabilir değildir' veya 'Belirlenmemiştir' yazınız.",
                    regulation_ref="KKDİK Ek-2 md. 0.4, md. 9.1",
                    severity="ERROR"
                ))

        # B10 Kararlılık ve Tepkime
        tepkime = _get_nested(sds_dict, "b10_kararlilik_tepkime", "b10_1_tepkime")
        if not self._is_filled(tepkime):
            errors.append(ValidationItem(
                section="B10.1",
                field_path="b10_kararlilik_tepkime.b10_1_tepkime",
                message="10.1 Tepkime bilgisi boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 10.1",
                severity="ERROR"
            ))

        kararlilik = _get_nested(sds_dict, "b10_kararlilik_tepkime", "b10_2_kimyasal_kararlilik")
        if not self._is_filled(kararlilik):
            errors.append(ValidationItem(
                section="B10.2",
                field_path="b10_kararlilik_tepkime.b10_2_kimyasal_kararlilik",
                message="10.2 Kimyasal kararlılık bilgisi boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 10.2",
                severity="ERROR"
            ))

        # B11 Toksikolojik Bilgiler
        akut_toksisite = _get_nested(sds_dict, "b11_toksikolojik", "b11_1", "akut_toksisite")
        if not self._is_filled(akut_toksisite):
            errors.append(ValidationItem(
                section="B11.1",
                field_path="b11_toksikolojik.b11_1.akut_toksisite",
                message="11.1 Akut toksisite bilgisi boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 11.1",
                severity="ERROR"
            ))

        # B12 Ekolojik Bilgiler
        ekotoksisite = _get_nested(sds_dict, "b12_ekolojik", "b12_1_toksisite")
        if not self._is_filled(ekotoksisite):
            errors.append(ValidationItem(
                section="B12.1",
                field_path="b12_ekolojik.b12_1_toksisite",
                message="12.1 Ekotoksisite bilgisi boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 12.1",
                severity="ERROR"
            ))

        # B13 Bertaraf Bilgileri
        atik_isleme = _get_nested(sds_dict, "b13_bertaraf", "b13_1_atik_isleme_yontemleri")
        if not self._is_filled(atik_isleme):
            errors.append(ValidationItem(
                section="B13.1",
                field_path="b13_bertaraf.b13_1_atik_isleme_yontemleri",
                message="13.1 Atık işleme yöntemleri boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 13.1",
                severity="ERROR"
            ))

        # B14 Taşımacılık Bilgisi
        un_no = _get_nested(sds_dict, "b14_tasimacilik", "b14_1_un_numarasi")
        if not self._is_filled(un_no):
            errors.append(ValidationItem(
                section="B14.1",
                field_path="b14_tasimacilik.b14_1_un_numarasi",
                message="14.1 UN numarası boş bırakılamaz (Tehlikeli değilse 'Taşımacılık için tehlikeli madde değildir' yazınız).",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 14.1",
                severity="ERROR"
            ))

        # B15 Mevzuat Bilgisi
        mevzuat = _get_nested(sds_dict, "b15_mevzuat", "b15_1_ozel_mevzuat_hukumleri")
        if not self._is_filled(mevzuat):
            errors.append(ValidationItem(
                section="B15.1",
                field_path="b15_mevzuat.b15_1_ozel_mevzuat_hukumleri",
                message="15.1 Madde veya karışıma özel güvenlik, sağlık ve çevre mevzuatı hükümleri boş bırakılamaz.",
                regulation_ref="KKDİK Ek-2 md. 0.4, md. 15.1",
                severity="ERROR"
            ))

        # -------------------------------------------------------------
        # KURAL 5: H-Kodları 16. Bölüm Tam Metin Referansı (md. 2.1, 16.d)
        # -------------------------------------------------------------
        found_h_codes = reference_service.extract_h_codes_from_sds(sds_dict)
        b16_tam_h = _get_nested(sds_dict, "b16_diger_bilgiler", "tam_h_ifadeleri", default=[])
        b16_h_text_combined = " ".join([str(x) for x in b16_tam_h])

        missing_h_in_b16 = []
        for code in found_h_codes:
            if code not in b16_h_text_combined:
                missing_h_in_b16.append(code)

        if missing_h_in_b16:
            warnings.append(ValidationItem(
                section="B16",
                field_path="b16_diger_bilgiler.tam_h_ifadeleri",
                message=f"Bölüm 2 ve 3'te geçen H-kodlarının ({', '.join(missing_h_in_b16)}) tam metinleri 16. Bölüm'de listelenmelidir.",
                regulation_ref="KKDİK Ek-2 md. 2.1, md. 16.d",
                severity="WARNING"
            ))

        # -------------------------------------------------------------
        # İlerleme (Section Progress) Hesabı
        # -------------------------------------------------------------
        section_progress = self._calculate_progress(sds_dict, errors, warnings)
        overall_completion = round(
            sum(p.completion_percentage for p in section_progress) / len(section_progress), 1
        ) if section_progress else 0.0

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid_for_export=is_valid,
            total_errors=len(errors),
            total_warnings=len(warnings),
            overall_completion_percentage=overall_completion,
            errors=errors,
            warnings=warnings,
            section_progress=section_progress
        )

    def _check_forbidden_phrases(self, data: Any, warnings: List[ValidationItem], path: str = ""):
        """
        Tüm metin alanlarını özyinelemeli tarayarak yasaklı ifadeleri tespit eder.
        """
        if isinstance(data, dict):
            for k, v in data.items():
                current_path = f"{path}.{k}" if path else k
                self._check_forbidden_phrases(v, warnings, current_path)
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                current_path = f"{path}[{idx}]"
                self._check_forbidden_phrases(item, warnings, current_path)
        elif isinstance(data, str):
            for phrase, pattern in self.compiled_forbidden:
                if pattern.search(data):
                    warnings.append(ValidationItem(
                        section="B0.2.4",
                        field_path=path,
                        message=f"'{phrase}' ifadesi KKDİK Ek-2 Madde 0.2.4 gereği yasaklı veya yanıltıcı kabul edilir. Lütfen mevzuata uygun net bir ifade kullanınız.",
                        regulation_ref="KKDİK Ek-2 md. 0.2.4",
                        severity="WARNING"
                    ))

    def _calculate_progress(
        self,
        sds_dict: Dict[str, Any],
        errors: List[ValidationItem],
        warnings: List[ValidationItem]
    ) -> List[SectionProgress]:
        """
        16 bölümün her birinin alt bölüm doluluk oranını ve durumunu hesaplar.
        """
        progress_list = []
        error_sections = {e.section.split('.')[0] for e in errors}
        warning_sections = {w.section.split('.')[0] for w in warnings}

        section_checks = {
            1: [
                _get_nested(sds_dict, "b1_kimlik", "b1_1", "madde_karisim_adi"),
                _get_nested(sds_dict, "b1_kimlik", "b1_2", "tanimlanmis_kullanimlar"),
                _get_nested(sds_dict, "b1_kimlik", "b1_3", "tedarikci_adi"),
                _get_nested(sds_dict, "b1_kimlik", "b1_4", "acil_telefon"),
            ],
            2: [
                _get_nested(sds_dict, "b2_zarar_tanimi", "b2_1", "siniflandirmalar") or
                _get_nested(sds_dict, "b2_zarar_tanimi", "b2_1", "siniflandirilmamis"),
                _get_nested(sds_dict, "b2_zarar_tanimi", "b2_2", "uyari_kelimesi") or
                _get_nested(sds_dict, "b2_zarar_tanimi", "b2_2", "h_ifadeleri"),
                _get_nested(sds_dict, "b2_zarar_tanimi", "b2_3", "pbt_vpvb_degerlendirme"),
            ],
            3: [
                _get_nested(sds_dict, "b3_bilesim", "madde", "kimyasal_kimlik") or
                _get_nested(sds_dict, "b3_bilesim", "karisim", "bilesenler"),
            ],
            4: [
                _get_nested(sds_dict, "b4_ilk_yardim", "b4_1", "soluma"),
                _get_nested(sds_dict, "b4_ilk_yardim", "b4_1", "cilt_temasi"),
                _get_nested(sds_dict, "b4_ilk_yardim", "b4_1", "goz_temasi"),
                _get_nested(sds_dict, "b4_ilk_yardim", "b4_1", "yutma"),
                _get_nested(sds_dict, "b4_ilk_yardim", "b4_2_belirtiler_etkiler"),
                _get_nested(sds_dict, "b4_ilk_yardim", "b4_3_acil_tibbi_mudahale"),
            ],
            5: [
                _get_nested(sds_dict, "b5_yangin_mucadele", "b5_1", "uygun_sondurucu"),
                _get_nested(sds_dict, "b5_yangin_mucadele", "b5_2_ozel_zararlar"),
                _get_nested(sds_dict, "b5_yangin_mucadele", "b5_3_sondurme_ekibi_tavsiyeleri"),
            ],
            6: [
                _get_nested(sds_dict, "b6_kaza_sonucu_yayilma", "b6_1", "kisisel_onlemler_acil_olmayan") or
                _get_nested(sds_dict, "b6_kaza_sonucu_yayilma", "b6_1", "kisisel_onlemler_acil_mudahale"),
                _get_nested(sds_dict, "b6_kaza_sonucu_yayilma", "b6_2_cevresel_onlemler"),
                _get_nested(sds_dict, "b6_kaza_sonucu_yayilma", "b6_3_kontrol_temizleme_yontemleri"),
                _get_nested(sds_dict, "b6_kaza_sonucu_yayilma", "b6_4_diger_bolumlere_atif"),
            ],
            7: [
                _get_nested(sds_dict, "b7_ellecme_depolama", "b7_1_guvenli_ellecleme"),
                _get_nested(sds_dict, "b7_ellecme_depolama", "b7_2", "guvenli_depolama_kosullari"),
                _get_nested(sds_dict, "b7_ellecme_depolama", "b7_3_belirli_son_kullanimlar"),
            ],
            8: [
                _get_nested(sds_dict, "b8_maruz_kalma_kontrolu", "b8_1_kontrol_parametreleri"),
                _get_nested(sds_dict, "b8_maruz_kalma_kontrolu", "b8_2", "muhendislik_kontrolleri"),
                _get_nested(sds_dict, "b8_maruz_kalma_kontrolu", "b8_2", "kkd", "cilt_el") or
                _get_nested(sds_dict, "b8_maruz_kalma_kontrolu", "b8_2", "kkd", "goz_yuz"),
            ],
            9: [
                _get_nested(sds_dict, "b9_fiziksel_kimyasal_ozellikler", "b9_1", "gorunum"),
                _get_nested(sds_dict, "b9_fiziksel_kimyasal_ozellikler", "b9_1", "koku"),
                _get_nested(sds_dict, "b9_fiziksel_kimyasal_ozellikler", "b9_1", "ph"),
                _get_nested(sds_dict, "b9_fiziksel_kimyasal_ozellikler", "b9_1", "parlama_noktasi"),
                _get_nested(sds_dict, "b9_fiziksel_kimyasal_ozellikler", "b9_1", "cozunurluk"),
            ],
            10: [
                _get_nested(sds_dict, "b10_kararlilik_tepkime", "b10_1_tepkime"),
                _get_nested(sds_dict, "b10_kararlilik_tepkime", "b10_2_kimyasal_kararlilik"),
                _get_nested(sds_dict, "b10_kararlilik_tepkime", "b10_3_zararli_reaksiyon_olasiligi"),
                _get_nested(sds_dict, "b10_kararlilik_tepkime", "b10_4_kacinilmasi_gereken_durumlar"),
            ],
            11: [
                _get_nested(sds_dict, "b11_toksikolojik", "b11_1", "akut_toksisite"),
                _get_nested(sds_dict, "b11_toksikolojik", "b11_1", "cilt_asinmasi_tahrisi"),
                _get_nested(sds_dict, "b11_toksikolojik", "b11_1", "goz_hasari"),
            ],
            12: [
                _get_nested(sds_dict, "b12_ekolojik", "b12_1_toksisite"),
                _get_nested(sds_dict, "b12_ekolojik", "b12_2_kalicilik_bozunabilirlik"),
                _get_nested(sds_dict, "b12_ekolojik", "b12_3_biyobirikim"),
            ],
            13: [
                _get_nested(sds_dict, "b13_bertaraf", "b13_1_atik_isleme_yontemleri"),
                _get_nested(sds_dict, "b13_bertaraf", "b13_1_ambalaj_atik_isleme"),
            ],
            14: [
                _get_nested(sds_dict, "b14_tasimacilik", "b14_1_un_numarasi"),
                _get_nested(sds_dict, "b14_tasimacilik", "b14_2_un_tasimacilik_adi"),
                _get_nested(sds_dict, "b14_tasimacilik", "b14_3_tasimacilik_sinifi"),
            ],
            15: [
                _get_nested(sds_dict, "b15_mevzuat", "b15_1_ozel_mevzuat_hukumleri"),
                _get_nested(sds_dict, "b15_mevzuat", "b15_2_kimyasal_guvenlik_degerlendirmesi"),
            ],
            16: [
                _get_nested(sds_dict, "b16_diger_bilgiler", "revizyon_aciklamasi") or
                _get_nested(sds_dict, "b16_diger_bilgiler", "tam_h_ifadeleri"),
            ]
        }

        for meta in SECTION_METADATA:
            num = meta["num"]
            code = meta["code"]
            title = meta["title"]
            checks = section_checks.get(num, [])
            total = len(checks)
            filled = sum(1 for item in checks if self._is_filled(item))
            pct = round((filled / total * 100.0), 1) if total > 0 else 100.0

            progress_list.append(SectionProgress(
                section_number=num,
                section_code=code,
                section_title=title,
                total_subsections=total,
                filled_subsections=filled,
                completion_percentage=pct,
                has_errors=code in error_sections,
                has_warnings=code in warning_sections
            ))

        return progress_list


validator_service = ValidatorService()
