# KKDİK Uyumlu SDS / GBF Hazırlayıcısı — Backend Servisi

KKDİK Ek-2, SEA yönetmelikleri (Ek-1 & Ek-4), CLP (EC 1272/2008) ve REACH Annex II standartlarına tam uyumlu olarak geliştirilmiş Güvenlik Bilgi Formu (SDS/GBF) hazırlama, otomatik karışım zararlılık hesaplama, veri kalitesi & belirsizlik analizi, yapay zekâ destekli çeviri, ADR taşımacılık ve ürün yönetim sistemi backend altyapısı.

## Mimari ve Teknolojiler
* **Framework:** Python 3.12 + FastAPI
* **Veri Doğrulama & Modelleme:** Pydantic v2 (16 Bölümlük SDS Şeması ve Tip-Güvenli Regülatif Modeller)
* **Veritabanı (ORM):** SQLite + SQLAlchemy
* **Yapay Zekâ:** Google Gemini (1.5 Flash / 2.5 Flash Lite) + Deterministik Sözlük Hibrit Çeviri Motoru
* **Dışa Aktarma:** `python-docx` (Word), `xhtml2pdf` / `reportlab` (Lazy-load PDF), Jinja2 (HTML Önizleme)
* **Taşımacılık Motoru:** ADR Sınıfı, PG, UN Numarası ve Tünel Kodları (`transport_engine.py`)
* **Test Altyapısı:** Pytest (144 otomatize test, %100 başarılı)

---

## 🏗️ Regülasyon Motoru Mimarisi (Regulatory Pipeline v2)

Backend sınıflandırma motoru; **Pipeline Pattern** ve **Strategy Pattern** prensipleriyle tasarlanmış çok aşamalı bir yapıya sahiptir:

1. **Input Katmanı:** Ham bileşenler, konsantrasyonlar ve fiziksel test parametreleri (Parlama Noktası, Kinematik Viskozite, pH, Fiziksel Hal).
2. **Normalization (`RegulatoryParser`):** Ham metinleri kanonik CLP/SEA tehlike sınıflarına, H-kodlarına, SCL değerlerine ve M-faktörlerine dönüştürür.
3. **Data Quality (`DataQualityAssessor`):**
   * Konsantrasyon belirsizliklerini (`range`, `less_than`, `greater_than`) tespit eder ve `UNCERTAIN` kalitesine atar.
   * Reçetedeki toplam konsantrasyon kontrolünü yapar: $\Sigma_{min} > 100\%$ ise `ERROR` / `CONTRADICTORY`, $\Sigma_{max} > 100\%$ ise `WARNING` / `UNCERTAIN`.
   * Eksik fiziksel test gereksinimlerini (örn. alevlenir sıvılarda parlama noktası eksikliği) denetler (`INSUFFICIENT_DATA`).
4. **Rule Strategies (`app/services/rules/`):**
   * `FlammableLiquidRule`: Parlama ve kaynama noktası eşikleri.
   * `SkinEyeRule`: Cilt aşınması 1A/1B/1C, tahriş (Kat 2) ve göz hasarı/tahrişi toplanabilirlik kuralları ve SCL entegrasyonu.
   * `AspirationHazardRule`: Viskozite ($\le 20.5\text{ mm}^2/\text{s}$) ve konsantrasyon ($\ge 10\%$) eşleşmesi.
   * `AcuteToxicityRule`: ATE_mix harmonik formülü ve Tablo 3.1.2 dönüşüm değerleri.
   * `AquaticRule`: Akut/Kronik toplanabilirlik ve M-faktörü çarpanları.
   * `CMRRule` & `STOTRule`: Kanserojenlik, mutajenlik, üreme toksisitesi ve hedef organ toksisitesi eşikleri.
   * `SupplementalHazardRule`: EUH066, EUH204, EUH208 tamamlayıcı zararlılıklar.
5. **Evidence & Dual Projection:** Aralık içeren bileşenler için hem minimum hem maksimum değerler simüle edilerek kesin durumlar (`DEFINITELY_TRUE`, `DEFINITELY_FALSE`) ile aralık eşiği durumları (`INDETERMINATE`) ayrıştırılır.
6. **Precedence (`PictogramPrecedenceMatrix`):** `pictogram_precedence_matrix.json` tablosu üzerinden SEA Madde 26 / CLP Art. 26 bildirimsel kuralları çalıştırılarak piktogramlar elenir (GHS06 > GHS07, GHS05 > GHS07 vb.) ve denetim kaydı oluşturulur.
7. **Label Generator (`LabelGenerator`):** SEA Ek-4 uyarınca P-kodları türetilir ve hiyerarşik fazlalıklar ayıklanır.

---

## Dizin Yapısı

```
backend/
├── app/
│   ├── data/
│   │   ├── h_statements.json               # CLP/KKDİK Türkçe H-ifadeleri
│   │   ├── p_statements.json               # Türkçe P-ifadeleri
│   │   ├── pictograms.json                 # GHS Tehlike Piktogramları (GHS01-GHS09)
│   │   ├── h_to_p_map.json                 # SEA Ek-4 H -> P haritalama kuralları
│   │   ├── raw_materials.json              # Standart hammadde kütüphanesi (ATE & M-Faktörlü)
│   │   ├── pictogram_precedence_matrix.json# SEA Md. 26 Piktogram Öncelik Matrisi
│   │   ├── regulatory_test_matrix.csv      # Resmî Regülasyon Test Matrisi (CSV)
│   │   └── regulatory_test_matrix.json     # Resmî Regülasyon Test Matrisi (JSON)
│   ├── models/
│   │   ├── db_models.py                    # Product ve Category SQLAlchemy modelleri
│   │   └── regulatory.py                   # StructuredSubstance, DataQuality, ATE modelleri
│   ├── routers/
│   │   ├── products.py                     # Ürün CRUD, kopyalama, doğrulama, hesaplama, ihracat
│   │   ├── references.py                   # H/P/Piktogram/Hammadde referans kütüphanesi
│   │   └── ai.py                           # Gemini AI yapılandırma ve çeviri endpoint'leri
│   ├── schemas/                            # Pydantic şemaları
│   │   ├── sds_sections.py                 # 16 Bölümlük SDS Ağaç Şeması (B1 - B16)
│   │   ├── product.py                      # Ürün CRUD ve listeleme şemaları
│   │   ├── validation.py                   # KKDİK doğrulama ve ilerleme şemaları
│   │   ├── reference.py                    # Referans veri şemaları
│   │   └── ai.py                           # AI ayar ve çeviri şemaları
│   ├── services/                           # İş mantığı ve mevzuat motorları
│   │   ├── regulatory_engine/              # Pipeline, DataQuality, Parser, Precedence, Label
│   │   ├── rules/                          # Kural Stratejileri (Flammable, Skin, Eye, CMR, STOT, Aquatic, Acute)
│   │   ├── classification_engine.py        # Motor cephesi (Facade)
│   │   ├── transport_engine.py             # ADR Taşımacılık Sınıflandırma Motoru
│   │   ├── product_service.py              # Ürün CRUD, kopyalama ve autosave
│   │   ├── validator_service.py            # KKDİK Ek-2 Bölüm 4 doğrulama motoru
│   │   ├── reference_service.py            # H-kod ayrıştırma ve sözlük servisi
│   │   ├── docx_export_service.py          # Word (.docx) ihracat motoru (TR & EN)
│   │   ├── pdf_export_service.py           # PDF ihracat motoru (Lazy import korumalı)
│   │   ├── translation_service.py          # Deterministik derin çeviri motoru
│   │   └── gemini_service.py               # Google Gemini AI entegrasyonu
│   ├── templates/                          # Antetli GBF Şablonu, Fontlar & Piktogramlar
│   ├── config.py                           # Yapılandırma ve ortam değişkenleri
│   ├── database.py                         # SQLite bağlantı ve Session yönetimi
│   └── main.py                             # FastAPI ana uygulama ve middleware
├── tests/                                  # 139 Adet Otomasyon Testi
│   ├── test_regulatory_test_matrix.py      # 28 adet SEA/CLP benchmark testi
│   ├── test_classification_engine.py       # ATE_mix, M-faktör, toplanabilirlik testleri
│   ├── test_validators.py                  # KKDİK Ek-2 doğrulama kuralları testleri
│   ├── test_models.py                      # 16 Bölümlük Pydantic modelleri testleri
│   ├── test_product_crud.py                # CRUD, duplicate ve API entegrasyon testleri
│   ├── test_references.py                  # Mevzuat kütüphanesi API testleri
│   ├── test_exports.py                     # Word, PDF & HTML ihracat testleri
│   ├── test_translation_deep.py            # Deterministik çeviri motoru testleri
│   └── test_ai.py                          # AI konfigürasyon testleri
├── requirements.txt
└── run.py                                  # Backend sunucu başlatıcı
```

---

## 16 Bölümlük SDS Veri Modeli (`sds_sections.py`)

1. **B1: Maddenin / Karışımın ve Şirketin / Dağıtıcının Kimliği** (1.1, 1.2, 1.3, 1.4)
2. **B2: Zararlılık Tanımlanması** (2.1 Sınıflandırma, 2.2 Etiket Unsurları, 2.3 Diğer Zararlar)
3. **B3: Bileşimi / İçindekiler Hakkında Bilgi** (3.1 Madde XOR 3.2 Karışım, ATE & M-faktör alanları)
4. **B4: İlk Yardım Önlemleri** (4.1 Soluma/Cilt/Göz/Yutma, 4.2 Belirtiler, 4.3 Tıbbi Müdahale)
5. **B5: Yangınla Mücadele Önlemleri** (5.1 Söndürücüler, 5.2 Özel Zararlar, 5.3 Ekip Tavsiyeleri)
6. **B6: Kaza Sonucu Yayılmaya Karşı Önlemler** (6.1 Kişisel, 6.2 Çevresel, 6.3 Temizleme, 6.4 Atıf)
7. **B7: Elleçleme ve Depolama** (7.1 Elleçleme, 7.2 Depolama & Uyumsuzluklar, 7.3 Son Kullanımlar)
8. **B8: Maruz Kalma Kontrolleri / Kişisel Korunma** (8.1 Limitler, 8.2 KKD & Havalandırma)
9. **B9: Fiziksel ve Kimyasal Özellikler** (9.1 20 temel özellik, 9.2 Diğer bilgiler)
10. **B10: Kararlılık ve Tepkime** (10.1 - 10.6)
11. **B11: Toksikolojik Bilgiler** (11.1 Akut, Tahriş, CMR, BHOT vb.)
12. **B12: Ekolojik Bilgiler** (12.1 Ekotoksisite, 12.2 Kalıcılık, 12.3 Biyobirikim vb.)
13. **B13: Bertaraf Etme Bilgileri** (13.1 Atık ve ambalaj işleme, kanalizasyon uyarısı)
14. **B14: Taşımacılık Bilgisi** (14.1 UN No, 14.2 UN Adı, 14.3 Sınıf, 14.4 PG vb.)
15. **B15: Mevzuat Bilgisi** (15.1 Mevzuat hükümleri, 15.2 Kimyasal güvenlik değerlendirmesi)
16. **B16: Diğer Bilgiler** (Revizyon açıklaması, kısaltmalar, literatür, tam H-ifadeleri)

---

## API Uç Noktaları

### Ürün & SDS İşlemleri
* `POST /api/products`: Yeni ürün ve SDS taslağı oluşturma
* `GET /api/products`: Ürün listeleme (arama, kategori filtresi, tamamlama skoru, sayfalama)
* `GET /api/products/{id}`: Ürün detayı ve 16 bölümlük SDS verisi
* `PUT /api/products/{id}`: Ürün ve SDS güncelleme (Autosave uyumlu derin birleştirme)
* `DELETE /api/products/{id}`: Ürün silme
* `POST /api/products/{id}/duplicate`: Var olan ürünü kopyalayarak yeni ürün oluşturma
* `GET /api/products/{id}/validate`: Ürün SDS'ini KKDİK Ek-2 kurallarına göre doğrulama
* `POST /api/products/{id}/calculate-hazards`: Bölüm 3.2'den Bölüm 2 zararlılıklarını hesaplama (ATE_mix, M-faktör dahil)
* `POST /api/products/{id}/apply-calculated-hazards`: Hesaplanan zararlılıkları Bölüm 2'ye yazma
* `GET /api/products/{id}/export-docx`: Türkçe Word (.docx) belgesi indirme
* `GET /api/products/{id}/export-pdf`: Türkçe PDF belgesi indirme
* `GET /api/products/{id}/export-english-docx`: REACH Annex II İngilizce Word (.docx) indirme
* `GET /api/products/{id}/export-english-pdf`: REACH Annex II İngilizce PDF indirme
* `GET /api/products/{id}/preview-html`: Anlık HTML şablon önizleme

### Mevzuat & Hammadde Kütüphanesi
* `GET /api/references/h-statements`: Tüm H-kodları veya kategori/arama filtresi
* `GET /api/references/p-statements`: Tüm P-kodları veya tip/arama filtresi
* `GET /api/references/pictograms`: GHS01-GHS09 Piktogram listesi
* `GET /api/references/raw-materials`: Hammadde kütüphanesi arama ve listeleme

### Yapay Zekâ (Gemini AI)
* `GET /api/ai/config`: Gemini AI durum ve model bilgisi
* `POST /api/ai/config`: API anahtarı ve model yapılandırması
* `POST /api/ai/translate`: Belirli metin veya SDS bölümlerini İngilizceye çevirme

---

## Çalıştırma ve Test

### Sunucuyu Başlatma
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
* API Dokümantasyonu (Swagger): `http://127.0.0.1:8000/docs`

### Testleri Çalıştırma
```powershell
python -m pytest backend/tests -v --tb=short
```
*(144 passed in ~6.7s)*

