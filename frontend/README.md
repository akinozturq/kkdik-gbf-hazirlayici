# KKDİK Uyumlu SDS / GBF Hazırlayıcısı — Frontend Arayüzü

React 19, Vite ve modern CSS ile geliştirilmiş, 16 bölümlük interaktif Güvenlik Bilgi Formu (SDS) sihirbazı ve ürün yönetim kullanıcı arayüzü.

## 🌟 Temel Arayüz Özellikleri

* **16 Bölümlük Form Sihirbazı (Wizard):**
  * KKDİK Ek-2 alt başlıklarına göre yapılandırılmış adım adım form sihirbazı.
  * 3.1 Madde ve 3.2 Karışım seçimi (XOR kuralı).
  * Bölüm 3.2 karışım tablosunda ATE (Oral, Dermal, Soluma) ve M-Faktörü (Akut, Kronik) parametre girişleri.
* **Canlı KKDİK Mevzuat Denetimi (Validation Drawer):**
  * 0.4 Zorunlu alan, 0.2.4 yasaklı ifadeler, tarih ve çapraz H-kodu denetimlerini anlık olarak gösteren çekmece paneli.
* **SEA Karışım Zararlılık Hesaplama Modalı:**
  * Bileşenlerden otomatik zararlılık hesaplama, GHS piktogramları, uyarı kelimesi ve adım adım matematiksel rapor gösterimi; tek tıkla Bölüm 2'ye aktarma.
* **Hammadde Kütüphanesi Seçici Modalı:**
  * Standart kimyasalları arama, detaylarını inceleme ve formülasyona otomatik aktarma.
* **Sektörel Şablonlar & Otomatik Kaydetme (Autosave):**
  * Tiner, Poliüretan, Boya vb. için tek tıkla şablon doldurma; arka planda sessiz ve güvenli otomatik kayıt.
* **Yapay Zekâ (Gemini AI) Çeviri ve Dışa Aktarma Menüsü:**
  * Türkçe/İngilizce PDF, Word (.docx) indirme ve HTML canlı önizleme.

## 🚀 Çalıştırma

```powershell
cd frontend
npm install
npm run dev
```

* Uygulama adresi: `http://localhost:5173`
* API Proxy: `/api` istekleri otomatik olarak `http://127.0.0.1:8000` backend servisine yönlendirilir (`vite.config.js`).

