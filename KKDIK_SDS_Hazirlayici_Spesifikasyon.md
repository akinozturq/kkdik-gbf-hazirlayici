# KKDİK Uyumlu SDS Hazırlayıcısı — v1 Proje Spesifikasyonu

## 0\. Özet

Aypol Kimyasal Güvenlik Bilgi Formu (SDS/GBF) hazırlama sürecini otomatikleştiren, tek
kullanıcılı, yerel çalışan bir masaüstü/web uygulaması. Kullanıcı ürün bilgilerini bir form
sihirbazından girer, uygulama KKDİK Ek-2'ye göre 16 bölümlük taslağı oluşturur, eksik
zorunlu alanları uyarır, isteğe bağlı olarak yapay zekâ ile metin önerileri üretir ve sonucu
PDF/DOCX olarak dışa aktarır.

\---

## 1\. Kullanıcı Akışları

### 1.1. Ürün Yönetimi

* Yeni kimyasal ürün kaydı oluşturma (ürün adı, ticari kod, ürün ailesi/kategori)
* Var olan bir üründen "kopyala → yeni ürün" (benzer formülasyonlar için hızlı başlangıç)
* Ürün listesi: arama, filtreleme (kategori, son güncelleme tarihi, tamamlanma durumu)
* Ürün silme/arşivleme

### 1.2. SDS Formu Doldurma (Sihirbaz)

* 16 bölüm, her biri ayrı adım (step) olarak sunulur
* Her adımda: zorunlu alan işaretleri, KKDİK madde/fıkra referansı (tooltip/yardım metni
olarak), önceki/sonraki gezinme, ilerleme çubuğu
* Serbest gezinme: kullanıcı adımları sırasız da doldurabilir, sihirbaz sadece rehberlik eder
* Taslak otomatik kaydedilir (yerel dosya/DB'ye anlık yazım)

### 1.3. Dışa Aktarma

* PDF: resmî GBF sayfa formatına yakın (16 bölüm, alt başlıklar, sayfa numarası "sayfa X/Y",
hazırlanma/revizyon tarihi üst bilgide)
* DOCX: aynı içerik, düzenlenebilir Word formatında (kurumsal şablon/antet ile)
* Her iki formatta da eksik zorunlu alan varsa dışa aktarmadan önce uyarı

\---

## 2\. Mevzuat ve İçerik Desteği

### 2.1. Rehberli Doğrulama Kuralları

* KKDİK Ek-2 gereği hiçbir alt bölüm boş bırakılamaz (0.4) → uygulama boş alanları
"N/A — gerekçesi: ..." gibi açık gerekçeyle doldurmayı zorunlu kılar, sessiz boş bırakmaya
izin vermez
* Zararlı olmadığını ima eden yasaklı ifadeler ('zararsız', 'sağlığa etkisi yok' vb. — madde
0.2.4) girildiğinde uyarı
* 

  3. Bölüm'de yalnızca 3.1 (madde) veya 3.2 (karışım) seçilir, ikisi birden değil
* Zararlılık ifadeleri kod olarak girilirse (H-kodları), 16. Bölüm'de tam metinlerinin
otomatik listelenmesi (0.2.4 / madde 16.d gereği)

### 2.2. AI Destekli Metin Önerisi Akışı

* Kullanıcı bir bölüme ham/madde madde bilgi girer (ör. "beyaz, hafif kokulu, pH 8-9 sulu
emülsiyon")
* AI bu girdiyi KKDİK'in ilgili bölüm için beklediği dil ve yapıya (açık, anlaşılır, net,
kısaltmasız — madde 0.2.4) uygun taslak metne dönüştürür
* Kullanıcı öneriyi kabul eder / düzenler / reddeder — AI çıktısı asla otomatik "son hal"
olarak kaydedilmez, her zaman onay adımı vardır
* Bölümler arası tutarlılık kontrolü (ör. Bölüm 2'deki sınıflandırma ile Bölüm 11/12'deki
toksikolojik/ekolojik veriler çelişiyorsa uyarı) — v1'de basit kural tabanlı, ileride AI
destekli olabilir

\---

## 3\. Veri Modeli — 16 Bölüm

Aşağıdaki şema hem form alanlarını hem de gelecekteki Pydantic modelini/DB şemasını
tanımlamak için kullanılabilir. Liste tipi alanlar (`\[]`) tekrarlanabilir satır grupları temsil
eder.

```
Product
├── id, urun\_adi, ticari\_kod, kategori, olusturma\_tarihi, son\_guncelleme
└── SDS
    ├── meta: hazirlama\_tarihi, revizyon\_no, versiyon\_no, dil (tr)
    │
    ├── B1\_Kimlik
    │   ├── 1.1: madde\_karisim\_adi, kayit\_numarasi?, diger\_adlar\[]
    │   ├── 1.2: tanimlanmis\_kullanimlar\[], tavsiye\_edilmeyen\_kullanimlar\[]
    │   ├── 1.3: tedarikci\_adi, adres, telefon, eposta, yetkili\_kisi
    │   └── 1.4: acil\_telefon, hizmet\_kisitlamasi?
    │
    ├── B2\_ZararTanimi
    │   ├── 2.1: siniflandirmalar\[] {zararlilik\_sinifi, kategori, h\_kodu}, siniflandirilmamis
    │   ├── 2.2: piktogramlar\[], uyari\_kelimesi, h\_ifadeleri\[], p\_ifadeleri\[]
    │   └── 2.3: pbt\_vpvb\_degerlendirme, diger\_zararlar\_aciklama
    │
    ├── B3\_Bilesim  (3.1 XOR 3.2)
    │   ├── 3.1 (madde): kimyasal\_kimlik, cas\_no?, ec\_no?, safsizliklar\[]
    │   └── 3.2 (karışım): bilesenler\[] {ad, cas\_no?, ec\_no?, kayit\_no?, konsantrasyon,
    │         siniflandirma}
    │
    ├── B4\_IlkYardim
    │   ├── 4.1: soluma, cilt\_temasi, goz\_temasi, yutma
    │   ├── 4.2: belirtiler\_etkiler
    │   └── 4.3: acil\_tibbi\_mudahale
    │
    ├── B5\_YanginMucadele
    │   ├── 5.1: uygun\_sondurucu, uygun\_olmayan\_sondurucu
    │   ├── 5.2: ozel\_zararlar
    │   └── 5.3: sondurme\_ekibi\_tavsiyeleri
    │
    ├── B6\_KazaSonucuYayilma
    │   ├── 6.1: kisisel\_onlemler\_acil\_olmayan, kisisel\_onlemler\_acil\_mudahale
    │   ├── 6.2: cevresel\_onlemler
    │   ├── 6.3: kontrol\_temizleme\_yontemleri
    │   └── 6.4: diger\_bolumlere\_atif
    │
    ├── B7\_EllecmeDepolama
    │   ├── 7.1: guvenli\_ellecleme
    │   ├── 7.2: guvenli\_depolama\_kosullari, uyumsuzluklar
    │   └── 7.3: belirli\_son\_kullanimlar
    │
    ├── B8\_MaruzKalmaKontrolu
    │   ├── 8.1: kontrol\_parametreleri\[] {madde, sinir\_degeri, birim, yasal\_dayanak}
    │   └── 8.2: muhendislik\_kontrolleri,
    │         kkd {goz\_yuz, cilt\_el, cilt\_diger, solunum, isil},
    │         cevresel\_kontroller
    │
    ├── B9\_FizikselKimyasalOzellikler
    │   ├── 9.1: gorunum, koku, koku\_esigi, ph, erime\_noktasi, kaynama\_noktasi,
    │   │     parlama\_noktasi, buharlasma\_hizi, alevlenirlik, ust\_alt\_limitler,
    │   │     buhar\_basinci, buhar\_yogunlugu, bagil\_yogunluk, cozunurluk,
    │   │     dagilim\_katsayisi\_log\_kow, kendiliginden\_tutusma\_sicakligi,
    │   │     bozunma\_sicakligi, akiskanlik, patlayici\_ozellikler, oksitleyici\_ozellikler
    │   └── 9.2: diger\_bilgiler (karisabilirlik, iletkenlik, vb.)
    │
    ├── B10\_KararlilikTepkime
    │   ├── 10.1 tepkime, 10.2 kimyasal\_kararlilik, 10.3 zararli\_reaksiyon\_olasiligi,
    │   │   10.4 kacinilmasi\_gereken\_durumlar, 10.5 kacinilmasi\_gereken\_maddeler,
    │   │   10.6 zararli\_bozunma\_urunleri
    │
    ├── B11\_Toksikolojik
    │   └── 11.1: akut\_toksisite, cilt\_asinmasi\_tahrisi, goz\_hasari, solunum\_cilt\_hassasiyeti,
    │         mutajenite, kanserojenite, ureme\_toksisitesi, bhot\_tek\_maruz, bhot\_tekrarli,
    │         aspirasyon\_zarari, maruz\_kalma\_yollari, belirtiler, kronik\_etkiler
    │
    ├── B12\_Ekolojik
    │   └── 12.1 toksisite, 12.2 kalicilik\_bozunabilirlik, 12.3 biyobirikim,
    │         12.4 topraktaki\_hareketlilik, 12.5 pbt\_vpvb\_sonuclari, 12.6 diger\_olumsuz\_etkiler
    │
    ├── B13\_Bertaraf
    │   └── 13.1: atik\_isleme\_yontemleri, ambalaj\_atik\_isleme, kanalizasyon\_uyarisi
    │
    ├── B14\_Tasimacilik
    │   └── 14.1 un\_numarasi, 14.2 un\_tasimacilik\_adi, 14.3 tasimacilik\_sinifi,
    │         14.4 ambalajlama\_grubu, 14.5 cevresel\_zararlar,
    │         14.6 kullanici\_ozel\_onlemler, 14.7 marpol\_ibc?
    │
    ├── B15\_Mevzuat
    │   └── 15.1 ozel\_mevzuat\_hukumleri, 15.2 kimyasal\_guvenlik\_degerlendirmesi\_yapildi\_mi
    │
    └── B16\_DigerBilgiler
        └── revizyon\_aciklamasi, kisaltmalar\_anahtari, literatur\_referanslari,
              degerlendirme\_yontemleri, tam\_h\_ifadeleri (2-15. bölümlerden otomatik toplanır),
              egitim\_tavsiyeleri
```

\---

## 4\. Zorunlu Alan / Doğrulama Kuralları (v1 için özet liste)

|Kural|Kaynak (KKDİK Ek-2)|
|-|-|
|Hiçbir alt bölüm tamamen boş bırakılamaz|md. 0.4|
|3.1 / 3.2 karşılıklı dışlayıcı|md. 0.3.1, 3. Bölüm|
|Yasaklı ifade listesi ('zararsız', 'sağlığa etkisi yok'...) engellenir/uyarılır|md. 0.2.4|
|Hazırlama tarihi ilk sayfada zorunlu|md. 0.2.5|
|Sayfa numaralandırma "sayfa X/toplam" formatı|md. 0.3.2|
|H-kodları kısaltılmışsa 16. Bölüm'de tam metin referansı zorunlu|md. 2.1, 16.d|
|Karışım sınıflandırma kriterlerini karşılamıyorsa bu açıkça belirtilmeli|md. 2.1|

\---

## 5\. Önerilen Teknik Mimari

Mevcut çalışma tarzınla (PolchemColorLAB) tutarlı, Antigravity CLI ile inşa edilebilir bir yığın:

* **Backend:** Python + FastAPI — form verisi Pydantic modelleriyle 16 bölüm şemasını
birebir yansıtır; doğrulama kuralları (Bölüm 4) Pydantic validator'ları olarak yazılır
* **Veri saklama:** Tek kullanıcı/yerel olduğu için SQLite (dosya tabanlı, kurulum
gerektirmez) — ileride çok kullanıcıya geçilirse PostgreSQL'e taşınabilir
* **Frontend:** React — sihirbaz akışı için adım bileşenleri (step components), form state
yönetimi (React Hook Form önerilir), otomatik taslak kaydı (debounced autosave)
* **PDF export:** HTML şablonundan (Jinja2) WeasyPrint ile PDF üretimi — resmî GBF sayfa
düzenini (üst bilgi, sayfa X/Y, 16 bölüm başlıkları) HTML/CSS ile birebir kontrol etmek
kolay
* **DOCX export:** python-docx ile aynı içerik modelinden üretim (PDF şablonuyla ortak veri
kaynağı, iki ayrı render fonksiyonu)
* **AI metin önerisi:** Anthropic API (Claude) — her bölüm için ayrı, KKDİK dil kurallarını
(madde 0.2.4) içeren sistem promptu; kullanıcı girdisini alıp taslak metin döndürür,
kaydetmeden önce kullanıcı onayı şart
* **Kimlik doğrulama:** Yok — yerel tek kullanıcı, opsiyonel olarak ileride basit bir
"workspace kilidi" (parola) eklenebilir ama v1 kapsamı dışında

\---

## 6\. Arayüz Yönü

* **Yapı:** Sihirbaz (adım adım, ilerleme çubuklu, bir sonraki/önceki gezinme) — modern ve
ferah bir deneyim
* **Görsel dil:** Kurumsal ve sade — nötr renk paleti (gri/lacivert tonları + tek bir vurgu
rengi), bol boşluk, mevzuat referanslarının küçük/ikincil tipografiyle (tooltip veya
yardımcı metin) gösterilmesi, süslemeden kaçınma
* Sonuç: "mevzuat odaklı ama sıkıcı olmayan" bir sihirbaz — kullanıcı her adımda ne
yapması gerektiğini net görür, ama arayüz eski usul kurumsal yazılım hissi vermez

\---

## 7\. MVP Yol Haritası (Öneri Fazlar)

1. **Faz 1 — Veri modeli + CRUD:** Ürün kaydı, 16 bölümlük Pydantic şeması, SQLite
entegrasyonu, temel doğrulama kuralları
2. **Faz 2 — Sihirbaz UI:** React tarafında 16 adımlı form akışı, autosave, ilerleme takibi,
zorunlu alan uyarıları
3. **Faz 3 — Export:** PDF (WeasyPrint) ve DOCX (python-docx) üretimi, ortak şablon verisi
4. **Faz 4 — AI metin önerisi:** Bölüm bazlı AI destek akışı, onay/düzenleme arayüzü
5. **Faz 5 (v1 sonrası, kapsam dışı):** Çoklu kullanıcı, revizyon geçmişi/versiyonlama,
toplu ürün import, mevzuat güncellemesi takibi

\---

