# KKDİK Uyumlu SDS / GBF Hazırlayıcısı — Faz 1 Backend

KKDİK Ek-2 ve SEA yönetmeliklerine uygun olarak geliştirilmiş Güvenlik Bilgi Formu (SDS/GBF) hazırlama, doğrulama ve ürün yönetim sistemi backend altyapısı.

## Mimari ve Teknolojiler
* **Framework:** Python + FastAPI
* **Veri Doğrulama & Modelleme:** Pydantic v2 (16 Bölümlük SDS Modeli)
* **Veritabanı (ORM):** SQLite + SQLAlchemy
* **Test Altyapısı:** Pytest + TestClient (23/23 birim ve entegrasyon testi)

---

## Dizin Yapısı

```
backend/
├── app/
│   ├── data/                   # Mevzuat referans veritabanı (JSON)
│   │   ├── h_statements.json   # CLP/KKDİK Türkçe H-ifadeleri
│   │   ├── p_statements.json   # Türkçe P-ifadeleri
│   │   └── pictograms.json     # GHS Tehlike Piktogramları (GHS01-GHS09)
│   ├── models/                 # SQLAlchemy DB modelleri
│   │   └── db_models.py        # Product tablosu ve JSON SDS depolama
│   ├── routers/                # FastAPI endpoint yönlendiricileri
│   │   ├── products.py         # Ürün CRUD, kopyalama, doğrulama, H-kodu toplama
│   │   └── references.py       # H/P/Piktogram referans kütüphanesi
│   ├── schemas/                # Pydantic şemaları
│   │   ├── sds_sections.py     # 16 Bölümlük SDS Ağaç Şeması (B1 - B16)
│   │   ├── product.py          # Ürün CRUD ve listeleme şemaları
│   │   ├── validation.py       # KKDİK doğrulama ve ilerleme şemaları
│   │   └── reference.py        # Referans veri şemaları
│   ├── services/               # İş mantığı ve mevzuat motorları
│   │   ├── product_service.py  # Ürün CRUD, kopyalama ve autosave
│   │   ├── validator_service.py# KKDİK Ek-2 Bölüm 4 doğrulama motoru
│   │   └── reference_service.py# H-kod ayrıştırma ve sözlük servisi
│   ├── config.py               # Yapılandırma ve ortam değişkenleri
│   ├── database.py             # SQLite bağlantı ve Session yönetimi
│   └── main.py                 # FastAPI ana uygulama ve middleware
├── tests/                      # Otomasyon testleri
│   ├── conftest.py             # SQLite bellek içi test fikstürleri
│   ├── test_models.py          # 16 Bölümlük Pydantic modelleri testleri
│   ├── test_validators.py      # KKDİK Ek-2 doğrulama kuralları testleri
│   ├── test_product_crud.py    # CRUD, duplicate ve API entegrasyon testleri
│   └── test_references.py      # Mevzuat kütüphanesi API testleri
├── requirements.txt
└── run.py                      # Backend sunucu başlatıcı
```

---

## 16 Bölümlük SDS Veri Modeli (`sds_sections.py`)

1. **B1: Maddenin / Karışımın ve Şirketin / Dağıtıcının Kimliği** (1.1, 1.2, 1.3, 1.4)
2. **B2: Zararlılık Tanımlanması** (2.1 Sınıflandırma, 2.2 Etiket Unsurları, 2.3 Diğer Zararlar)
3. **B3: Bileşimi / İçindekiler Hakkında Bilgi** (3.1 Madde XOR 3.2 Karışım)
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

## Bölüm 4 Doğrulama Kuralları (Mevzuat Motoru)

| Kural | KKDİK Referansı | Açıklama |
|---|---|---|
| **Boş Alan Yasağı** | md. 0.4 | Zorunlu alt bölümler sessizce boş bırakılamaz. Gerekçelendirme ('N/A — gerekçesi: ...' veya 'Bilgi yok') gereklidir. |
| **XOR Kuralı** | md. 0.3.1, 3. Bölüm | 3. Bölüm'de yalnızca 3.1 (madde) veya 3.2 (karışım) yer alabilir; ikisi birden tanımlanamaz. |
| **Yasaklı İfadeler** | md. 0.2.4 | 'zararsız', 'sağlığa etkisi yok', 'çoğu kullanım koşullarında güvenli', 'toksik değil', 'çevre dostu' vb. tespit edildiğinde uyarılır. |
| **Hazırlama Tarihi** | md. 0.2.5 | SDS ilk sayfasında hazırlanma tarihi zorunludur. |
| **H-Kodu Tam Metin Referansı** | md. 2.1, 16.d | Formda (B2, B3) geçen tüm H-kodlarının Bölüm 16'da açık Türkçe metin karşılığı bulunmalıdır. |
| **Sınıflandırılmamış Karışım** | md. 2.1 | Ürün sınıflandırılmamışsa buna ilişkin açık mevzuat gerekçesi zorunludur. |

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
* `POST /api/products/{id}/auto-fill-h-codes`: H-kodlarını toplayıp Bölüm 16'ya yazma
* `POST /api/products/validate-raw`: Ham SDS JSON'ını kaydetmeden anlık doğrulama

### Mevzuat Kütüphanesi
* `GET /api/references/h-statements`: Tüm H-kodları veya kategori/arama filtresi
* `GET /api/references/h-statements/{code}`: Belirli bir H-kodu açıklaması
* `GET /api/references/p-statements`: Tüm P-kodları veya tip/arama filtresi
* `GET /api/references/p-statements/{code}`: Belirli bir P-kodu açıklaması
* `GET /api/references/pictograms`: GHS01-GHS09 Piktogram listesi
* `GET /api/references/pictograms/{code}`: Belirli bir piktogram detayı

---

## Çalıştırma ve Test

### Sunucuyu Başlatma
```powershell
cd backend
python run.py
```
* API Dokümantasyonu (Swagger): `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`

### Testleri Çalıştırma
```powershell
$env:PYTHONPATH="backend"
python -m pytest backend/tests -v
```
