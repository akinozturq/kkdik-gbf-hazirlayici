import React, { useState } from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';
import { Sparkles, Plus, Trash2 } from 'lucide-react';

export default function Step16_DigerBilgiler() {
  const { sdsData, updateSdsField, autoFillHStatements } = useApp();
  const [autoFilling, setAutoFilling] = useState(false);

  const b16 = sdsData?.b16_diger_bilgiler || {};
  const tamHIfadeleri = b16.tam_h_ifadeleri || [];

  const handleAutoFillH = async () => {
    setAutoFilling(true);
    try {
      await autoFillHStatements();
    } finally {
      setAutoFilling(false);
    }
  };

  const addHRow = () => {
    updateSdsField(
      ['b16_diger_bilgiler', 'tam_h_ifadeleri'],
      [...tamHIfadeleri, '']
    );
  };

  const updateHRow = (index, value) => {
    const updated = [...tamHIfadeleri];
    updated[index] = value;
    updateSdsField(['b16_diger_bilgiler', 'tam_h_ifadeleri'], updated);
  };

  const removeHRow = (index) => {
    const updated = tamHIfadeleri.filter((_, i) => i !== index);
    updateSdsField(['b16_diger_bilgiler', 'tam_h_ifadeleri'], updated);
  };

  return (
    <div>
      {/* Otomatik H-Kodları Derleme Alanı */}
      <div className="section-group-title">
        <span>16.d. Zararlılık İfadelerinin (H-Kodları) Tam Metinleri</span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={handleAutoFillH}
            disabled={autoFilling}
            style={{ background: '#eff6ff', borderColor: '#3b82f6', color: '#1d4ed8' }}
          >
            <Sparkles size={14} />
            {autoFilling ? 'Toplanıyor...' : 'Formdaki H-Kodlarından Otomatik Derle'}
          </button>
          <button type="button" className="btn btn-secondary btn-sm" onClick={addHRow}>
            <Plus size={14} />
            Manuel Satır Ekle
          </button>
        </div>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '10px' }}>
          KKDİK Ek-2 Madde 2.1 ve 16.d gereği, formun 2. ve 3. bölümlerinde kısaltma olarak yer alan tüm H-ifadelerinin tam Türkçe metinleri burada listelenmelidir.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {tamHIfadeleri.map((hText, idx) => (
            <div key={idx} style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input
                type="text"
                className="form-control"
                placeholder="ör. H225: Kolay alevlenir sıvı ve buhar."
                value={hText}
                onChange={(e) => updateHRow(idx, e.target.value)}
              />
              <button
                type="button"
                className="btn btn-danger btn-sm"
                onClick={() => removeHRow(idx)}
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))}
          {tamHIfadeleri.length === 0 && (
            <div
              style={{
                padding: '24px',
                textAlign: 'center',
                background: '#f8fafc',
                border: '1px dashed #cbd5e1',
                borderRadius: '8px',
                color: '#64748b',
                fontSize: '0.85rem',
              }}
            >
              Henüz H-ifadeleri tam metni eklenmedi. Yukarıdaki <strong>"Formdaki H-Kodlarından Otomatik Derle"</strong> butonuna basarak 2. ve 3. bölümdeki kodların tam açıklamalarını anında ekleyebilirsiniz.
            </div>
          )}
        </div>
      </div>

      {/* Diğer Alt Bölümler */}
      <div className="section-group-title">
        <span>Diğer Bilgiler ve Açıklamalar</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Revizyon Açıklaması ve Değişiklikler</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. İlk versiyon, KKDİK Yönetmeliği Ek-2 hükümlerine uygun olarak hazırlanmıştır."
            value={b16.revizyon_aciklamasi || ''}
            onChange={(e) => updateSdsField(['b16_diger_bilgiler', 'revizyon_aciklamasi'], e.target.value)}
          />
          <FieldHelper
            onInsertText={(val) => updateSdsField(['b16_diger_bilgiler', 'revizyon_aciklamasi'], val)}
            templates={['İlk versiyon. KKDİK Ek-2 formatında hazırlanmıştır.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Kısaltmalar ve Akronimler Anahtarı</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. ADR: Tehlikeli Malların Karayolu ile Uluslararası Taşınmasına İlişkin Avrupa Anlaşması; CAS: Chemical Abstracts Service; TWA: Zaman Ağırlıklı Ortalama; STEL: Kısa Süreli Maruziyet Sınırı."
            value={b16.kisaltmalar_anahtari || ''}
            onChange={(e) => updateSdsField(['b16_diger_bilgiler', 'kisaltmalar_anahtari'], e.target.value)}
          />
          <FieldHelper
            onInsertText={(val) => updateSdsField(['b16_diger_bilgiler', 'kisaltmalar_anahtari'], val)}
            templates={[
              'ADR: Tehlikeli Malların Karayoluyla Taşınması; CAS: Chemical Abstracts Service; TWA: 8 saatlik zaman ağırlıklı ortalama maruziyet sınırı; STEL: 15 dakikalık kısa süreli maruziyet sınırı; LD50: Test hayvanlarının %50\'sini öldüren ölümcül doz.',
            ]}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Önemli Literatür Referansları ve Veri Kaynakları</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. ECHA (Avrupa Kimyasallar Ajansı) Veritabanı, T.C. Çevre Şehircilik ve İklim Değişikliği Bakanlığı Kimyasallar Yönetimi Portalı, Hammadde Güvenlik Bilgi Formları."
            value={b16.literatur_referanslari || ''}
            onChange={(e) => updateSdsField(['b16_diger_bilgiler', 'literatur_referanslari'], e.target.value)}
          />
          <FieldHelper
            onInsertText={(val) => updateSdsField(['b16_diger_bilgiler', 'literatur_referanslari'], val)}
            templates={['ECHA Veritabanı, Hammadde Üreticisi Güvenlik Bilgi Formları, Ulusal Mevzuat Veritabanı.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Karışım Sınıflandırma Değerlendirme Yöntemleri</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. SEA Yönetmeliği (RG: 28848) Ek-1 kapsamındaki hesaplama ve eşik değer konsantrasyon yöntemleri kullanılmıştır."
            value={b16.degerlendirme_yontemleri || ''}
            onChange={(e) => updateSdsField(['b16_diger_bilgiler', 'degerlendirme_yontemleri'], e.target.value)}
          />
          <FieldHelper
            onInsertText={(val) => updateSdsField(['b16_diger_bilgiler', 'degerlendirme_yontemleri'], val)}
            templates={['SEA Yönetmeliği hesaplama ve konsantrasyon eşik yöntemleri ile sınıflandırılmıştır.']}
          />
        </div>

        <div className="form-group" style={{ gridColumn: 'span 2' }}>
          <label className="form-label">
            <span>İşçiler İçin Eğitim Tavsiyeleri</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Çalışanlar kimyasal maddelerin güvenli elleçlenmesi, kişisel koruyucu donanım kullanımı ve acil durum müdahale prosedürleri konusunda eğitilmelidir."
            value={b16.egitim_tavsiyeleri || ''}
            onChange={(e) => updateSdsField(['b16_diger_bilgiler', 'egitim_tavsiyeleri'], e.target.value)}
          />
          <FieldHelper
            onInsertText={(val) => updateSdsField(['b16_diger_bilgiler', 'egitim_tavsiyeleri'], val)}
            templates={['Çalışanlara kimyasal maddelerle çalışma, KKD kullanımı ve acil müdahale eğitimleri verilmelidir.']}
          />
        </div>
      </div>
    </div>
  );
}
