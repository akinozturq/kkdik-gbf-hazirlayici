# KKDİK Uyumlu SDS / GBF Hazırlayıcısı — Backend Servisi

KKDİK Ek-2, SEA yönetmelikleri ve REACH Annex II standartlarına uygun olarak geliştirilmiş Güvenlik Bilgi Formu (SDS/GBF) hazırlama, otomatik karışım zararlılık hesaplama, yapay zekâ çeviri ve ürün yönetim sistemi backend altyapısı.

## Mimari ve Teknolojiler
* **Framework:** Python + FastAPI
* **Veri Doğrulama & Modelleme:** Pydantic v2 (16 Bölümlük SDS Modeli)
* **Veritabanı (ORM):** SQLite + SQLAlchemy
* **Yapay Zekâ:** Google Gemini (1.5 Flash / 2.5 Flash Lite) + Deterministik Sözlük Hibrit Çeviri Motoru
* **Dışa Aktarma:** `python-docx` (Word), `xhtml2pdf` / `reportlab` (PDF), Jinja2 (HTML Önizleme)
* **Test Altyapısı:** Pytest + TestClient (57/57 birim ve entegrasyon testi)

---

## Dizin Yapısı

```
backend/
├── app/
│   ├── data/                   # Mevzuat referans veritabanı (JSON)
│   │   ├── h_statements.json   # CLP/KKDİK Türkçe H-ifadeleri
│   │   ├── p_statements.json   # Türkçe P-ifadeleri
│   │   ├── pictograms.json     # GHS Tehlike Piktogramları (GHS01-GHS09)
│   │   ├── h_to_p_map.json     # SEA Ek-4 H -> P haritalama kuralları
│   │   └── raw_materials.json  # Standart hammadde kütüphanesi (ATE & M-Faktörlü)
│   ├── models/                 # SQLAlchemy DB modelleri
│   │   └── db_models.py        # Product ve Category tabloları
│   ├── routers/                # FastAPI endpoint yönlendiricileri
│   │   ├── products.py         # Ürün CRUD, kopyalama, doğrulama, hesaplama, ihracat
│   │   ├── references.py       # H/P/Piktogram/Hammadde referans kütüphanesi
│   │   └── ai.py               # Gemini AI yapılandırma ve çeviri endpoint'leri
│   ├── schemas/                # Pydantic şemaları
│   │   ├── sds_sections.py     # 16 Bölümlük SDS Ağaç Şeması (B1 - B16)
│   │   ├── product.py          # Ürün CRUD ve listeleme şemaları
│   │   ├── validation.py       # KKDİK doğrulama ve ilerleme şemaları
│   │   ├── reference.py        # Referans veri şemaları
│   │   └── ai.py               # AI ayar ve çeviri şemaları
│   ├── services/               # İş mantığı ve mevzuat motorları
│   │   ├── classification_engine.py # SEA Ek-1 Karışım Hesaplama, ATE_mix & M-faktörü
│   │   ├── product_service.py  # Ürün CRUD, kopyalama ve autosave
│   │   ├── validator_service.py# KKDİK Ek-2 Bölüm 4 doğrulama motoru
│   │   ├── reference_service.py# H-kod ayrıştırma ve sözlük servisi
│   │   ├── docx_export_service.py # Word (.docx) ihracat motoru (TR & EN)
│   │   ├── pdf_export_service.py  # PDF ihracat motoru (TR & EN)
│   │   ├── translation_service.py # Deterministik derin çeviri motoru
│   │   └── gemini_service.py   # Google Gemini AI entegrasyonu
│   ├── templates/              # Antetli GBF Şablonu, Fontlar & Piktogramlar
│   ├── config.py               # Yapılandırma ve ortam değişkenleri
│   ├── database.py             # SQLite bağlantı ve Session yönetimi
│   └── main.py                 # FastAPI ana uygulama ve middleware
├── tests/                      # 57 Adet Otomasyon Testi
│   ├── conftest.py             # SQLite bellek içi test fikstürleri
│   ├── test_models.py          # 16 Bölümlük Pydantic modelleri testleri
│   ├── test_validators.py      # KKDİK Ek-2 doğrulama kuralları testleri
│   ├── test_product_crud.py    # CRUD, duplicate ve API entegrasyon testleri
│   ├── test_references.py      # Mevzuat kütüphanesi API testleri
│   ├── test_classification_engine.py # Karışım hesaplama, ATE_mix & M-faktör testleri
│   ├── test_exports.py         # Word, PDF & HTML ihracat testleri
│   ├── test_translation_deep.py# Deterministik çeviri motoru testleri
│   └── test_ai.py              # AI konfigürasyon testleri
├── requirements.txt
└── run.py                      # Backend sunucu başlatıcı
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
python run.py
```
* API Dokümantasyonu (Swagger): `http://127.0.0.1:8000/docs`

### Testleri Çalıştırma
```powershell
$env:PYTHONPATH="backend"
python -m pytest backend/tests -v
```
*(57 passed in ~5.4s)*

