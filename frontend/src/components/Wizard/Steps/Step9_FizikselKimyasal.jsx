import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step9_FizikselKimyasal() {
  const { sdsData, updateSdsField } = useApp();

  const b9 = sdsData?.b9_fiziksel_kimyasal_ozellikler || {};
  const b9_1 = b9.b9_1 || {};

  const propConfigs = [
    { key: 'gorunum', label: 'Görünüm (Fiziksel hal, renk)', required: true, ph: 'ör. Sıvı, berrak sarımtırak' },
    { key: 'koku', label: 'Koku', required: true, ph: 'ör. Karakteristik solvent kokusu' },
    { key: 'koku_esigi', label: 'Koku Eşiği', required: false, ph: 'ör. Belirlenmemiştir / 0.1 ppm' },
    { key: 'ph', label: 'pH Değeri', required: true, ph: 'ör. 7.5 - 8.5 (veya Uygulanamaz - susuz ortam)' },
    { key: 'erime_noktasi', label: 'Erime / Donma Noktası', required: false, ph: 'ör. <-20 °C' },
    { key: 'kaynama_noktasi', label: 'İlk Kaynama Noktası ve Aralığı', required: false, ph: 'ör. 138 - 144 °C' },
    { key: 'parlama_noktasi', label: 'Parlama Noktası', required: true, ph: 'ör. 28 °C (Kapalı kap)' },
    { key: 'buharlasma_hizi', label: 'Buharlaşma Hızı', required: false, ph: 'ör. Belirlenmemiştir' },
    { key: 'alevlenirlik', label: 'Alevlenirlik (Katı, gaz)', required: false, ph: 'ör. Alevlenir sıvı' },
    { key: 'ust_alt_limitler', label: 'Üst / Alt Alevlenirlik veya Patlama Limitleri', required: false, ph: 'ör. Alt: %1.0, Üst: %7.0' },
    { key: 'buhar_basinci', label: 'Buhar Basıncı', required: false, ph: 'ör. 8 hPa (20°C)' },
    { key: 'buhar_yogunlugu', label: 'Buhar Yoğunluğu', required: false, ph: 'ör. 3.7 (Hava = 1)' },
    { key: 'bagil_yogunluk', label: 'Bağıl Yoğunluk / Özgül Ağırlık', required: false, ph: 'ör. 1.05 ± 0.02 g/cm³ (20°C)' },
    { key: 'cozunurluk', label: 'Çözünürlük (Suda vb.)', required: true, ph: 'ör. Suda çözünmez, organik solventlerde çözünür' },
    { key: 'dagilim_katsayisi_log_kow', label: 'Dağılım Katsayısı (n-oktanol/su - log Kow)', required: false, ph: 'ör. 3.12 (Hesaplanmış)' },
    { key: 'kendiliginden_tutusma_sicakligi', label: 'Kendiliğinden Tutuşma Sıcaklığı', required: false, ph: 'ör. 465 °C' },
    { key: 'bozunma_sicakligi', label: 'Bozunma Sıcaklığı', required: false, ph: 'ör. > 200 °C' },
    { key: 'akiskanlik', label: 'Akışkanlık (Viskozite)', required: false, ph: 'ör. 400 - 600 mPa.s (25°C, Brookfield)' },
    { key: 'patlayici_ozellikler', label: 'Patlayıcı Özellikler', required: false, ph: 'ör. Patlayıcı değildir' },
    { key: 'oksitleyici_ozellikler', label: 'Oksitleyici Özellikler', required: false, ph: 'ör. Oksitleyici değildir' },
  ];

  return (
    <div>
      <div className="section-group-title">
        <span>9.1. Temel Fiziksel ve Kimyasal Özellikler Hakkında Bilgi</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
        {propConfigs.map((prop) => (
          <div key={prop.key} className="form-group">
            <label className="form-label">
              <span>
                {prop.label} {prop.required && <span className="req-star">*</span>}
              </span>
            </label>
            <input
              type="text"
              className="form-control"
              placeholder={prop.ph}
              value={b9_1[prop.key] || ''}
              onChange={(e) =>
                updateSdsField(['b9_fiziksel_kimyasal_ozellikler', 'b9_1', prop.key], e.target.value)
              }
            />
            <FieldHelper
              onInsertText={(val) =>
                updateSdsField(['b9_fiziksel_kimyasal_ozellikler', 'b9_1', prop.key], val)
              }
              templates={['Uygulanabilir değildir.', 'Belirlenmemiştir.']}
            />
          </div>
        ))}
      </div>

      <div className="section-group-title">
        <span>9.2. Diğer Bilgiler</span>
      </div>

      <div className="form-group">
        <label className="form-label">
          <span>Diğer Fiziksel/Kimyasal Parametreler (Karışabilirlik, İletkenlik, Katı Madde vb.)</span>
        </label>
        <textarea
          className="form-control"
          placeholder="ör. Katı Madde Oranı: %60 ± 2, Uçucu Organik Bileşik (VOC): 380 g/L"
          value={b9.b9_2_diger_bilgiler || ''}
          onChange={(e) =>
            updateSdsField(['b9_fiziksel_kimyasal_ozellikler', 'b9_2_diger_bilgiler'], e.target.value)
          }
        />
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 9.2"
          onInsertText={(val) =>
            updateSdsField(['b9_fiziksel_kimyasal_ozellikler', 'b9_2_diger_bilgiler'], val)
          }
          templates={['Ek bilgi bulunmamaktadır.']}
        />
      </div>
    </div>
  );
}
