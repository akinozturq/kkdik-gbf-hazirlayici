import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step1_Kimlik() {
  const { sdsData, updateSdsField } = useApp();

  const b1 = sdsData?.b1_kimlik || {};
  const b1_1 = b1.b1_1 || {};
  const b1_2 = b1.b1_2 || {};
  const b1_3 = b1.b1_3 || {};
  const b1_4 = b1.b1_4 || {};
  const meta = sdsData?.meta || {};

  return (
    <div>
      {/* 0.2.5 Meta Bilgileri */}
      <div className="section-group-title">
        <span>Meta Bilgileri (Hazırlama & Revizyon)</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Hazırlama Tarihi <span className="req-star">*</span></span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="GG.AA.YYYY"
            value={meta.hazirlama_tarihi || ''}
            onChange={(e) => updateSdsField(['meta', 'hazirlama_tarihi'], e.target.value)}
          />
          <FieldHelper legalRef="KKDİK Ek-2 md. 0.2.5" tooltip="İlk sayfada yer alması zorunludur." />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Revizyon Tarihi</span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="GG.AA.YYYY"
            value={meta.revizyon_tarihi || ''}
            onChange={(e) => updateSdsField(['meta', 'revizyon_tarihi'], e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Revizyon No</span>
          </label>
          <input
            type="text"
            className="form-control"
            value={meta.revizyon_no || '0'}
            onChange={(e) => updateSdsField(['meta', 'revizyon_no'], e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Versiyon No</span>
          </label>
          <input
            type="text"
            className="form-control"
            value={meta.versiyon_no || '1.0'}
            onChange={(e) => updateSdsField(['meta', 'versiyon_no'], e.target.value)}
          />
        </div>
      </div>

      {/* 1.1 Madde / Karışım Kimliği */}
      <div className="section-group-title">
        <span>1.1. Madde / Karışım Kimliği</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Madde veya Karışımın Adı <span className="req-star">*</span></span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. Polyester Reçine PRS-100"
            value={b1_1.madde_karisim_adi || ''}
            onChange={(e) => updateSdsField(['b1_kimlik', 'b1_1', 'madde_karisim_adi'], e.target.value)}
          />
          <FieldHelper legalRef="KKDİK Ek-2 md. 1.1" tooltip="SEA Yönetmeliği md. 20(2)'ye göre Türkçe tanımlayıcı ad." />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>KKDİK / REACH Kayıt Numarası</span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. 01-2119457290-43-0000"
            value={b1_1.kayit_numarasi || ''}
            onChange={(e) => updateSdsField(['b1_kimlik', 'b1_1', 'kayit_numarasi'], e.target.value)}
          />
          <FieldHelper
            legalRef="md. 1.1"
            onInsertText={(val) => updateSdsField(['b1_kimlik', 'b1_1', 'kayit_numarasi'], val)}
            templates={['Kayıttan muaftır.', 'Uygulanabilir değildir.']}
          />
        </div>
      </div>

      {/* 1.2 Kullanımlar */}
      <div className="section-group-title">
        <span>1.2. Madde veya Karışımın Belirlenmiş Kullanımları ve Tavsiye Edilmeyen Kullanımları</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Tanımlanmış / Tavsiye Edilen Kullanımlar</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Sanayi ve endüstriyel tesislerde kompozit döküm ve bağlayıcı olarak kullanılır."
            value={(b1_2.tanimlanmis_kullanimlar || []).join('\n')}
            onChange={(e) =>
              updateSdsField(
                ['b1_kimlik', 'b1_2', 'tanimlanmis_kullanimlar'],
                e.target.value.split('\n').filter((x) => x.trim())
              )
            }
          />
          <FieldHelper legalRef="KKDİK Ek-2 md. 1.2" tooltip="Kullanım alanları açıkça belirtilmelidir." />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Tavsiye Edilmeyen Kullanımlar</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Tüketici tipi genel hobi uygulamaları ve çocukların erişebileceği alanlar."
            value={(b1_2.tavsiye_edilmeyen_kullanimlar || []).join('\n')}
            onChange={(e) =>
              updateSdsField(
                ['b1_kimlik', 'b1_2', 'tavsiye_edilmeyen_kullanimlar'],
                e.target.value.split('\n').filter((x) => x.trim())
              )
            }
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 1.2"
            onInsertText={(val) =>
              updateSdsField(['b1_kimlik', 'b1_2', 'tavsiye_edilmeyen_kullanimlar'], [val])
            }
            templates={['Tavsiye edilen kullanımların dışında kullanılmamalıdır.']}
          />
        </div>
      </div>

      {/* 1.3 Tedarikçi Bilgileri */}
      <div className="section-group-title">
        <span>1.3. Güvenlik Bilgi Formu Tedarikçisinin Bilgileri</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Tedarikçi / İmalatçı Şirket Adı <span className="req-star">*</span></span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. Aypol Kimya San. ve Tic. A.Ş."
            value={b1_3.tedarikci_adi || ''}
            onChange={(e) => updateSdsField(['b1_kimlik', 'b1_3', 'tedarikci_adi'], e.target.value)}
          />
          <FieldHelper legalRef="KKDİK Ek-2 md. 1.3" />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Yetkili Kişi (KDU / Sertifikalı Hazırlayıcı)</span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. Kimyager Ahmet Yılmaz (Sertifika No: KDU-01.12.05)"
            value={b1_3.yetkili_kisi || ''}
            onChange={(e) => updateSdsField(['b1_kimlik', 'b1_3', 'yetkili_kisi'], e.target.value)}
          />
        </div>

        <div className="form-group" style={{ gridColumn: 'span 2' }}>
          <label className="form-label">
            <span>Açık Adres</span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. Kimyacılar Organize Sanayi Bölgesi, Melek Aras Bulvarı No:12 Tuzla / İstanbul"
            value={b1_3.adres || ''}
            onChange={(e) => updateSdsField(['b1_kimlik', 'b1_3', 'adres'], e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Telefon Numarası</span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. +90 216 123 45 67"
            value={b1_3.telefon || ''}
            onChange={(e) => updateSdsField(['b1_kimlik', 'b1_3', 'telefon'], e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>GBF Sorumlusu E-Posta <span className="req-star">*</span></span>
          </label>
          <input
            type="email"
            className="form-control"
            placeholder="ör. sds@aypolkimya.com"
            value={b1_3.eposta || ''}
            onChange={(e) => updateSdsField(['b1_kimlik', 'b1_3', 'eposta'], e.target.value)}
          />
          <FieldHelper legalRef="md. 1.3" tooltip="GBF'den sorumlu yetkili kişinin e-posta adresi zorunludur." />
        </div>
      </div>

      {/* 1.4 Acil Durum Telefonu */}
      <div className="section-group-title">
        <span>1.4. Acil Durum Telefon Numarası</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>Acil Durum Telefon Numarası <span className="req-star">*</span></span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. 114 (UZEM) / +90 216 123 45 68"
            value={b1_4.acil_telefon || ''}
            onChange={(e) => updateSdsField(['b1_kimlik', 'b1_4', 'acil_telefon'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 1.4"
            onInsertText={(val) => updateSdsField(['b1_kimlik', 'b1_4', 'acil_telefon'], val)}
            templates={['114 (Ulusal Zehir Danışma Merkezi - UZEM)', '112 (Acil Çağrı Merkezi)']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Hizmet Kısıtlaması (Opsiyonel)</span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. 7/24 Kesintisiz veya Mesai saatleri içi (08:30 - 18:00)"
            value={b1_4.hizmet_kisitlamasi || ''}
            onChange={(e) => updateSdsField(['b1_kimlik', 'b1_4', 'hizmet_kisitlamasi'], e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}
