"""
KKDİK Uyumlu 16 Bölümlük SDS Pydantic Veri Modelleri
Spesifikasyon 3. Bölüm ve KKDİK Ek-2 gereksinimlerine birebir uygun olarak tasarlanmıştır.
"""

from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field, model_validator, ConfigDict


# ==========================================
# META MODEL
# ==========================================
class SDSMeta(BaseModel):
    hazirlama_tarihi: Optional[str] = Field(None, description="Hazırlama tarihi (GG.AA.YYYY veya YYYY-AA-GG)")
    revizyon_tarihi: Optional[str] = Field(None, description="Revizyon tarihi")
    revizyon_no: str = Field("0", description="Revizyon numarası")
    versiyon_no: str = Field("1.0", description="Versiyon numarası")
    dil: str = Field("tr", description="SDS dili (varsayılan tr)")


# ==========================================
# BÖLÜM 1: MADDENİN / KARIŞIMIN VE ŞİRKETİN / DAĞITICININ KİMLİĞİ
# ==========================================
class B1_1_MaddeKarisimKimlik(BaseModel):
    madde_karisim_adi: str = Field("", description="Madde veya karışımın ticari / kimyasal adı")
    kayit_numarasi: Optional[str] = Field(None, description="KKDİK / REACH Kayıt Numarası (varsa)")
    diger_adlar: List[str] = Field(default_factory=list, description="Diğer tanımlayıcı adlar, eşanlamlılar")

class B1_2_Kullanimlar(BaseModel):
    tanimlanmis_kullanimlar: List[str] = Field(default_factory=list, description="Belirlenmiş / tavsiye edilen kullanım alanları")
    tavsiye_edilmeyen_kullanimlar: List[str] = Field(default_factory=list, description="Tavsiye edilmeyen kullanım alanları")

class B1_3_Tedarikci(BaseModel):
    tedarikci_adi: str = Field("", description="Tedarikçi / İmalatçı / İthalatçı Şirket Adı")
    adres: str = Field("", description="Şirket Açık Adresi")
    telefon: str = Field("", description="Telefon Numarası")
    eposta: str = Field("", description="Güvenlik Bilgi Formundan sorumlu yetkili e-posta adresi")
    yetkili_kisi: str = Field("", description="GBF Hazırlayıcısı / İletişim Kişisi")

class B1_4_AcilDurum(BaseModel):
    acil_telefon: str = Field("", description="Acil durum telefon numarası (ör. Ulusal Zehir Merkezi 114 veya şirket acil no)")
    hizmet_kisitlamasi: Optional[str] = Field(None, description="Acil hat çalışma saatleri veya hizmet kısıtlaması (varsa)")

class B1_Kimlik(BaseModel):
    b1_1: B1_1_MaddeKarisimKimlik = Field(default_factory=B1_1_MaddeKarisimKimlik)
    b1_2: B1_2_Kullanimlar = Field(default_factory=B1_2_Kullanimlar)
    b1_3: B1_3_Tedarikci = Field(default_factory=B1_3_Tedarikci)
    b1_4: B1_4_AcilDurum = Field(default_factory=B1_4_AcilDurum)


# ==========================================
# BÖLÜM 2: ZARARLILIK TANIMLANMASI
# ==========================================
class ClassificationItem(BaseModel):
    zararlilik_sinifi: str = Field("", description="Zararlılık sınıfı (ör. Alevlenir Sıvılar, Cilt Aşınması)")
    kategori: str = Field("", description="Kategori (ör. Kategori 2, Kategori 1B)")
    h_kodu: str = Field("", description="Zararlılık ifadesi kodu (ör. H225, H314)")

class B2_1_Siniflandirma(BaseModel):
    siniflandirmalar: List[ClassificationItem] = Field(default_factory=list, description="SEA / KKDİK sınıflandırma listesi")
    siniflandirilmamis: bool = Field(False, description="Ürün zararlı olarak sınıflandırılmamış ise True")
    siniflandirilmama_gerekcesi: Optional[str] = Field(None, description="Sınıflandırılmamış ise açık mevzuat gerekçesi")

class B2_2_EtiketUnsurlari(BaseModel):
    piktogramlar: List[str] = Field(default_factory=list, description="GHS Piktogram kodları (ör. GHS02, GHS07)")
    uyari_kelimesi: Optional[str] = Field(None, description="Uyarı kelimesi ('Tehlike', 'Dikkat' veya 'Yok')")
    h_ifadeleri: List[str] = Field(default_factory=list, description="H-kodları listesi (ör. ['H225', 'H319'])")
    p_ifadeleri: List[str] = Field(default_factory=list, description="P-kodları listesi (ör. ['P210', 'P280', 'P305+P351+P338'])")

class B2_3_DigerZararlar(BaseModel):
    pbt_vpvb_degerlendirme: Optional[str] = Field(None, description="PBT ve vPvB değerlendirme sonuçları")
    diger_zararlar_aciklama: Optional[str] = Field(None, description="Diğer zararlar (toz patlaması riski, endokrin bozucu vb.)")

class B2_ZararTanimi(BaseModel):
    b2_1: B2_1_Siniflandirma = Field(default_factory=B2_1_Siniflandirma)
    b2_2: B2_2_EtiketUnsurlari = Field(default_factory=B2_2_EtiketUnsurlari)
    b2_3: B2_3_DigerZararlar = Field(default_factory=B2_3_DigerZararlar)


# ==========================================
# BÖLÜM 3: BİLEŞİMİ / İÇİNDEKİLER HAKKINDA BİLGİ (3.1 XOR 3.2)
# ==========================================
class B3_1_MaddeDetay(BaseModel):
    kimyasal_kimlik: Optional[str] = Field(None, description="Maddenin kimyasal adı / IUPAC adı")
    cas_no: Optional[str] = Field(None, description="CAS Numarası")
    ec_no: Optional[str] = Field(None, description="EC / EINECS Numarası")
    safsizliklar: List[str] = Field(default_factory=list, description="Sınıflandırmaya etki eden safsızlıklar / katkı maddeleri")

class MixtureComponentItem(BaseModel):
    ad: str = Field("", description="Bileşen kimyasal / ticari adı")
    cas_no: Optional[str] = Field(None, description="CAS Numarası")
    ec_no: Optional[str] = Field(None, description="EC / EINECS Numarası")
    kayit_no: Optional[str] = Field(None, description="KKDİK / REACH Kayıt Numarası")
    konsantrasyon: str = Field("", description="Ağırlıkça % veya konsantrasyon aralığı (ör. %10-25)")
    siniflandirma: str = Field("", description="Bileşenin SEA sınıflandırması ve H-ifadeleri")

class B3_2_KarisimDetay(BaseModel):
    bilesenler: List[MixtureComponentItem] = Field(default_factory=list, description="Karışımı oluşturan tehlikeli bileşenler listesi")

class B3_Bilesim(BaseModel):
    tip: Literal["madde", "karisim"] = Field("karisim", description="Ürün türü: 'madde' (3.1) veya 'karisim' (3.2)")
    madde: Optional[B3_1_MaddeDetay] = Field(default_factory=B3_1_MaddeDetay, description="3.1 Madde bilgileri")
    karisim: Optional[B3_2_KarisimDetay] = Field(default_factory=B3_2_KarisimDetay, description="3.2 Karışım bileşen bilgileri")


# ==========================================
# BÖLÜM 4: İLK YARDIM ÖNLEMLERİ
# ==========================================
class B4_1_IlkYardimTanim(BaseModel):
    soluma: Optional[str] = Field(None, description="Solunması halinde ilk yardım")
    cilt_temasi: Optional[str] = Field(None, description="Cilt ile teması halinde ilk yardım")
    goz_temasi: Optional[str] = Field(None, description="Göz ile teması halinde ilk yardım")
    yutma: Optional[str] = Field(None, description="Yutulması halinde ilk yardım")

class B4_IlkYardim(BaseModel):
    b4_1: B4_1_IlkYardimTanim = Field(default_factory=B4_1_IlkYardimTanim)
    b4_2_belirtiler_etkiler: Optional[str] = Field(None, description="4.2 Akut ve sonradan görülen en önemli belirtiler ve etkiler")
    b4_3_acil_tibbi_mudahale: Optional[str] = Field(None, description="4.3 Tıbbi müdahale ve özel tedavi gereği için ilk işaretler")


# ==========================================
# BÖLÜM 5: YANGINLA MÜCADELE ÖNLEMLERİ
# ==========================================
class B5_1_SondurucuMaddeler(BaseModel):
    uygun_sondurucu: Optional[str] = Field(None, description="Uygun yangın söndürücü maddeler")
    uygun_olmayan_sondurucu: Optional[str] = Field(None, description="Güvenlik nedeniyle kullanılmaması gereken söndürücüler")

class B5_YanginMucadele(BaseModel):
    b5_1: B5_1_SondurucuMaddeler = Field(default_factory=B5_1_SondurucuMaddeler)
    b5_2_ozel_zararlar: Optional[str] = Field(None, description="5.2 Madde veya karışımdan kaynaklanan özel zararlar (yanma ürünleri vb.)")
    b5_3_sondurme_ekibi_tavsiyeleri: Optional[str] = Field(None, description="5.3 Yangın söndürme ekipleri için tavsiyeler ve koruyucu ekipman")


# ==========================================
# BÖLÜM 6: KAZA SONUCU YAYILMAYA KARŞI ÖNLEMLER
# ==========================================
class B6_1_KisiselOnlemler(BaseModel):
    kisisel_onlemler_acil_olmayan: Optional[str] = Field(None, description="Acil durum personeli olmayanlar için önlemler")
    kisisel_onlemler_acil_mudahale: Optional[str] = Field(None, description="Acil durumda müdahale edenler için önlemler")

class B6_KazaSonucuYayilma(BaseModel):
    b6_1: B6_1_KisiselOnlemler = Field(default_factory=B6_1_KisiselOnlemler)
    b6_2_cevresel_onlemler: Optional[str] = Field(None, description="6.2 Çevresel önlemler")
    b6_3_kontrol_temizleme_yontemleri: Optional[str] = Field(None, description="6.3 Muhafaza etme ve temizleme için yöntemler ve materyaller")
    b6_4_diger_bolumlere_atif: Optional[str] = Field(None, description="6.4 Diğer bölümlere atıflar (ör. Bölüm 8 ve Bölüm 13)")


# ==========================================
# BÖLÜM 7: ELLEÇLEME VE DEPOLAMA
# ==========================================
class B7_2_Depolama(BaseModel):
    guvenli_depolama_kosullari: Optional[str] = Field(None, description="Uyumsuzluklar da dâhil olmak üzere güvenli depolama koşulları")
    uyumsuzluklar: Optional[str] = Field(None, description="Birlikte depolanmaması gereken uyumsuz maddeler")

class B7_EllecmeDepolama(BaseModel):
    b7_1_guvenli_ellecleme: Optional[str] = Field(None, description="7.1 Güvenli elleçleme için önlemler")
    b7_2: B7_2_Depolama = Field(default_factory=B7_2_Depolama)
    b7_3_belirli_son_kullanimlar: Optional[str] = Field(None, description="7.3 Belirli son kullanımlar")


# ==========================================
# BÖLÜM 8: MARUZ KALMA KONTROLLERİ / KİŞİSEL KORUNMA
# ==========================================
class ExposureControlParamItem(BaseModel):
    madde: str = Field("", description="Madde veya bileşen adı")
    sinir_degeri: str = Field("", description="Mesleki maruziyet sınır değeri (TWA / STEL)")
    birim: str = Field("", description="Birim (mg/m³, ppm vb.)")
    yasal_dayanak: str = Field("", description="Kaynak mevzuat / standart (ör. Kimyasal Maddelerle Çalışmalarda Sağlık ve Güvenlik Önlemleri)")

class KkdPersonalProtectionItem(BaseModel):
    goz_yuz: Optional[str] = Field(None, description="Göz / Yüz koruması (ör. EN 166 uyumlu koruyucu gözlük)")
    cilt_el: Optional[str] = Field(None, description="Ellerin korunması (ör. EN 374 uyumlu nitril eldiven)")
    cilt_diger: Optional[str] = Field(None, description="Cildin diğer kısımlarının korunması (koruyucu önlük/elbise)")
    solunum: Optional[str] = Field(None, description="Solunum sisteminin korunması (ör. A2P2 filtreli maske)")
    isil: Optional[str] = Field(None, description="Isıl zararlara karşı koruma")

class B8_2_MaruzKalmaKontrolleri(BaseModel):
    muhendislik_kontrolleri: Optional[str] = Field(None, description="Uygun mühendislik kontrolleri (havalandırma vb.)")
    kkd: KkdPersonalProtectionItem = Field(default_factory=KkdPersonalProtectionItem, description="Kişisel koruyucu donanım")
    cevresel_kontroller: Optional[str] = Field(None, description="Çevresel maruz kalma kontrolleri")

class B8_MaruzKalmaKontrolu(BaseModel):
    b8_1_kontrol_parametreleri: List[ExposureControlParamItem] = Field(default_factory=list, description="8.1 Kontrol parametreleri")
    b8_2: B8_2_MaruzKalmaKontrolleri = Field(default_factory=B8_2_MaruzKalmaKontrolleri)


# ==========================================
# BÖLÜM 9: FİZİKSEL VE KİMYASAL ÖZELLİKLER
# ==========================================
class B9_1_TemelOzellikler(BaseModel):
    gorunum: Optional[str] = Field(None, description="Fiziksel hal, renk")
    koku: Optional[str] = Field(None, description="Koku")
    koku_esigi: Optional[str] = Field(None, description="Koku eşiği")
    ph: Optional[str] = Field(None, description="pH değeri")
    erime_noktasi: Optional[str] = Field(None, description="Erime / donma noktası")
    kaynama_noktasi: Optional[str] = Field(None, description="İlk kaynama noktası ve kaynama aralığı")
    parlama_noktasi: Optional[str] = Field(None, description="Parlama noktası")
    buharlasma_hizi: Optional[str] = Field(None, description="Buharlaşma hızı")
    alevlenirlik: Optional[str] = Field(None, description="Alevlenirlik (katı, gaz)")
    ust_alt_limitler: Optional[str] = Field(None, description="Üst / alt alevlenirlik veya patlayıcı limitleri")
    buhar_basinci: Optional[str] = Field(None, description="Buhar basıncı")
    buhar_yogunlugu: Optional[str] = Field(None, description="Buhar yoğunluğu")
    bagil_yogunluk: Optional[str] = Field(None, description="Bağıl yoğunluk / özgül ağırlık")
    cozunurluk: Optional[str] = Field(None, description="Çözünürlük (suda vb.)")
    dagilim_katsayisi_log_kow: Optional[str] = Field(None, description="Dağılım katsayısı: n-oktanol/su (log Kow)")
    kendiliginden_tutusma_sicakligi: Optional[str] = Field(None, description="Kendiliğinden tutuşma sıcaklığı")
    bozunma_sicakligi: Optional[str] = Field(None, description="Bozunma sıcaklığı")
    akiskanlik: Optional[str] = Field(None, description="Akışkanlık / viskozite (kinematik/dinamik)")
    patlayici_ozellikler: Optional[str] = Field(None, description="Patlayıcı özellikler")
    oksitleyici_ozellikler: Optional[str] = Field(None, description="Oksitleyici özellikler")

class B9_FizikselKimyasalOzellikler(BaseModel):
    b9_1: B9_1_TemelOzellikler = Field(default_factory=B9_1_TemelOzellikler)
    b9_2_diger_bilgiler: Optional[str] = Field(None, description="9.2 Diğer bilgiler (karışabilirlik, iletkenlik, yağda çözünürlük vb.)")


# ==========================================
# BÖLÜM 10: KARARLILIK VE TEPKİME
# ==========================================
class B10_KararlilikTepkime(BaseModel):
    b10_1_tepkime: Optional[str] = Field(None, description="10.1 Tepkime")
    b10_2_kimyasal_kararlilik: Optional[str] = Field(None, description="10.2 Kimyasal kararlılık")
    b10_3_zararli_reaksiyon_olasiligi: Optional[str] = Field(None, description="10.3 Zararlı reaksiyon olasılığı")
    b10_4_kacinilmasi_gereken_durumlar: Optional[str] = Field(None, description="10.4 Kaçınılması gereken durumlar (yüksek sıcaklık, ışık vb.)")
    b10_5_kacinilmasi_gereken_maddeler: Optional[str] = Field(None, description="10.5 Kaçınılması gereken maddeler (kuvvetli asitler, bazlar vb.)")
    b10_6_zararli_bozunma_urunleri: Optional[str] = Field(None, description="10.6 Zararlı bozunma ürünleri")


# ==========================================
# BÖLÜM 11: TOKSİKOLOJİK BİLGİLER
# ==========================================
class B11_1_ToksikolojikEtkiler(BaseModel):
    akut_toksisite: Optional[str] = Field(None, description="Akut toksisite (LD50 / LC50)")
    cilt_asinmasi_tahrisi: Optional[str] = Field(None, description="Cilt aşınması / tahrişi")
    goz_hasari: Optional[str] = Field(None, description="Ciddi göz hasarları / tahrişi")
    solunum_cilt_hassasiyeti: Optional[str] = Field(None, description="Solunum yolları veya cilt hassaslaşması")
    mutajenite: Optional[str] = Field(None, description="Eşey hücre mutajenitesi")
    kanserojenite: Optional[str] = Field(None, description="Kanserojenite")
    ureme_toksisitesi: Optional[str] = Field(None, description="Üreme toksisitesi")
    bhot_tek_maruz: Optional[str] = Field(None, description="Belirli Hedef Organ Toksisitesi (BHOT) - tek maruz kalma")
    bhot_tekrarli: Optional[str] = Field(None, description="Belirli Hedef Organ Toksisitesi (BHOT) - tekrarlı maruz kalma")
    aspirasyon_zarari: Optional[str] = Field(None, description="Aspirasyon zararı")
    maruz_kalma_yollari: Optional[str] = Field(None, description="Olası maruz kalma yollarına ilişkin bilgiler")
    belirtiler: Optional[str] = Field(None, description="Fiziksel, kimyasal ve toksikolojik özellikler ile ilgili belirtiler")
    kronik_etkiler: Optional[str] = Field(None, description="Gecikmeli ve hemen ortaya çıkan etkiler ile kısa ve uzun süreli maruz kalmadan doğan kronik etkiler")

class B11_Toksikolojik(BaseModel):
    b11_1: B11_1_ToksikolojikEtkiler = Field(default_factory=B11_1_ToksikolojikEtkiler)


# ==========================================
# BÖLÜM 12: EKOLOJİK BİLGİLER
# ==========================================
class B12_Ekolojik(BaseModel):
    b12_1_toksisite: Optional[str] = Field(None, description="12.1 Ekotoksisite (balık, su piresi, alg)")
    b12_2_kalicilik_bozunabilirlik: Optional[str] = Field(None, description="12.2 Kalıcılık ve bozunabilirlik")
    b12_3_biyobirikim: Optional[str] = Field(None, description="12.3 Biyobirikim potansiyeli (BCF)")
    b12_4_topraktaki_hareketlilik: Optional[str] = Field(None, description="12.4 Toprakta hareketlilik (Koc)")
    b12_5_pbt_vpvb_sonuclari: Optional[str] = Field(None, description="12.5 PBT ve vPvB değerlendirmesinin sonuçları")
    b12_6_diger_olumsuz_etkiler: Optional[str] = Field(None, description="12.6 Diğer olumsuz etkiler")


# ==========================================
# BÖLÜM 13: BERTARAF ETME BİLGİLERİ
# ==========================================
class B13_Bertaraf(BaseModel):
    b13_1_atik_isleme_yontemleri: Optional[str] = Field(None, description="13.1 Atık işleme yöntemleri")
    b13_1_ambalaj_atik_isleme: Optional[str] = Field(None, description="Ambalaj atıklarının işlenmesi")
    b13_1_kanalizasyon_uyarisi: Optional[str] = Field(None, description="Kanalizasyona boşaltılmaması uyarısı ve atık kodları")


# ==========================================
# BÖLÜM 14: TAŞIMACILIK BİLGİSİ
# ==========================================
class B14_Tasimacilik(BaseModel):
    b14_1_un_numarasi: Optional[str] = Field(None, description="14.1 UN Numarası (ör. UN 1263 veya 'Taşımacılık için tehlikeli madde değildir')")
    b14_2_un_tasimacilik_adi: Optional[str] = Field(None, description="14.2 Uygun UN taşımacılık adı")
    b14_3_tasimacilik_sinifi: Optional[str] = Field(None, description="14.3 Taşımacılık zararlılık sınıf(lar)ı")
    b14_4_ambalajlama_grubu: Optional[str] = Field(None, description="14.4 Ambalajlama grubu (PG I, II, III)")
    b14_5_cevresel_zararlar: Optional[str] = Field(None, description="14.5 Çevresel zararlar (Deniz Kirletici vb.)")
    b14_6_kullanici_ozel_onlemler: Optional[str] = Field(None, description="14.6 Kullanıcı için özel önlemler")
    b14_7_marpol_ibc: Optional[str] = Field(None, description="14.7 MARPOL 73/78 Ek II ve IBC koduna göre dökme taşımacılık")


# ==========================================
# BÖLÜM 15: MEVZUAT BİLGİSİ
# ==========================================
class B15_Mevzuat(BaseModel):
    b15_1_ozel_mevzuat_hukumleri: Optional[str] = Field(None, description="15.1 Madde veya karışıma özel güvenlik, sağlık ve çevre mevzuatı")
    b15_2_kimyasal_guvenlik_degerlendirmesi: Optional[str] = Field(None, description="15.2 Kimyasal güvenlik değerlendirmesi yapıldı mı? (Açıklama)")


# ==========================================
# BÖLÜM 16: DİĞER BİLGİLER
# ==========================================
class B16_DigerBilgiler(BaseModel):
    revizyon_aciklamasi: Optional[str] = Field(None, description="Revizyon açıklaması ve yapılan değişiklikler")
    kisaltmalar_anahtari: Optional[str] = Field(None, description="Kısaltmalar ve akronimler anahtarı")
    literatur_referanslari: Optional[str] = Field(None, description="Önemli literatür referansları ve veri kaynakları")
    degerlendirme_yontemleri: Optional[str] = Field(None, description="Karışımın sınıflandırılmasında kullanılan değerlendirme yöntemleri")
    tam_h_ifadeleri: List[str] = Field(default_factory=list, description="2-15. bölümlerde geçen tüm H-kodlarının tam metinleri")
    egitim_tavsiyeleri: Optional[str] = Field(None, description="İşçiler için eğitim tavsiyeleri")


# ==========================================
# 16 BÖLÜMLÜK BİRLEŞİK SDS MODELİ
# ==========================================
class SDSModel(BaseModel):
    meta: SDSMeta = Field(default_factory=SDSMeta)
    b1_kimlik: B1_Kimlik = Field(default_factory=B1_Kimlik)
    b2_zarar_tanimi: B2_ZararTanimi = Field(default_factory=B2_ZararTanimi)
    b3_bilesim: B3_Bilesim = Field(default_factory=B3_Bilesim)
    b4_ilk_yardim: B4_IlkYardim = Field(default_factory=B4_IlkYardim)
    b5_yangin_mucadele: B5_YanginMucadele = Field(default_factory=B5_YanginMucadele)
    b6_kaza_sonucu_yayilma: B6_KazaSonucuYayilma = Field(default_factory=B6_KazaSonucuYayilma)
    b7_ellecme_depolama: B7_EllecmeDepolama = Field(default_factory=B7_EllecmeDepolama)
    b8_maruz_kalma_kontrolu: B8_MaruzKalmaKontrolu = Field(default_factory=B8_MaruzKalmaKontrolu)
    b9_fiziksel_kimyasal_ozellikler: B9_FizikselKimyasalOzellikler = Field(default_factory=B9_FizikselKimyasalOzellikler)
    b10_kararlilik_tepkime: B10_KararlilikTepkime = Field(default_factory=B10_KararlilikTepkime)
    b11_toksikolojik: B11_Toksikolojik = Field(default_factory=B11_Toksikolojik)
    b12_ekolojik: B12_Ekolojik = Field(default_factory=B12_Ekolojik)
    b13_bertaraf: B13_Bertaraf = Field(default_factory=B13_Bertaraf)
    b14_tasimacilik: B14_Tasimacilik = Field(default_factory=B14_Tasimacilik)
    b15_mevzuat: B15_Mevzuat = Field(default_factory=B15_Mevzuat)
    b16_diger_bilgiler: B16_DigerBilgiler = Field(default_factory=B16_DigerBilgiler)

    model_config = ConfigDict(populate_by_name=True)
