import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step4_IlkYardim() {
  const { sdsData, updateSdsField } = useApp();

  const b4 = sdsData?.b4_ilk_yardim || {};
  const b4_1 = b4.b4_1 || {};

  return (
    <div>
      <div className="section-group-title">
        <span>4.1. İlk Yardım Önlemlerinin Açıklanması</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Solunması Halinde <span className="req-star">*</span></span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Kazazedeyi derhal temiz havaya çıkarın. Nefes alması güçleşirse oksijen verin, doktora başvurun."
            value={b4_1.soluma || ''}
            onChange={(e) => updateSdsField(['b4_ilk_yardim', 'b4_1', 'soluma'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 4.1"
            onInsertText={(val) => updateSdsField(['b4_ilk_yardim', 'b4_1', 'soluma'], val)}
            templates={['Kazazedeyi temiz havaya çıkarın. Rahat nefes alabileceği bir pozisyonda tutun.', 'Özel bir soluma önlemi gerekmez.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Cilt ile Teması Halinde <span className="req-star">*</span></span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Kirlenmiş giysileri hemen çıkarın. Cildi bol su ve sabunla en az 15 dakika yıkayın."
            value={b4_1.cilt_temasi || ''}
            onChange={(e) => updateSdsField(['b4_ilk_yardim', 'b4_1', 'cilt_temasi'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 4.1"
            onInsertText={(val) => updateSdsField(['b4_ilk_yardim', 'b4_1', 'cilt_temasi'], val)}
            templates={['Cildi bol su ve sabun ile yıkayınız.', 'Kirlenmiş giysileri çıkarın ve yeniden kullanmadan önce yıkayın.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Göz ile Teması Halinde <span className="req-star">*</span></span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Göz kapaklarını açık tutarak derhal bol su ile en az 15 dakika yıkayın. Kontak lens varsa çıkarın."
            value={b4_1.goz_temasi || ''}
            onChange={(e) => updateSdsField(['b4_ilk_yardim', 'b4_1', 'goz_temasi'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 4.1"
            onInsertText={(val) => updateSdsField(['b4_ilk_yardim', 'b4_1', 'goz_temasi'], val)}
            templates={['Gözleri birkaç dakika dikkatlice bol su ile yıkayın. Varsa kontakt lensleri çıkarın.', 'Tahriş sürerse doktora başvurun.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Yutulması Halinde <span className="req-star">*</span></span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Ağzı suyla çalkalayın. Doktor tavsiyesi olmadan kesinlikle KUSTURMAYIN. Derhal tıbbi yardım alın."
            value={b4_1.yutma || ''}
            onChange={(e) => updateSdsField(['b4_ilk_yardim', 'b4_1', 'yutma'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 4.1"
            onInsertText={(val) => updateSdsField(['b4_ilk_yardim', 'b4_1', 'yutma'], val)}
            templates={['Ağzı suyla çalkalayın. İstifra ettirmeyiniz. Derhal tıbbi yardım alınız.', 'Bilinç kapalıysa ağızdan hiçbir şey vermeyiniz.']}
          />
        </div>
      </div>

      <div className="section-group-title">
        <span>4.2 & 4.3. Belirtiler ve Tıbbi Müdahale</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>4.2. Akut ve Sonradan Görülen En Önemli Belirtiler ve Etkiler</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Gözde ve ciltte kızarıklık, yanma hissi, solunum yollarında tahriş, baş dönmesi."
            value={b4.b4_2_belirtiler_etkiler || ''}
            onChange={(e) => updateSdsField(['b4_ilk_yardim', 'b4_2_belirtiler_etkiler'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 4.2"
            onInsertText={(val) => updateSdsField(['b4_ilk_yardim', 'b4_2_belirtiler_etkiler'], val)}
            templates={['Bilinen akut veya gecikmeli önemli bir belirti bildirilmemiştir.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>4.3. Tıbbi Müdahale ve Özel Tedavi Gereği İçin İlk İşaretler</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Semptomatik tedavi uygulayınız. Özel bir antidot bulunmamaktadır."
            value={b4.b4_3_acil_tibbi_mudahale || ''}
            onChange={(e) => updateSdsField(['b4_ilk_yardim', 'b4_3_acil_tibbi_mudahale'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 4.3"
            onInsertText={(val) => updateSdsField(['b4_ilk_yardim', 'b4_3_acil_tibbi_mudahale'], val)}
            templates={['Semptomatik ve destekleyici tedavi uygulayınız.', 'Özel bir tedavi gerekmez.']}
          />
        </div>
      </div>
    </div>
  );
}
