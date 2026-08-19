import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step15_Mevzuat() {
  const { sdsData, updateSdsField } = useApp();

  const b15 = sdsData?.b15_mevzuat || {};

  return (
    <div>
      <div className="section-group-title">
        <span>15.1. Madde veya Karışıma Özel Güvenlik, Sağlık ve Çevre Mevzuatı</span>
      </div>

      <div className="form-group">
        <label className="form-label">
          <span>Ulusal ve Uluslararası Mevzuat Hükümleri <span className="req-star">*</span></span>
        </label>
        <textarea
          className="form-control"
          placeholder="ör. T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı KKDİK Yönetmeliği (RG: 23/06/2017 - 30105), SEA Yönetmeliği (RG: 11/12/2013 - 28848), Kimyasal Maddelerle Çalışmalarda Sağlık ve Güvenlik Önlemleri Hakkında Yönetmelik, Tehlikeli Maddelerin Karayoluyla Taşınması Hakkında Yönetmelik."
          value={b15.b15_1_ozel_mevzuat_hukumleri || ''}
          onChange={(e) => updateSdsField(['b15_mevzuat', 'b15_1_ozel_mevzuat_hukumleri'], e.target.value)}
          style={{ minHeight: '110px' }}
        />
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 15.1"
          onInsertText={(val) => updateSdsField(['b15_mevzuat', 'b15_1_ozel_mevzuat_hukumleri'], val)}
          templates={[
            'KKDİK Yönetmeliği (RG: 30105), SEA Yönetmeliği (RG: 28848), Kimyasal Maddelerle Çalışmalarda Sağlık ve Güvenlik Önlemleri Hakkında Yönetmelik.',
          ]}
        />
      </div>

      <div className="section-group-title">
        <span>15.2. Kimyasal Güvenlik Değerlendirmesi</span>
      </div>

      <div className="form-group">
        <label className="form-label">
          <span>Kimyasal Güvenlik Değerlendirmesi (KGD) Yapıldı mı?</span>
        </label>
        <textarea
          className="form-control"
          placeholder="ör. Bu karışım için henüz bir Kimyasal Güvenlik Değerlendirmesi (KGD / Chemical Safety Assessment) gerçekleştirilmemiştir."
          value={b15.b15_2_kimyasal_guvenlik_degerlendirmesi || ''}
          onChange={(e) =>
            updateSdsField(['b15_mevzuat', 'b15_2_kimyasal_guvenlik_degerlendirmesi'], e.target.value)
          }
        />
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 15.2"
          onInsertText={(val) =>
            updateSdsField(['b15_mevzuat', 'b15_2_kimyasal_guvenlik_degerlendirmesi'], val)
          }
          templates={[
            'Tedarikçi tarafından bu madde/karışım için bir Kimyasal Güvenlik Değerlendirmesi yapılmamıştır.',
            'Bileşen maddeler için Kimyasal Güvenlik Değerlendirmesi yapılmıştır.',
          ]}
        />
      </div>
    </div>
  );
}
