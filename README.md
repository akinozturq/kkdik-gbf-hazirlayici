# KKDİK Uyumlu Güvenlik Bilgi Formu (SDS / GBF) Hazırlayıcı 🚀

T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı **KKDİK Yönetmeliği (Ek-2)** ve **SEA Yönetmeliği (Ek-1 & Ek-4)** standartlarına tam uyumlu, 16 bölümlük Güvenlik Bilgi Formu (SDS) yönetim, otomatik karışım zararlılık hesaplama, doğrulama ve PDF/Word dışa aktarma sistemi.

---

## 🌟 Öne Çıkan Özellikler

1. **16 Bölümlük Eksiksiz Veri Modeli & Doğrulama Motoru:**
   * KKDİK Ek-2 ve SEA standartlarında tip güvenli Pydantic v2 şeması.
   * Canlı kural denetimi: 0.4 Zorunlu alt bölümler, 3.1 XOR 3.2 kuralı, 0.2.4 Yasaklı ifadeler filtresi, Bölüm 16 çapraz referans kontrolü.
   * Bölüm bazlı ve genel mevzuata uygunluk ilerleme skoru.

2. **SEA Ek-1 Karışım Zararlılık Hesaplama Motoru:**
   * Bölüm 3.2 Karışım tablosuna girilen bileşen konsantrasyonlarından yola çıkarak Bölüm 2'yi otomatik hesaplar.
   * Cilt aşınması/tahrişi, ciddi göz hasarı/tahrişi, aspirasyon toksisitesi, STOT SE/RE, izosiyanat/solunum hassaslaşması ve sucul kronik toplanabilirlik formülleri.
   * GHS Piktogram ve Uyarı Kelimesi öncelik kuralları (SEA Madde 26 & 28).
   * Şeffaf matematiksel hesaplama adımları raporu.

3. **SEA Ek-4 H ➔ P Önlem İfadeleri Haritalama:**
   * Hesaplanan H-kodlarına karşılık gelen tüm geçerli P-kodlarını (Önleme, Müdahale, Depolama, Bertaraf) otomatik türetir.
   * SEA Madde 30(1) uyarınca mükerrer/çelişen ifadeleri akıllıca ayıklar.

4. **Sektörel Hazır GBF Şablonları (Presets):**
   * *Tiner & Solventler*, *Poliüretan Sertleştiriciler (İzosiyanat)*, *Solventli Boyalar* ve *Su Bazlı Sistemler* için 4, 5, 6, 7, 8, 10 ve 13. bölümleri tek tıkla otomatik doldurma.

5. **Kurumsal Dışa Aktarma Motoru (PDF & Word .docx):**
   * Google Sans tipografisi (12pt ana, 11pt alt başlık, 10pt gövde metni).
   * Resmî GHS piktogram görselleri (GHS01 - GHS09).
   * Renkli/mavi dolgusuz, yalın ve kurumsal antetli belge tasarımı.
   * KKDİK Ek-2 Bölüm B uyarınca 1.1'den 16.5'e kadar tüm alt başlıkların eksiksiz ve ayrı yapısı.

---

## 🚀 Proje Mimarisi

```
├── backend/                       # FastAPI Backend Servisi
│   ├── app/
│   │   ├── data/                 # H/P İfadeleri, H->P Haritası & GHS Piktogramları
│   │   ├── models/               # SQLAlchemy DB Modelleri (SQLite)
│   │   ├── routers/              # /api/products, /api/references Endpoint'leri
│   │   ├── schemas/              # 16 Bölümlük KKDİK Pydantic v2 Veri Modelleri
│   │   ├── services/             # ClassificationEngine, ProductService, ValidatorService, ExportServices
│   │   └── templates/            # Antetli GBF Şablonu, Fonts & Piktogramlar
│   └── tests/                    # 34 Adet Otomatize Pytest Test Paketi
│
├── frontend/                      # React 19 + Vite Frontend Sihirbazı
│   ├── src/
│   │   ├── api/                  # Backend REST API İstemcisi
│   │   ├── context/              # AppContext (Autosave & State Management)
│   │   ├── components/
│   │   │   ├── Header.jsx        # Üst Navigasyon, Autosave Durumu, Sektörel Şablon
│   │   │   ├── ProductList/      # Ürün Havuzu, Arama/Filtreleme, Kopyalama, Silme
│   │   │   ├── Wizard/           # 16 Bölümlük Form Sihirbazı, Hesaplama & Şablon Modalları
│   │   │   └── Common/           # KKDİK Canlı Doğrulama Çekmecesi & H/P Seçici Modal
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
*(34 passed in ~2.5s)*
