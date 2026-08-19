"""
Pytest Test Yapılandırması ve Fikstürleri
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.schemas.sds_sections import SDSModel

# Bellek içi SQLite test veritabanı
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_valid_sds_dict():
    """Tüm zorunlu alanları doldurulmuş, geçerli bir SDS örneği"""
    return {
        "meta": {
            "hazirlama_tarihi": "18.08.2026",
            "revizyon_tarihi": "18.08.2026",
            "revizyon_no": "0",
            "versiyon_no": "1.0",
            "dil": "tr"
        },
        "b1_kimlik": {
            "b1_1": {
                "madde_karisim_adi": "Polyester Reçine Solüsyonu",
                "kayit_numarasi": "01-2119457290-43-0000",
                "diger_adlar": ["Polimerik Bağlayıcı", "Aypol PRS-100"]
            },
            "b1_2": {
                "tanimlanmis_kullanimlar": ["Endüstriyel kaplama ve kompozit üretimi"],
                "tavsiye_edilmeyen_kullanimlar": ["Tüketici tipi hobi uygulamaları"]
            },
            "b1_3": {
                "tedarikci_adi": "Aypol Kimya San. ve Tic. A.Ş.",
                "adres": "Kimyacılar OSB, 34956 Tuzla / İstanbul",
                "telefon": "+90 216 123 45 67",
                "eposta": "gbf@aypolkimya.com",
                "yetkili_kisi": "Kimyager Ahmet Yılmaz (Sertifika No: KDU01.12.05)"
            },
            "b1_4": {
                "acil_telefon": "114 (UZEM) / +90 216 123 45 68 (7/24 Şirket Acil)",
                "hizmet_kisitlamasi": "7/24 Kesintisiz hizmet"
            }
        },
        "b2_zarar_tanimi": {
            "b2_1": {
                "siniflandirmalar": [
                    {"zararlilik_sinifi": "Alevlenir Sıvılar", "kategori": "Kategori 3", "h_kodu": "H226"},
                    {"zararlilik_sinifi": "Cilt Tahrişi", "kategori": "Kategori 2", "h_kodu": "H315"},
                    {"zararlilik_sinifi": "Göz Tahrişi", "kategori": "Kategori 2", "h_kodu": "H319"}
                ],
                "siniflandirilmamis": False,
                "siniflandirilmama_gerekcesi": None
            },
            "b2_2": {
                "piktogramlar": ["GHS02", "GHS07"],
                "uyari_kelimesi": "Dikkat",
                "h_ifadeleri": ["H226", "H315", "H319"],
                "p_ifadeleri": ["P210", "P280", "P302+P352", "P305+P351+P338", "P501"]
            },
            "b2_3": {
                "pbt_vpvb_degerlendirme": "Maddeler PBT veya vPvB olarak değerlendirilmemiştir.",
                "diger_zararlar_aciklama": "Buharları hava ile patlayıcı karışım oluşturabilir."
            }
        },
        "b3_bilesim": {
            "tip": "karisim",
            "madde": None,
            "karisim": {
                "bilesenler": [
                    {
                        "ad": "Stiren",
                        "cas_no": "100-42-5",
                        "ec_no": "202-851-5",
                        "kayit_no": "01-2119457861-32-XXXX",
                        "konsantrasyon": "%30 - 40",
                        "siniflandirma": "Flam. Liq. 3 H226, Skin Irrit. 2 H315, Eye Irrit. 2 H319"
                    }
                ]
            }
        },
        "b4_ilk_yardim": {
            "b4_1": {
                "soluma": "Kazazedeyi temiz havaya çıkarın, rahat nefes almasını sağlayın.",
                "cilt_temasi": "Kirlenmiş elbiseleri çıkarın, cildi bol su ve sabunla yıkayın.",
                "goz_temasi": "Gözleri açık tutarak en az 15 dakika bol suyla yıkayın.",
                "yutma": "Ağzı bol su ile çalkalayın. Doktor tavsiyesi olmadan kusturmayın."
            },
            "b4_2_belirtiler_etkiler": "Göz ve ciltte kızarıklık, solunum yolu tahrişi.",
            "b4_3_acil_tibbi_mudahale": "Semptomatik tedavi uygulayınız."
        },
        "b5_yangin_mucadele": {
            "b5_1": {
                "uygun_sondurucu": "Köpük, kuru kimyevi toz, karbon dioksit (CO2)",
                "uygun_olmayan_sondurucu": "Doğrudan yüksek basınçlı su jeti"
            },
            "b5_2_ozel_zararlar": "Yanma sonucu karbon monoksit ve toksik gazlar açığa çıkabilir.",
            "b5_3_sondurme_ekibi_tavsiyeleri": "Bağımsız solunum cihazı ve tam koruyucu yangın elbisesi giyiniz."
        },
        "b6_kaza_sonucu_yayilma": {
            "b6_1": {
                "kisisel_onlemler_acil_olmayan": "Ateş kaynaklarını uzaklaştırın, alanı havalandırın.",
                "kisisel_onlemler_acil_mudahale": "Koruyucu eldiven ve gaz maskesi kullanın."
            },
            "b6_2_cevresel_onlemler": "Kanalizasyona, yüzey sularına ve toprağa karışmasını önleyin.",
            "b6_3_kontrol_temizleme_yontemleri": "Kum veya inert emici ile toplayıp uygun atık kabına alın.",
            "b6_4_diger_bolumlere_atif": "Kişisel korunma için Bölüm 8'e, bertaraf için Bölüm 13'e bakınız."
        },
        "b7_ellecme_depolama": {
            "b7_1_guvenli_ellecleme": "Statik elektriklenmeye karşı önlem alın. İyi havalandırılmış alanda çalışın.",
            "b7_2": {
                "guvenli_depolama_kosullari": "Serin, kuru, iyi havalandırılmış alanda 25°C altında muhafaza edin.",
                "uyumsuzluklar": "Kuvvetli oksitleyiciler ve peroksitlerden uzak tutun."
            },
            "b7_3_belirli_son_kullanimlar": "Bölüm 1.2'de belirtilen kullanımlar dışındaki alanlar için tedarikçiye danışınız."
        },
        "b8_maruz_kalma_kontrolu": {
            "b8_1_kontrol_parametreleri": [
                {
                    "madde": "Stiren",
                    "sinir_degeri": "TWA: 20 ppm (85 mg/m³), STEL: 40 ppm (170 mg/m³)",
                    "birim": "mg/m³",
                    "yasal_dayanak": "İş Sağlığı ve Güvenliği Mevzuatı"
                }
            ],
            "b8_2": {
                "muhendislik_kontrolleri": "Lokal egzoz havalandırması sağlayınız.",
                "kkd": {
                    "goz_yuz": "EN 166 uyumlu koruyucu gözlük",
                    "cilt_el": "EN 374 uyumlu nitril/bütil koruyucu eldiven",
                    "cilt_diger": "Antistatik koruyucu iş kıyafeti",
                    "solunum": "EN 14387 uyumlu A tipi organik buhar filtreli maske",
                    "isil": "Gerekli değildir."
                },
                "cevresel_kontroller": "Havalandırma bacalarından emisyon limitlerine uyulmalıdır."
            }
        },
        "b9_fiziksel_kimyasal_ozellikler": {
            "b9_1": {
                "gorunum": "Sıvı, Şeffaf sarımtırak",
                "koku": "Karakteristik stiren kokusu",
                "koku_esigi": "0.15 ppm",
                "ph": "Uygulanabilir değildir (susuz ortam)",
                "erime_noktasi": "-31 °C",
                "kaynama_noktasi": "145 °C",
                "parlama_noktasi": "31 °C (Kapalı kap)",
                "buharlasma_hizi": "Belirlenmemiştir",
                "alevlenirlik": "Alevlenir sıvı",
                "ust_alt_limitler": "%1.1 - %6.1",
                "buhar_basinci": "6.7 hPa (20°C)",
                "buhar_yogunlugu": "3.6 (Hava = 1)",
                "bagil_yogunluk": "1.10 g/cm³ (20°C)",
                "cozunurluk": "Suda çözünmez (< 0.24 g/l), aromatik solventlerde çözünür",
                "dagilim_katsayisi_log_kow": "2.96",
                "kendiliginden_tutusma_sicakligi": "490 °C",
                "bozunma_sicakligi": "> 200 °C",
                "akiskanlik": "600-800 mPa.s (25°C)",
                "patlayici_ozellikler": "Patlayıcı değildir.",
                "oksitleyici_ozellikler": "Oksitleyici değildir."
            },
            "b9_2_diger_bilgiler": "Katı Madde Oranı: %65 ± 2"
        },
        "b10_kararlilik_tepkime": {
            "b10_1_tepkime": "Normal kullanım koşullarında tehlikeli tepkime vermez.",
            "b10_2_kimyasal_kararlilik": "Tavsiye edilen depolama sıcaklıklarında kararlıdır.",
            "b10_3_zararli_reaksiyon_olasiligi": "Aşırı sıcakta kontrolsüz ekzotermik polimerizasyon gerçekleşebilir.",
            "b10_4_kacinilmasi_gereken_durumlar": "Isı, açık alev, doğrudan güneş ışığı.",
            "b10_5_kacinilmasi_gereken_maddeler": "Kuvvetli asitler, bazlar, peroksitler.",
            "b10_6_zararli_bozunma_urunleri": "Normal şartlarda oluşmaz. Yangında karbon oksitler."
        },
        "b11_toksikolojik": {
            "b11_1": {
                "akut_toksisite": "LD50 Oral (Sıçan): > 2000 mg/kg; LC50 Soluma (Sıçan, 4s): 11.8 mg/l",
                "cilt_asinmasi_tahrisi": "Ciltte tahrişe neden olur.",
                "goz_hasari": "Ciddi göz tahrişine neden olur.",
                "solunum_cilt_hassasiyeti": "Hassaslaşma etkisi bildirilmemiştir.",
                "mutajenite": "Sınıflandırma kriterlerini karşılamamaktadır.",
                "kanserojenite": "Sınıflandırma kriterlerini karşılamamaktadır.",
                "ureme_toksisitesi": "Sınıflandırma kriterlerini karşılamamaktadır.",
                "bhot_tek_maruz": "Solunum yolu tahrişine yol açabilir.",
                "bhot_tekrarli": "Uzun süreli veya tekrarlı maruz kalma sonucu işitme organlarına zarar verebilir.",
                "aspirasyon_zarari": "Aspirasyon zararı oluşturmaz.",
                "maruz_kalma_yollari": "Soluma, cilt ve göz teması.",
                "belirtiler": "Gözlerde yaşarma, ciltte kızarıklık, baş dönmesi.",
                "kronik_etkiler": "Sürekli maruziyet cilt kuruluğuna yol açabilir."
            }
        },
        "b12_ekolojik": {
            "b12_1_toksisite": "LC50 Balık (Pimephales promelas, 96s): 4.02 mg/l (Zararlı)",
            "b12_2_kalicilik_bozunabilirlik": "Biyolojik olarak kolayca parçalanabilir.",
            "b12_3_biyobirikim": "Düşük biyobirikim potansiyeli (BCF: 74)",
            "b12_4_topraktaki_hareketlilik": "Koc: 352 (Orta derece hareketlilik)",
            "b12_5_pbt_vpvb_sonuclari": "PBT/vPvB kriterlerini karşılamaz.",
            "b12_6_diger_olumsuz_etkiler": "Kanalizasyon ve su kaynaklarına dökülmemelidir."
        },
        "b13_bertaraf": {
            "b13_1_atik_isleme_yontemleri": "Lisanslı tehlikeli atık yakma veya bertaraf tesisine gönderilmelidir. Atık Kodu: 08 01 11*",
            "b13_1_ambalaj_atik_isleme": "Boş ambalajlar tehlikeli atık olarak lisanslı geri kazanım firmalarına verilmelidir.",
            "b13_1_kanalizasyon_uyarisi": "Kanalizasyona veya evsel atık depolarına kesinlikle dökmeyiniz."
        },
        "b14_tasimacilik": {
            "b14_1_un_numarasi": "UN 1866",
            "b14_2_un_tasimacilik_adi": "REÇİNE ÇÖZELTİSİ, alevlenebilir",
            "b14_3_tasimacilik_sinifi": "3",
            "b14_4_ambalajlama_grubu": "III",
            "b14_5_cevresel_zararlar": "Deniz Kirletici değildir.",
            "b14_6_kullanici_ozel_onlemler": "ADR/RID hükümlerine uygun şekilde taşınmalıdır.",
            "b14_7_marpol_ibc": "Uygulanabilir değildir."
        },
        "b15_mevzuat": {
            "b15_1_ozel_mevzuat_hukumleri": "KKDİK Yönetmeliği (RG: 30105), SEA Yönetmeliği (RG: 28848), Tehlikeli Maddelerin Karayoluyla Taşınması Yönetmeliği.",
            "b15_2_kimyasal_guvenlik_degerlendirmesi": "Bu karışım için henüz bir Kimyasal Güvenlik Değerlendirmesi gerçekleştirilmemiştir."
        },
        "b16_diger_bilgiler": {
            "revizyon_aciklamasi": "İlk versiyon, KKDİK Ek-2 formatında hazırlanmıştır.",
            "kisaltmalar_anahtari": "ADR: Tehlikeli Malların Karayolu ile Taşınması; TWA: Zaman Ağırlıklı Ortalama; STEL: Kısa Süreli Maruziyet Sınırı.",
            "literatur_referanslari": "ECHA Veritabanı, T.C. Çevre Şehircilik ve İklim Değişikliği Bakanlığı Kimyasallar Yönetimi Portalı.",
            "degerlendirme_yontemleri": "SEA Yönetmeliği hesaplama ve eşik değer yöntemleri.",
            "tam_h_ifadeleri": [
                "H226: Alevlenir sıvı ve buhar.",
                "H315: Cilt tahrişine yol açar.",
                "H319: Ciddi göz tahrişine yol açar."
            ],
            "egitim_tavsiyeleri": "Çalışanlar kimyasal maddelerle çalışma ve KKD kullanımı konusunda eğitilmelidir."
        }
    }
