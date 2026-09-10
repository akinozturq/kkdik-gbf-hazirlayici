# KKDİK Uyumlu SDS / GBF Hazırlayıcısı — Frontend Arayüzü

React 19, Vite ve modern CSS ile geliştirilmiş, 16 bölümlük interaktif Güvenlik Bilgi Formu (SDS) sihirbazı, veri kalitesi & belirsizlik göstergeleri ve ürün yönetim kullanıcı arayüzü.

## 🌟 Temel Arayüz Özellikleri

* **16 Bölümlük Form Sihirbazı (Wizard):**
  * KKDİK Ek-2 alt başlıklarına göre yapılandırılmış adım adım form sihirbazı.
  * 3.1 Madde ve 3.2 Karışım seçimi (XOR kuralı).
  * Bölüm 3.2 karışım tablosunda ATE (Oral, Dermal, Soluma), M-Faktörü (Akut, Kronik), SCL ve konsantrasyon aralığı (`%min - %max`, `<X%`, `>X%`) girişleri.
* **Veri Kalitesi & Belirsizlik Göstergeleri (Data Quality Profile):**
  * Reçetede konsantrasyon aralığı veya eksik test verisi (parlama noktası, viskozite vb.) olduğunda hesaplama modalında `UNCERTAIN` ve `INCOMPLETE` uyarı rozetleri.
  * Toplam konsantrasyon %100'ü aştığında ($\Sigma C > 100\%$) anlık doğrulama hatası ve uyarı bildirimleri.
  * Aralık eşiğinde kalan zararlılıklar için `INDETERMINATE` (Aralık Eşiği / Belirsiz) etiketleme rozetleri.
* **SEA Karışım Zararlılık Hesaplama Modalı:**
  * Bileşenlerden otomatik zararlılık hesaplama, GHS piktogramları, uyarı kelimesi ve adım adım matematiksel rapor gösterimi; tek tıkla Bölüm 2'ye aktarma.
  * Piktogram öncelik kuralları baskılama denetim izi (`precedence_audit_log`) görüntüleme (örn. GHS06'nın GHS07'yi baskılaması).
* **Canlı KKDİK Mevzuat Denetimi (Validation Drawer):**
  * 0.4 Zorunlu alan, 0.2.4 yasaklı ifadeler, tarih, toplam konsantrasyon ve çapraz H-kodu denetimlerini anlık olarak gösteren çekmece paneli.
* **Hammadde Kütüphanesi Seçici Modalı:**
  * Standart endüstriyel kimyasalları arama, tehlike profillerini inceleme ve formülasyona tek tıkla otomatik aktarma.
* **ADR Taşımacılık Sınıflandırması Entegrasyonu:**
  * Bölüm 14 için otomatik türetilen ADR Sınıfı, Paketleme Grubu ve UN numarası önizlemesi.
* **Sektörel Şablonlar & Otomatik Kaydetme (Autosave):**
  * Tiner, Poliüretan, Boya vb. için tek tıkla şablon doldurma; arka planda sessiz ve güvenli otomatik kayıt.
* **Yapay Zekâ (Gemini AI) Çeviri ve Kurumsal Dışa Aktarma Menüsü:**
  * Türkçe/İngilizce PDF, Word (.docx) indirme ve HTML canlı önizleme.

## 🚀 Çalıştırma

```powershell
cd frontend
npm install
npm run dev
```

* Uygulama adresi: `http://localhost:5173`
* API Proxy: `/api` istekleri otomatik olarak `http://127.0.0.1:8000` backend servisine yönlendirilir (`vite.config.js`).


