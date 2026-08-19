import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step14_Tasimacilik() {
  const { sdsData, updateSdsField } = useApp();

  const b14 = sdsData?.b14_tasimacilik || {};

  return (
    <div>
      <div className="section-group-title">
        <span>14. Taşımacılık Bilgisi (ADR / RID / IMDG / IATA)</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>14.1. UN Numarası <span className="req-star">*</span></span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. UN 1263 veya UN 1866"
            value={b14.b14_1_un_numarasi || ''}
            onChange={(e) => updateSdsField(['b14_tasimacilik', 'b14_1_un_numarasi'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 14.1"
            onInsertText={(val) => updateSdsField(['b14_tasimacilik', 'b14_1_un_numarasi'], val)}
            templates={['Taşımacılık mevzuatına göre tehlikeli madde değildir.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>14.2. Uygun UN Taşımacılık Adı</span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. REÇİNE ÇÖZELTİSİ, alevlenebilir (RESIN SOLUTION, flammable)"
            value={b14.b14_2_un_tasimacilik_adi || ''}
            onChange={(e) => updateSdsField(['b14_tasimacilik', 'b14_2_un_tasimacilik_adi'], e.target.value)}
          />
          <FieldHelper
            legalRef="md. 14.2"
            onInsertText={(val) => updateSdsField(['b14_tasimacilik', 'b14_2_un_tasimacilik_adi'], val)}
            templates={['Uygulanabilir değildir.']}
          />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>14.3. Taşımacılık Zararlılık Sınıfı</span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. 3 (Alevlenir Sıvılar)"
            value={b14.b14_3_tasimacilik_sinifi || ''}
            onChange={(e) => updateSdsField(['b14_tasimacilik', 'b14_3_tasimacilik_sinifi'], e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>14.4. Ambalajlama Grubu</span>
          </label>
          <select
            className="form-control"
            value={b14.b14_4_ambalajlama_grubu || ''}
            onChange={(e) => updateSdsField(['b14_tasimacilik', 'b14_4_ambalajlama_grubu'], e.target.value)}
          >
            <option value="">Seçiniz...</option>
            <option value="PG I">PG I (Çok tehlikeli)</option>
            <option value="PG II">PG II (Orta tehlikeli)</option>
            <option value="PG III">PG III (Az tehlikeli)</option>
            <option value="Uygulanabilir değildir">Uygulanabilir değildir</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>14.5. Çevresel Zararlar</span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. Deniz Kirletici değildir (No/Hayır)"
            value={b14.b14_5_cevresel_zararlar || ''}
            onChange={(e) => updateSdsField(['b14_tasimacilik', 'b14_5_cevresel_zararlar'], e.target.value)}
          />
          <FieldHelper
            onInsertText={(val) => updateSdsField(['b14_tasimacilik', 'b14_5_cevresel_zararlar'], val)}
            templates={['Deniz Kirletici değildir.', 'Deniz Kirleticidir (Marine Pollutant).']}
          />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>14.6. Kullanıcı İçin Özel Önlemler</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. ADR / RID kurallarına uygun kapalı ve havalandırmalı araçlarda taşınmalıdır. Tünel Kısıtlama Kodu: (D/E)"
            value={b14.b14_6_kullanici_ozel_onlemler || ''}
            onChange={(e) => updateSdsField(['b14_tasimacilik', 'b14_6_kullanici_ozel_onlemler'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 14.6"
            onInsertText={(val) => updateSdsField(['b14_tasimacilik', 'b14_6_kullanici_ozel_onlemler'], val)}
            templates={['Taşıma sırasında devrilmesini ve ambalaj hasarını önleyecek tedbirleri alınız.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>14.7. MARPOL 73/78 Ek II ve IBC Koduna Göre Dökme Taşımacılık</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Uygulanabilir değildir (Ambalajlı olarak taşınır)."
            value={b14.b14_7_marpol_ibc || ''}
            onChange={(e) => updateSdsField(['b14_tasimacilik', 'b14_7_marpol_ibc'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 14.7"
            onInsertText={(val) => updateSdsField(['b14_tasimacilik', 'b14_7_marpol_ibc'], val)}
            templates={['Uygulanabilir değildir (Ürün yalnızca ambalajlı olarak sevk edilmektedir).']}
          />
        </div>
      </div>
    </div>
  );
}
