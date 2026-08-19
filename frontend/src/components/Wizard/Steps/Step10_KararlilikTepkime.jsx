import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step10_KararlilikTepkime() {
  const { sdsData, updateSdsField } = useApp();

  const b10 = sdsData?.b10_kararlilik_tepkime || {};

  const fields = [
    {
      key: 'b10_1_tepkime',
      label: '10.1. Tepkime',
      required: true,
      ph: 'ör. Normal kullanım ve depolama koşullarında tehlikeli tepkime vermez.',
      tpl: 'Tavsiye edilen koşullarda depolandığında ve elleçlendiğinde tehlikeli bir tepkime beklenmez.',
    },
    {
      key: 'b10_2_kimyasal_kararlilik',
      label: '10.2. Kimyasal Kararlılık',
      required: true,
      ph: 'ör. Normal ortam sıcaklığı ve basıncında kimyasal olarak kararlıdır.',
      tpl: 'Normal çevre ve öngörülen depolama/elleçleme sıcaklık ve basınç koşullarında kararlıdır.',
    },
    {
      key: 'b10_3_zararli_reaksiyon_olasiligi',
      label: '10.3. Zararlı Tepkime Olasılığı',
      required: false,
      ph: 'ör. Aşırı ısı ve uyumsuz maddelerle temasta ekzotermik polimerizasyon veya reaksiyon oluşabilir.',
      tpl: 'Normal depolama ve kullanım koşullarında tehlikeli reaksiyonlar meydana gelmez.',
    },
    {
      key: 'b10_4_kacinilmasi_gereken_durumlar',
      label: '10.4. Kaçınılması Gereken Durumlar',
      required: false,
      ph: 'ör. Yüksek sıcaklık, açık alev, kıvılcım, statik boşalma ve doğrudan güneş ışığı.',
      tpl: 'Isı, alev, kıvılcım ve diğer ateşleme kaynaklarından uzak tutunuz.',
    },
    {
      key: 'b10_5_kacinilmasi_gereken_maddeler',
      label: '10.5. Kaçınılması Gereken Maddeler',
      required: false,
      ph: 'ör. Kuvvetli asitler, bazlar, kuvvetli oksitleyiciler ve peroksitler.',
      tpl: 'Kuvvetli asitler, kuvvetli bazlar ve oksitleyici maddeler.',
    },
    {
      key: 'b10_6_zararli_bozunma_urunleri',
      label: '10.6. Zararlı Bozunma Ürünleri',
      required: false,
      ph: 'ör. Normal koşullarda ayrışmaz. Yangın halinde karbon monoksit, karbon dioksit açığa çıkar.',
      tpl: 'Normal depolama ve kullanımda zararlı bozunma ürünleri oluşmaz. Yangında toksik gazlar çıkabilir.',
    },
  ];

  return (
    <div>
      <div className="section-group-title">
        <span>10. Kararlılık ve Tepkime</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {fields.map((f) => (
          <div key={f.key} className="form-group">
            <label className="form-label">
              <span>
                {f.label} {f.required && <span className="req-star">*</span>}
              </span>
            </label>
            <textarea
              className="form-control"
              placeholder={f.ph}
              value={b10[f.key] || ''}
              onChange={(e) => updateSdsField(['b10_kararlilik_tepkime', f.key], e.target.value)}
            />
            <FieldHelper
              legalRef="KKDİK Ek-2 md. 10"
              onInsertText={(val) => updateSdsField(['b10_kararlilik_tepkime', f.key], val)}
              templates={[f.tpl]}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
