import React, { useState } from 'react';
import { useApp } from '../../../context/AppContext';
import { api } from '../../../api/client';
import FieldHelper from '../../Common/FieldHelper';
import { Truck, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Step14_Tasimacilik() {
  const { sdsData, updateSdsField, currentProduct } = useApp();
  const [calculating, setCalculating] = useState(false);
  const [calcRationale, setCalcRationale] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const b14 = sdsData?.b14_tasimacilik || {};

  const handleAutoCalculateTransport = async () => {
    setCalculating(true);
    setErrorMsg(null);
    try {
      const effectiveProductName = (
        currentProduct?.urun_adi ||
        sdsData?.b1_kimlik?.b1_1?.madde_karisim_adi ||
        sdsData?.b1_kimlik?.b1_1?.ticari_adi ||
        ''
      );

      const res = await api.calculateTransportPreview(
        sdsData || {},
        effectiveProductName
      );

      if (res) {
        updateSdsField(['b14_tasimacilik', 'b14_1_un_numarasi'], res.b14_1_un_numarasi || '');
        updateSdsField(['b14_tasimacilik', 'b14_2_un_tasimacilik_adi'], res.b14_2_un_tasimacilik_adi || '');
        updateSdsField(['b14_tasimacilik', 'b14_3_tasimacilik_sinifi'], res.b14_3_tasimacilik_sinifi || '');
        updateSdsField(['b14_tasimacilik', 'b14_4_ambalajlama_grubu'], res.b14_4_ambalajlama_grubu || '');
        updateSdsField(['b14_tasimacilik', 'b14_5_cevresel_zararlar'], res.b14_5_cevresel_zararlar || '');
        updateSdsField(['b14_tasimacilik', 'b14_6_kullanici_ozel_onlemler'], res.b14_6_kullanici_ozel_onlemler || '');
        setCalcRationale(res.aciklama || 'ADR kurallarına göre hesaplandı.');
      }
    } catch (err) {
      console.error('Taşımacılık hesaplama hatası:', err);
      setErrorMsg('Hesaplama sırasında bir hata oluştu: ' + (err.message || err));
    } finally {
      setCalculating(false);
    }
  };

  return (
    <div>
      <div className="section-group-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
        <span>14. Taşımacılık Bilgisi (ADR / RID / IMDG / IATA)</span>
        <button
          type="button"
          className="btn btn-primary btn-sm"
          onClick={handleAutoCalculateTransport}
          disabled={calculating}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          title="Bölüm 9 test verileri (Parlama/Kaynama Noktası) ve Bölüm 2 sınıflarından ADR/UN bilgilerini otomatik türet"
        >
          {calculating ? (
            <>
              <Sparkles size={14} className="spin-animate" /> Hesaplanıyor...
            </>
          ) : (
            <>
              <Truck size={14} /> Otomatik ADR / UN Sınıflandırması Hesapla
            </>
          )}
        </button>
      </div>

      {calcRationale && (
        <div
          style={{
            marginBottom: '16px',
            padding: '10px 14px',
            background: '#ecfdf5',
            border: '1px solid #a7f3d0',
            borderRadius: '6px',
            color: '#065f46',
            fontSize: '0.84rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <CheckCircle2 size={16} color="#059669" style={{ flexShrink: 0 }} />
          <div>
            <strong>ADR Karar Motoru Sonucu:</strong> {calcRationale}
          </div>
        </div>
      )}

      {errorMsg && (
        <div
          style={{
            marginBottom: '16px',
            padding: '10px 14px',
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '6px',
            color: '#991b1b',
            fontSize: '0.84rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <AlertCircle size={16} color="#dc2626" style={{ flexShrink: 0 }} />
          <div>{errorMsg}</div>
        </div>
      )}

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
