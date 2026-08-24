# KKDİK Uyumlu Güvenlik Bilgi Formu (SDS / GBF) Hazırlayıcı 🚀

T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı **KKDİK Yönetmeliği (Ek-2)** ve **SEA Yönetmeliği (Ek-1 & Ek-4)** ile Avrupa Birliği **REACH (Annex II)** standartlarına tam uyumlu, 16 bölümlük Güvenlik Bilgi Formu (SDS) yönetim, otomatik karışım zararlılık hesaplama, yapay zekâ destekli İngilizce çeviri, kural denetimi ve kurumsal PDF/Word dışa aktarma sistemi.

---

## 🌟 Öne Çıkan Özellikler

1. **16 Bölümlük Eksiksiz Veri Modeli & Doğrulama Motoru:**
   * KKDİK Ek-2 ve SEA standartlarında tip güvenli Pydantic v2 şeması.
   * Canlı kural denetimi: 0.4 Zorunlu alt bölümler, 3.1 XOR 3.2 kuralı, 0.2.4 Yasaklı ifadeler filtresi, Bölüm 16 çapraz referans kontrolü.
   * Bölüm bazlı ve genel mevzuata uygunluk ilerleme skoru.

2. **SEA Ek-1 Gelişmiş Karışım Zararlılık Hesaplama Motoru:**
   * **Akut Toksisite (ATE_mix):** SEA Ek-1 Bölüm 3.1.3.6 harmonik formülü `100/ATE_mix = Σ(Ci/ATEi)` (Oral, Dermal ve Soluma maruziyet yolları; Buhar mg/L, Gaz ppmV, Toz/Sis mg/L ayrımı ve SEA Ek-1 Tablo 3.1.2 dönüşüm değerleri fallback desteği).
   * **Sucul Çevre Zararları & M-Faktörü:** Akut Kategori 1 (H400) ve Kronik 1-4 (H410-H413) toplanabilirlik formülleri; Akut ve Kronik M-faktörü (`M x C`) çarpan desteği.
   * **Fiziksel & Sağlık Zararları:** Alevlenir sıvılar (ölçülmüş parlama noktası zorunluluğu), Cilt Aşınması 1A/1B/1C ayrımı, ciddi göz hasarı/tahrişi, aspirasyon toksisitesi, STOT SE/RE, izosiyanat/solunum hassaslaşması (EUH204), CMR 1A/1B ve EUH066 kuralları.
   * **GHS Piktogram ve Uyarı Kelimesi Öncelik Kuralları:** SEA Madde 26 & 28 (GHS06 vs GHS07, GHS05 vs GHS07, GHS08 vs GHS07 eleme mantığı).
   * **Semantik Çapraz Doğrulama (Semantic Cross-Validation):** Bölüm 2 ile Bölüm 9 (parlama noktası, kinematik viskozite), Bölüm 12 (ekotoksisite) ve Bölüm 14 (UN No) arasındaki mantıksal tutarlılık denetimi.
   * **Şeffaf Matematiksel Hesaplama Raporu:** Her adımın formül ve ara değerlerini gösteren detaylı denetim raporu.

3. **Hammadde Kütüphanesi & Reçete Entegrasyonu:**
   * Standart endüstriyel kimyasallar (Aseton, Toluen vb.) için CAS, EC, molekül bilgileri, SEA sınıflandırması, fiziksel parametreler, ATE ve M-faktörü değerlerini içeren kütüphane.
   * Bölüm 3.2 formuna tek tıkla otomatik bileşen aktarımı.

4. **REACH Annex II İngilizce SDS & AI Destekli Hibrit Çeviri:**
   * Deterministik mevzuat sözlüğü ve **Google Gemini AI** hibrit altyapısıyla Türkçe GBF'den uluslararası standartta 16 bölümlük İngilizce SDS üretimi.
   * İngilizce PDF, Word (.docx) ve anlık HTML önizleme desteği.

5. **SEA Ek-4 H ➔ P Önlem İfadeleri Haritalama:**
   * Hesaplanan H-kodlarına karşılık gelen tüm geçerli P-kodlarını (Önleme, Müdahale, Depolama, Bertaraf) otomatik türetir.
   * SEA Madde 30(1) uyarınca mükerrer ve hiyerarşik çelişen ifadeleri akıllıca ayıklar.

6. **Sektörel Hazır GBF Şablonları (Presets):**
   * *Tiner & Solventler*, *Poliüretan Sertleştiriciler (İzosiyanat)*, *Solventli Boyalar* ve *Su Bazlı Sistemler* için ilgili bölümleri tek tıkla otomatik doldurma.

7. **Kurumsal Dışa Aktarma Motoru (PDF, Word .docx & HTML Önizleme):**
   * Google Sans tipografisi, vektörel resmî GHS piktogramları (GHS01 - GHS09).
   * Renkli/mavi dolgusuz, yalın ve kurumsal antetli belge tasarımı.
   * KKDİK Ek-2 Bölüm B uyarınca 1.1'den 16.5'e kadar tüm alt başlıkların eksiksiz ve ayrı yapısı.

---

## 🚀 Proje Mimarisi

```
├── backend/                       # FastAPI Backend Servisi
│   ├── app/
│   │   ├── data/                 # H/P İfadeleri, H->P Haritası, Hammadde Kütüphanesi & Piktogramlar
│   │   ├── models/               # SQLAlchemy DB Modelleri (SQLite)
│   │   ├── routers/              # /api/products, /api/references, /api/ai Endpoint'leri
│   │   ├── schemas/              # 16 Bölümlük KKDİK Pydantic v2 Veri Modelleri
│   │   ├── services/             # ClassificationEngine, ProductService, ValidatorService, ExportServices, AI/Translation
│   │   └── templates/            # Antetli GBF Şablonu, Fonts & Piktogramlar
│   └── tests/                    # 65 Adet Kapsamlı Otomatize Pytest Test Paketi
│
├── frontend/                      # React 19 + Vite Frontend Sihirbazı
│   ├── src/
│   │   ├── api/                  # Backend REST API İstemcisi
│   │   ├── context/              # AppContext (Autosave & Global State)
│   │   ├── components/
│   │   │   ├── Header.jsx        # Üst Navigasyon, Autosave, Sektörel Şablon, AI Çeviri Seçici
│   │   │   ├── ProductList/      # Ürün Havuzu, Arama/Filtreleme, Kopyalama, Dışa Aktarma
│   │   │   ├── Wizard/           # 16 Bölümlük Form Sihirbazı, ATE & M-Faktör Girişleri, Hesaplama Modalı
│   │   │   └── Common/           # KKDİK Canlı Doğrulama Çekmecesi, Hammadde Seçici & H/P Modalları
│   │   └── index.css             # Kurumsal Modern Tasarım Sistemi
```

---

## 🛠️ Çalıştırma Talimatları

### 1. Backend Servisini Başlatma (FastAPI)
```powershell
# Terminal 1:
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
* Backend API: `http://127.0.0.1:8000`
* Swagger API Dokümantasyonu: `http://127.0.0.1:8000/docs`

### 2. Frontend Uygulamasını Başlatma (React + Vite)
```powershell
# Terminal 2:
cd frontend
npm run dev
```
* Web Uygulaması: `http://localhost:5173`

---

## 🧪 Testleri Çalıştırma
```powershell
$env:PYTHONPATH="backend"
python -m pytest backend/tests -v
```
*(57 passed in ~5.4s)*

