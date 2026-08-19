import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step7_EllecmeDepolama() {
  const { sdsData, updateSdsField } = useApp();

  const b7 = sdsData?.b7_ellecme_depolama || {};
  const b7_2 = b7.b7_2 || {};

  return (
    <div>
      <div className="section-group-title">
        <span>7.1. Güvenli Elleçleme İçin Önlemler</span>
      </div>

      <div className="form-group">
        <label className="form-label">
          <span>Güvenli Elleçleme Tavsiyeleri <span className="req-star">*</span></span>
        </label>
        <textarea
          className="form-control"
          placeholder="ör. Buhar veya sisini solumaktan kaçının. Statik elektriklenmeye karşı topraklama yapın. Çalışma alanında yemeyin, içmeyin."
          value={b7.b7_1_guvenli_ellecleme || ''}
          onChange={(e) => updateSdsField(['b7_ellecme_depolama', 'b7_1_guvenli_ellecleme'], e.target.value)}
        />
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 7.1"
          onInsertText={(val) => updateSdsField(['b7_ellecme_depolama', 'b7_1_guvenli_ellecleme'], val)}
          templates={[
            'İyi havalandırılmış alanlarda kullanın. Göz ve cilt temasından kaçının. Statik elektriklenmeye karşı önlem alın.',
            'Kullanım sonrası ellerinizi iyice yıkayınız.',
          ]}
        />
      </div>

      <div className="section-group-title">
        <span>7.2. Güvenli Saklama Koşulları ve Uyumsuzluklar</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Güvenli Depolama Koşulları <span className="req-star">*</span></span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Serin, kuru ve iyi havalandırılan alanda, doğrudan güneş ışığından uzakta (+5°C ile +25°C arasında) orijinal kabında saklayın."
            value={b7_2.guvenli_depolama_kosullari || ''}
            onChange={(e) =>
              updateSdsField(['b7_ellecme_depolama', 'b7_2', 'guvenli_depolama_kosullari'], e.target.value)
            }
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 7.2"
            onInsertText={(val) =>
              updateSdsField(['b7_ellecme_depolama', 'b7_2', 'guvenli_depolama_kosullari'], val)
            }
            templates={['Serin, kuru, iyi havalandırılan bir yerde orijinal kabı sıkıca kapalı olarak muhafaza ediniz.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Birlikte Depolanmaması Gereken Uyumsuz Maddeler</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Kuvvetli asitler, bazlar, kuvvetli oksitleyiciler ve organik peroksitler."
            value={b7_2.uyumsuzluklar || ''}
            onChange={(e) =>
              updateSdsField(['b7_ellecme_depolama', 'b7_2', 'uyumsuzluklar'], e.target.value)
            }
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 7.2"
            onInsertText={(val) =>
              updateSdsField(['b7_ellecme_depolama', 'b7_2', 'uyumsuzluklar'], val)
            }
            templates={['Kuvvetli oksitleyici ajanlar ve asitlerden uzak tutunuz.']}
          />
        </div>
      </div>

      <div className="section-group-title">
        <span>7.3. Belirli Son Kullanımlar</span>
      </div>

      <div className="form-group">
        <label className="form-label">
          <span>Belirli Son Kullanımlar</span>
        </label>
        <input
          type="text"
          className="form-control"
          placeholder="ör. Bölüm 1.2'de tanımlanan endüstriyel kullanımlar dışındaki alanlar için tedarikçiye başvurunuz."
          value={b7.b7_3_belirli_son_kullanimlar || ''}
          onChange={(e) =>
            updateSdsField(['b7_ellecme_depolama', 'b7_3_belirli_son_kullanimlar'], e.target.value)
          }
        />
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 7.3"
          onInsertText={(val) =>
            updateSdsField(['b7_ellecme_depolama', 'b7_3_belirli_son_kullanimlar'], val)
          }
          templates={['Bölüm 1.2\'de belirtilen belirlenmiş kullanımlar haricinde özel bir kullanım tavsiye edilmez.']}
        />
      </div>
    </div>
  );
}
