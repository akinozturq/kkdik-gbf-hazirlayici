import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step13_Bertaraf() {
  const { sdsData, updateSdsField } = useApp();

  const b13 = sdsData?.b13_bertaraf || {};

  return (
    <div>
      <div className="section-group-title">
        <span>13.1. Atık İşleme Yöntemleri</span>
      </div>

      <div className="form-group">
        <label className="form-label">
          <span>Ürün Atık İşleme ve Bertaraf Yöntemleri <span className="req-star">*</span></span>
        </label>
        <textarea
          className="form-control"
          placeholder="ör. Lisanslı tehlikeli atık yakma veya bertaraf tesisine gönderilmelidir. Atık Yönetimi Yönetmeliği (RG: 29314) hükümlerine uyulmalıdır. Önerilen Atık Kodu: 08 01 11* (Organik çözücüler veya diğer tehlikeli maddeler içeren atık boya ve vernikler)."
          value={b13.b13_1_atik_isleme_yontemleri || ''}
          onChange={(e) => updateSdsField(['b13_bertaraf', 'b13_1_atik_isleme_yontemleri'], e.target.value)}
        />
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 13.1"
          onInsertText={(val) => updateSdsField(['b13_bertaraf', 'b13_1_atik_isleme_yontemleri'], val)}
          templates={[
            'Ulusal ve yerel atık mevzuatına uygun olarak lisanslı atık bertaraf firmalarına teslim edilmelidir. Atık Kodu: 08 01 11*',
            'Evsel atıklarla birlikte bertaraf edilmemeli, lisanslı tesislere gönderilmelidir.',
          ]}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Ambalaj Atıklarının İşlenmesi</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Tamamen boşaltılmış ambalajlar tehlikeli atık olarak lisanslı geri kazanım veya bertaraf firmalarına teslim edilmelidir."
            value={b13.b13_1_ambalaj_atik_isleme || ''}
            onChange={(e) => updateSdsField(['b13_bertaraf', 'b13_1_ambalaj_atik_isleme'], e.target.value)}
          />
          <FieldHelper
            legalRef="md. 13.1"
            onInsertText={(val) => updateSdsField(['b13_bertaraf', 'b13_1_ambalaj_atik_isleme'], val)}
            templates={['Boş ambalajlar tehlikeli atık olarak lisanslı geri kazanım tesislerine teslim edilmelidir. Atık Kodu: 15 01 10*']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Kanalizasyon ve Çevreye Boşaltma Uyarısı</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Kanalizasyona, yüzey sularına veya doğaya kesinlikle boşaltılmamalıdır."
            value={b13.b13_1_kanalizasyon_uyarisi || ''}
            onChange={(e) => updateSdsField(['b13_bertaraf', 'b13_1_kanalizasyon_uyarisi'], e.target.value)}
          />
          <FieldHelper
            legalRef="md. 13.1"
            onInsertText={(val) => updateSdsField(['b13_bertaraf', 'b13_1_kanalizasyon_uyarisi'], val)}
            templates={['Kanalizasyona, su kanallarına veya toprağa dökülmesine kesinlikle izin verilmemelidir.']}
          />
        </div>
      </div>
    </div>
  );
}
