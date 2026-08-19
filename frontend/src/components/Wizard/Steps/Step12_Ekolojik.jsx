import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step12_Ekolojik() {
  const { sdsData, updateSdsField } = useApp();

  const b12 = sdsData?.b12_ekolojik || {};

  const ecoFields = [
    {
      key: 'b12_1_toksisite',
      label: '12.1. Toksisite (Ekotoksisite)',
      required: true,
      ph: 'ör. LC50 Balık (96s): > 10 mg/L; EC50 Daphnia (48s): > 100 mg/L veya Sucul ortamda zararlıdır.',
      tpl: 'Sucul organizmalar için toksik/zararlı olarak sınıflandırılmamıştır.',
    },
    {
      key: 'b12_2_kalicilik_bozunabilirlik',
      label: '12.2. Kalıcılık ve Bozunabilirlik',
      required: false,
      ph: 'ör. Biyolojik olarak kolay parçalanabilir (OECD 301B testi: %70+ bozunma).',
      tpl: 'Bileşenler biyolojik olarak kolayca ayrışabilir niteliktedir.',
    },
    {
      key: 'b12_3_biyobirikim',
      label: '12.3. Biyobirikim Potansiyeli',
      required: false,
      ph: 'ör. Düşük biyobirikim potansiyeli (BCF < 100).',
      tpl: 'Biyobirikim potansiyeli düşüktür (log Kow < 3).',
    },
    {
      key: 'b12_4_topraktaki_hareketlilik',
      label: '12.4. Toprakta Hareketlilik',
      required: false,
      ph: 'ör. Toprakta orta derecede hareketlidir (Koc değeri).',
      tpl: 'Su ve toprakta hareketlilik potansiyeli düşüktür / Çözünürlüğüne bağlıdır.',
    },
    {
      key: 'b12_5_pbt_vpvb_sonuclari',
      label: '12.5. PBT ve vPvB Değerlendirmesinin Sonuçları',
      required: false,
      ph: 'ör. Karışım, PBT veya vPvB olarak değerlendirilen maddeler içermemektedir.',
      tpl: 'PBT ve vPvB kriterlerini karşılamaz.',
    },
    {
      key: 'b12_6_diger_olumsuz_etkiler',
      label: '12.6. Diğer Olumsuz Etkiler',
      required: false,
      ph: 'ör. Ozon tabakasına zarar verici madde içermez. Kanalizasyona dökülmemelidir.',
      tpl: 'Çevre üzerinde bilinen diğer olumsuz bir etkisi bulunmamaktadır.',
    },
  ];

  return (
    <div>
      <div className="section-group-title">
        <span>12. Ekolojik Bilgiler</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {ecoFields.map((f) => (
          <div key={f.key} className="form-group">
            <label className="form-label">
              <span>
                {f.label} {f.required && <span className="req-star">*</span>}
              </span>
            </label>
            <textarea
              className="form-control"
              placeholder={f.ph}
              value={b12[f.key] || ''}
              onChange={(e) => updateSdsField(['b12_ekolojik', f.key], e.target.value)}
            />
            <FieldHelper
              legalRef="KKDİK Ek-2 md. 12"
              onInsertText={(val) => updateSdsField(['b12_ekolojik', f.key], val)}
              templates={[f.tpl, 'Veri bulunmamaktadır.']}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
