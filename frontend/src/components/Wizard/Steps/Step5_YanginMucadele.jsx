import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step5_YanginMucadele() {
  const { sdsData, updateSdsField } = useApp();

  const b5 = sdsData?.b5_yangin_mucadele || {};
  const b5_1 = b5.b5_1 || {};

  return (
    <div>
      <div className="section-group-title">
        <span>5.1. Yangın Söndürücüler</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Uygun Yangın Söndürücü Maddeler <span className="req-star">*</span></span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Su spreyi / sisi, köpük, kuru kimyevi toz, karbon dioksit (CO2)."
            value={b5_1.uygun_sondurucu || ''}
            onChange={(e) => updateSdsField(['b5_yangin_mucadele', 'b5_1', 'uygun_sondurucu'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 5.1"
            onInsertText={(val) => updateSdsField(['b5_yangin_mucadele', 'b5_1', 'uygun_sondurucu'], val)}
            templates={['Köpük, kuru kimyevi toz, karbon dioksit (CO2), su sisi.', 'Çevre yangınına uygun söndürme maddeleri kullanınız.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Güvenlik Nedeniyle Kullanılmaması Gereken Söndürücüler</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Yüksek basınçlı tam su jeti (yangını ve alevlenir sıvıyı etrafa yayabilir)."
            value={b5_1.uygun_olmayan_sondurucu || ''}
            onChange={(e) => updateSdsField(['b5_yangin_mucadele', 'b5_1', 'uygun_olmayan_sondurucu'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 5.1"
            onInsertText={(val) => updateSdsField(['b5_yangin_mucadele', 'b5_1', 'uygun_olmayan_sondurucu'], val)}
            templates={['Yüksek basınçlı su jeti.', 'Bilinen bir kısıtlama yoktur.']}
          />
        </div>
      </div>

      <div className="section-group-title">
        <span>5.2 & 5.3. Özel Zararlar ve İtfaiye Tavsiyeleri</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>5.2. Madde veya Karışımdan Kaynaklanan Özel Zararlar</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Yanma durumunda toksik gazlar (karbon monoksit, karbon dioksit, azot oksitler) açığa çıkar."
            value={b5.b5_2_ozel_zararlar || ''}
            onChange={(e) => updateSdsField(['b5_yangin_mucadele', 'b5_2_ozel_zararlar'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 5.2"
            onInsertText={(val) => updateSdsField(['b5_yangin_mucadele', 'b5_2_ozel_zararlar'], val)}
            templates={['Yanma sonucu karbon oksitler ve zararlı dumanlar oluşabilir.', 'Yanıcı veya patlayıcı buhar-hava karışımı oluşturabilir.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>5.3. Yangın Söndürme Ekipleri İçin Tavsiyeler</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Bağımsız solunum cihazı ve tam koruyucu yangın elbisesi kullanınız. Kapları su püskürterek soğutun."
            value={b5.b5_3_sondurme_ekibi_tavsiyeleri || ''}
            onChange={(e) => updateSdsField(['b5_yangin_mucadele', 'b5_3_sondurme_ekibi_tavsiyeleri'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 5.3"
            onInsertText={(val) => updateSdsField(['b5_yangin_mucadele', 'b5_3_sondurme_ekibi_tavsiyeleri'], val)}
            templates={['Tam koruyucu elbise ve pozitif basınçlı solunum cihazı kullanınız.', 'Yangına maruz kalan kapları su sıkarak soğutunuz.']}
          />
        </div>
      </div>
    </div>
  );
}
