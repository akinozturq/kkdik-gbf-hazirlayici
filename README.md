# KKDİK & SEA Uyumlu Güvenlik Bilgi Formu (SDS / GBF) Hazırlayıcı 🚀

T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı **KKDİK Yönetmeliği (Ek-2)**, **SEA Yönetmeliği (Ek-1 & Ek-4)** ve Avrupa Birliği **CLP (EC 1272/2008) / REACH (Annex II)** standartlarına tam uyumlu; 16 bölümlük Güvenlik Bilgi Formu (SDS) yönetim, otomatik karışım zararlılık hesaplama, veri kalitesi & belirsizlik analizi, yapay zekâ destekli İngilizce çeviri, kural denetimi ve kurumsal PDF/Word dışa aktarma sistemi.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.10+-e92063.svg)](https://docs.pydantic.dev/)
[![React](https://img.shields.io/badge/React-19.0-61dafb.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/Tests-144%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/Mevzuat-KKD%C4%B0K%20%2F%20SEA%20%2F%20CLP-orange.svg)]()

---

## 🏗️ Regülasyon Motoru Mimarisi (Regulatory Engine v2)

Sistem; ham kimyasal verilerini basit bir kuraldan geçirmek yerine, endüstriyel standartlarda **Strategy** ve **Pipeline** tasarım kalıplarına dayalı çok aşamalı bir regülasyon motoru işletir:

```
┌─────────────────┐
│     INPUT       │  Reçete bileşenleri, konsantrasyonlar, fiziksel test verileri (FP, Viskozite, pH)
└────────┬────────┘
         ▼
┌─────────────────┐
│  NORMALIZATION  │  RegulatoryParser: Kanonik CLP/SEA sınıfları, H-kodları, SCL, M-faktörleri, ATE
└────────┬────────┘
         ▼
┌─────────────────┐
│  DATA QUALITY   │  DataQualityAssessor: Belirsizlik analizi (range/min/max), eksik veri tespiti,
└────────┬────────┘  toplam konsantrasyon kontrolü (ΣC > 100%), fiziksel test gereksinimleri
         ▼
┌─────────────────┐
│ RULE STRATEGIES │  Bağımsız Tehlike Kural Stratejileri (Aspiration, Flammable, Skin/Eye, CMR,
└────────┬────────┘  STOT, Aquatic, Supplemental, Acute Toxicity - ATE_mix)
         ▼
┌─────────────────┐
│EVIDENCE & DUAL  │  Çift yönlü (Min / Max) projeksiyon simülasyonu: Kesin Zararlılık (DEFINITELY_TRUE),
│   PROJECTION    │  Kesin Yok (DEFINITELY_FALSE), Aralık Eşiği / Belirsiz (INDETERMINATE)
└────────┬────────┘
         ▼
┌─────────────────┐
│   PRECEDENCE    │  PictogramPrecedenceMatrix (SEA Madde 26 / CLP Art. 26 bildirimsel matrisi):
│   & DECISION    │  GHS06 > GHS07, GHS05 > GHS07, GHS08 > GHS07, GHS01 > GHS02/GHS03 eleme kuralları
└────────┬────────┘
         ▼
┌─────────────────┐
│ LABEL GENERATOR │  SEA Ek-4 H ➔ P önlem ifadeleri türetimi, hiyerarşik ayıklama ve uyarı kelimesi
└────────┬────────┘
         ▼
┌─────────────────┐
│   SDS EXPORT    │  16 Bölümlük Türkçe/İngilizce Kurumsal PDF, Word (.docx) ve ADR Taşımacılık
└─────────────────┘
```

---

## 🌟 Temel Yetenekler ve Yenilikler

### 1. Veri Kalitesi, Belirsizlik & Domain Doğrulama (Data Quality Layer)
* **Nitelikli Konsantrasyon Modeli:** Bileşen konsantrasyonları `exact`, `range`, `less_than` ve `greater_than` niteleyicileriyle tip-güvenli işlenir.
* **Aralık Eşiği (Indeterminate Status):** Formülasyonda konsantrasyon aralığı verildiğinde (örn. %5 - %15), motor hem minimum hem maksimum değerleri projeksiyonla simüle eder; eşiği aşan durumları `INDETERMINATE` (Aralık Eşiği / Belirsiz) olarak raporlar.
* **Toplam Konsantrasyon ($\Sigma C$) Denetimi:**
  * Reçetedeki bileşenlerin toplam konsantrasyonu %100'ü aştığında ($\Sigma_{min} > 100\%$) `ERROR` ve `CONTRADICTORY` seviyesinde veri kalitesi hatası üretilir.
  * Aralıkların üst sınır toplamı %100'ü aştığında ($\Sigma_{max} > 100\%$) kullanıcıya `WARNING` ve `UNCERTAIN` uyarısı verilir.
* **Fiziksel Test Eksikliği Tespiti:** Alevlenir sıvılar için parlama noktası, aspirasyon için 40°C kinematik viskozitesi veya aşındırıcılar için pH eksik olduğunda `INSUFFICIENT_DATA` / `INCOMPLETE` durumu atanarak güvenilirlik skoru düşürülür ve denetim izine eklenir.
* **Sıkı Domain Kısıtlamaları:** `0 <= Konsantrasyon <= 100`, `SCL > 0`, `M-Faktörü >= 1`, `ATE > 0`, `Viskozite > 0` gibi fiziksel sınır kontrolleri Pydantic seviyesinde zorunlu kılınmıştır.

### 2. SEA Ek-1 Kapsamlı Karışım Zararlılık Kuralları
* **Akut Toksisite (ATE_mix):** SEA Ek-1 Bölüm 3.1.3.6 harmonik formülü `100/ATE_mix = Σ(Ci/ATEi)`. Oral, Dermal, Soluma (Buhar, Gaz, Toz/Sis) ayrımı ve bilinmeyen bileşenler için SEA Ek-1 Tablo 3.1.2 dönüşüm değerleri desteği.
* **Sucul Çevre Zararları & M-Faktörü:** Akut 1 (H400) ve Kronik 1-4 (H410-H413) toplanabilirlik formülleri; Akut ve Kronik M-faktörü (`M x C`) çarpan desteği.
* **Cilt Aşınması / Tahrişi & Ciddi Göz Hasarı:** Kategori 1A, 1B, 1C hiyerarşisi, Kategori 2 tahriş toplanabilirliği ve Spesifik Konsantrasyon Limitleri (SCL).
* **Aspirasyon Zararı (H304):** $\ge \%10$ aspirasyon toksini ve 40°C'de $\le 20.5\text{ mm}^2/\text{s}$ viskozite kontrolü.
* **CMR & STOT:** Kanserojenlik (H350), Mutajenlik (H340), Üreme Toksisitesi (H360/H361 türevleri) ve Belirli Hedef Organ Toksisitesi (STOT SE 1/2/3, STOT RE 1/2) eşik kuralları.
* **Tamamlayıcı Zararlılıklar:** İzosiyanat uyarısı (EUH204), kuruyan cilt etkisi (EUH066) ve cilt hassaslaştırıcılar için EUH208 bildirim eşikleri.

### 3. Bildirimsel Piktogram Öncelik Matrisi (`PictogramPrecedenceMatrix`)
* SEA Madde 26 ve CLP Madde 26 kuralları harici `pictogram_precedence_matrix.json` dosyasına taşınmıştır.
* `GHS06 (Kafatası)` varsa `GHS07 (Ünlem)` otomatik bastırılır.
* `GHS05 (Aşındırıcı)` cilt/göz tahrişinden kaynaklanan `GHS07`yi bastırır.
* `GHS08 (Sağlık Zararı)` solunum hassaslaşmasından kaynaklanan `GHS07`yi bastırır.
* `GHS01 (Patlayıcı)` varsa `GHS02 (Alev)` ve `GHS03 (Oksitleyici)` bastırılır.
* Tüm baskılama kararları şeffaf denetim izinde (`precedence_audit_log`) gerekçesiyle sunulur.

### 4. Resmî Regülasyon Test Matrisi (Benchmark Suite)
* Mevzuat motorunun güvenilirliğini garanti altına alan **28 adet standart regülasyon benchmark senaryosu**:
  * CSV formatı: `backend/app/data/regulatory_test_matrix.csv`
  * JSON formatı: `backend/app/data/regulatory_test_matrix.json`
* `test_regulatory_test_matrix.py` parametrik test koşucusu ile her senaryo için `EXPECTED_STATUS`, `EXPECTED_H`, `EXPECTED_EUH`, `EXPECTED_PICTOGRAM` ve `EXPECTED_WARNING` değerleri otomatik doğrulanır.

### 5. ADR Tehlikeli Madde Taşımacılık Motoru (`transport_engine.py`)
* Sınıflandırma motorunun çıktılarına ve fiziksel parametrelere göre ADR Sınıfı (Sınıf 3, 6.1, 8, 9), Paketleme Grubu (PG I, II, III), UN Numarası, Tünel Kısıtlama Kodu ve Tremcard bilgilerini otomatik hesaplar.

### 6. 16 Bölümlük SDS Modeli, AI Çeviri & Kurumsal İhracat
* **Pydantic v2 Şeması:** KKDİK Ek-2 alt başlıklarına tam uyumlu 16 bölümlük veri yapısı.
* **Hibrit Çeviri:** Deterministik mevzuat sözlüğü + Google Gemini AI ile Türkçe GBF'den REACH Annex II uyumlu İngilizce SDS üretimi.
* **Kurumsal Dışa Aktarma:** Word (.docx) ve PDF (xhtml2pdf lazy-loading mimarisi ile) antetli, resmi GHS piktogramlı ve kurumsal tipografiye sahip dışa aktarım.

---

## 📂 Proje Dizin Yapısı

```
├── backend/                             # FastAPI Backend Servisi
│   ├── app/
│   │   ├── data/                       # Mevzuat referans verileri ve matrisler
│   │   │   ├── h_statements.json       # Türkçe H-ifadeleri
│   │   │   ├── p_statements.json       # Türkçe P-ifadeleri
│   │   │   ├── pictograms.json         # GHS Piktogram tanımları
│   │   │   ├── h_to_p_map.json         # SEA Ek-4 H ➔ P haritalama kuralları
│   │   │   ├── raw_materials.json      # Endüstriyel hammadde kütüphanesi
│   │   │   ├── pictogram_precedence_matrix.json # SEA Md. 26 Piktogram Öncelik Matrisi
│   │   │   ├── regulatory_test_matrix.csv       # Resmî Regülasyon Test Matrisi (CSV)
│   │   │   └── regulatory_test_matrix.json      # Resmî Regülasyon Test Matrisi (JSON)
│   │   ├── models/                     # Veritabanı ve Pydantic domain modelleri
│   │   │   ├── db_models.py            # SQLite SQLAlchemy tabloları
│   │   │   └── regulatory.py           # StructuredSubstance, DataQuality, SCL, ATE modelleri
│   │   ├── routers/                    # FastAPI REST API Uç Noktaları
│   │   │   ├── products.py             # Ürün CRUD, zararlılık hesaplama, ihracat
│   │   │   ├── references.py           # H/P/Piktogram ve hammadde endpoint'leri
│   │   │   └── ai.py                   # Gemini AI yapılandırma ve çeviri
│   │   ├── schemas/                    # 16 Bölümlük KKDİK SDS Pydantic şemaları
│   │   ├── services/                   # İş mantığı ve regülasyon motorları
│   │   │   ├── regulatory_engine/      # Pipeline, DataQualityAssessor, LabelGenerator, PrecedenceMatrix
│   │   │   ├── rules/                  # Flammable, SkinEye, CMR, STOT, Aquatic, AcuteTox, vb.
│   │   │   ├── classification_engine.py# Motor cephesi (Facade) ve köprü bağlayıcı
│   │   │   ├── transport_engine.py     # ADR Tehlikeli Madde Taşımacılık Motoru
│   │   │   ├── validator_service.py    # KKDİK Ek-2 ve semantik kural denetleyicisi
│   │   │   ├── docx_export_service.py  # Kurumsal Word (.docx) ihracatı
│   │   │   ├── pdf_export_service.py   # Kurumsal PDF ihracatı (Lazy import korumalı)
│   │   │   ├── translation_service.py  # Deterministik & AI hibrit çeviri motoru
│   │   │   └── gemini_service.py       # Google Gemini LLM servisi
│   │   └── templates/                  # Antetli GBF Şablonu, Fontlar ve Vektör Piktogramlar
│   └── tests/                          # 139 Adet Kapsamlı Otomatize Test Paketi
│       ├── test_regulatory_test_matrix.py # 28 adet parametrik regülasyon benchmark testi
│       ├── test_classification_engine.py  # ATE_mix, M-faktör, toplanabilirlik testleri
│       ├── test_validators.py             # KKDİK Ek-2 semantik doğrulama testleri
│       ├── test_models.py                 # Pydantic v2 domain model testleri
│       ├── test_exports.py                # Word, PDF & HTML ihracat testleri
│       └── ...
│
├── frontend/                            # React 19 + Vite Frontend Arayüzü
│   ├── src/
│   │   ├── api/                        # Backend REST API istemcisi
│   │   ├── context/                    # AppContext (Global State & Autosave)
│   │   ├── components/
│   │   │   ├── Wizard/                 # 16 Bölümlük Form Sihirbazı, ATE/M-Faktör girişleri
│   │   │   ├── Common/                 # Canlı KKDİK Doğrulama Çekmecesi, Hesaplama Raporu Modalı
│   │   │   └── ProductList/            # Ürün havuzu, filtreleme, klonlama ve dışa aktarım
│   │   └── index.css                   # Kurumsal Tailwind/CSS tasarım sistemi
```

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Gereksinimler
* **Python:** 3.10+ (Önerilen: 3.12+)
* **Node.js:** 18+ (Önerilen: 20+)

### 2. Backend Kurulumu ve Başlatma
```powershell
# Backend bağımlılıklarını yükleyin
pip install -r backend/requirements.txt

# Backend sunucusunu başlatın
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
* **Backend API Adresi:** `http://127.0.0.1:8000`
* **Swagger API Dokümantasyonu:** `http://127.0.0.1:8000/docs`

### 3. Frontend Kurulumu ve Başlatma
```powershell
# Frontend bağımlılıklarını yükleyin
cd frontend
npm install

# Geliştirici sunucusunu başlatın
npm run dev
```
* **Kullanıcı Arayüzü:** `http://localhost:5173`

---

## 🧪 Testleri Çalıştırma

Backend test paketi; regülasyon test matrisi, ATE harmonik formülleri, toplanabilirlik limitleri, Pydantic modelleri ve ihracat servislerini kapsayan **139 otomatize test** içerir:

```powershell
# Tüm testleri çalıştırma (Tavsiye edilen)
python -m pytest backend/ -v --tb=short

# Yalnızca Resmî Regülasyon Test Matrisini çalıştırma (28 Benchmark Senaryo)
python -m pytest backend/tests/test_regulatory_test_matrix.py -v

# Kod derleme kontrolü (Byte-compile)
python -m compileall backend
```

---

## 📜 İlgili Mevzuat ve Dayanaklar

* **KKDİK Yönetmeliği (Ek-2):** Kimyasalların Kaydı, Değerlendirilmesi, İzni ve Kısıtlanması Hakkında Yönetmelik (Resmî Gazete: 23.06.2017 - 30105 Mükerrer).
* **SEA Yönetmeliği (Ek-1, Ek-2, Ek-4):** Maddelerin ve Karışımların Sınıflandırılması, Etiketlenmesi ve Ambalajlanması Hakkında Yönetmelik (Resmî Gazete: 11.12.2013 - 28848 Mükerrer).
* **AB CLP Tüzüğü (EC 1272/2008):** Classification, Labelling and Packaging of Substances and Mixtures.
* **AB REACH Tüzüğü (EU 2020/878):** Requirements for the Compilation of Safety Data Sheets (Annex II).
* **ADR:** Tehlikeli Malların Karayolu ile Uluslararası Taşımacılığına İlişkin Avrupa Anlaşması.

