import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step6_KazaYayilma() {
  const { sdsData, updateSdsField } = useApp();

  const b6 = sdsData?.b6_kaza_sonucu_yayilma || {};
  const b6_1 = b6.b6_1 || {};

  return (
    <div>
      <div className="section-group-title">
        <span>6.1. Kişisel Önlemler, Koruyucu Ekipman ve Acil Durum Prosedürleri</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Acil Durum Personeli Olmayanlar İçin Önlemler <span className="req-star">*</span></span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Tüm ateş kaynaklarını uzaklaştırın. Alanı iyi havalandırın. Yetkisiz personeli tahliye edin."
            value={b6_1.kisisel_onlemler_acil_olmayan || ''}
            onChange={(e) =>
              updateSdsField(['b6_kaza_sonucu_yayilma', 'b6_1', 'kisisel_onlemler_acil_olmayan'], e.target.value)
            }
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 6.1"
            onInsertText={(val) =>
              updateSdsField(['b6_kaza_sonucu_yayilma', 'b6_1', 'kisisel_onlemler_acil_olmayan'], val)
            }
            templates={['Alanı derhal tahliye edin, iyi havalandırın. Ateşleme kaynaklarını ortadan kaldırın.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Acil Durumda Müdahale Edenler İçin Önlemler</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Uygun koruyucu gözlük, nitril eldiven ve buhar filtreli solunum maskesi kullanınız."
            value={b6_1.kisisel_onlemler_acil_mudahale || ''}
            onChange={(e) =>
              updateSdsField(['b6_kaza_sonucu_yayilma', 'b6_1', 'kisisel_onlemler_acil_mudahale'], e.target.value)
            }
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 6.1"
            onInsertText={(val) =>
              updateSdsField(['b6_kaza_sonucu_yayilma', 'b6_1', 'kisisel_onlemler_acil_mudahale'], val)
            }
            templates={['Bölüm 8\'de tavsiye edilen kişisel koruyucu ekipmanı kullanınız.']}
          />
        </div>
      </div>

      <div className="section-group-title">
        <span>6.2 & 6.3. Çevresel Önlemler ve Temizleme Yöntemleri</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>6.2. Çevresel Önlemler <span className="req-star">*</span></span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Kanalizasyona, yüzey veya yer altı sularına karışmasını önleyin. Sızıntı durumunda yetkililere haber verin."
            value={b6.b6_2_cevresel_onlemler || ''}
            onChange={(e) => updateSdsField(['b6_kaza_sonucu_yayilma', 'b6_2_cevresel_onlemler'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 6.2"
            onInsertText={(val) => updateSdsField(['b6_kaza_sonucu_yayilma', 'b6_2_cevresel_onlemler'], val)}
            templates={['Kanalizasyona, su kanallarına ve toprağa karışmasını önleyiniz.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>6.3. Muhafaza Etme ve Temizleme Yöntemleri <span className="req-star">*</span></span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Sıvı emici inert madde (kum, diatomit, talaş) ile toplayın. Bertaraf edilmek üzere uygun etiketli kaplara aktarın."
            value={b6.b6_3_kontrol_temizleme_yontemleri || ''}
            onChange={(e) =>
              updateSdsField(['b6_kaza_sonucu_yayilma', 'b6_3_kontrol_temizleme_yontemleri'], e.target.value)
            }
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 6.3"
            onInsertText={(val) =>
              updateSdsField(['b6_kaza_sonucu_yayilma', 'b6_3_kontrol_temizleme_yontemleri'], val)
            }
            templates={['İnert emici bir materyal ile toplayıp lisanslı atık kabına alınız.']}
          />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">
          <span>6.4. Diğer Bölümlere Atıflar</span>
        </label>
        <input
          type="text"
          className="form-control"
          placeholder="ör. Kişisel korunma için Bölüm 8'e, bertaraf için Bölüm 13'e bakınız."
          value={b6.b6_4_diger_bolumlere_atif || ''}
          onChange={(e) => updateSdsField(['b6_kaza_sonucu_yayilma', 'b6_4_diger_bolumlere_atif'], e.target.value)}
        />
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 6.4"
          onInsertText={(val) => updateSdsField(['b6_kaza_sonucu_yayilma', 'b6_4_diger_bolumlere_atif'], val)}
          templates={["Kişisel korunma donanımları için Bölüm 8'e, atık bertarafı için Bölüm 13'e bakınız."]}
        />
      </div>
    </div>
  );
}
