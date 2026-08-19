import React, { useState } from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';
import ExposureLimitPickerModal from '../../Common/ExposureLimitPickerModal';
import { api } from '../../../api/client';
import { Plus, Trash2, Sparkles, FileSpreadsheet, Layers } from 'lucide-react';

export default function Step8_MaruzKalma() {
  const { sdsData, updateSdsField, activeProductId } = useApp();
  const [isPickerOpen, setIsPickerOpen] = useState(false);
  const [isAutoFilling, setIsAutoFilling] = useState(false);

  const b8 = sdsData?.b8_maruz_kalma_kontrolu || {};
  const b8_1 = b8.b8_1_kontrol_parametreleri || [];
  const b8_2 = b8.b8_2 || {};
  const kkd = b8_2.kkd || {};

  // Add Exposure Param Row
  const addExposureRow = () => {
    const updated = [
      ...b8_1,
      { madde: '', sinir_degeri: '', birim: 'mg/m³ / ppm', yasal_dayanak: '' },
    ];
    updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_1_kontrol_parametreleri'], updated);
  };

  const removeExposureRow = (index) => {
    const updated = b8_1.filter((_, i) => i !== index);
    updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_1_kontrol_parametreleri'], updated);
  };

  const updateExposureRow = (index, field, value) => {
    const updated = [...b8_1];
    updated[index] = { ...updated[index], [field]: value };
    updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_1_kontrol_parametreleri'], updated);
  };

  // Auto-fill from Section 3 components
  const handleAutoFill = async () => {
    if (!activeProductId) return;
    setIsAutoFilling(true);
    try {
      const res = await api.autoFillExposureLimits(activeProductId, true);
      if (res.matched_limits && res.matched_limits.length > 0) {
        updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_1_kontrol_parametreleri'], res.matched_limits);
      } else {
        alert('Bölüm 3 bileşenleri taranmış ancak Yönetmelik Ek-1 tablosunda kayıtlı sınır değer bulunamamıştır (veya bileşen girilmemiş).');
      }
    } catch (err) {
      alert('Otomatik maruziyet limitleri doldurulurken hata: ' + err.message);
    } finally {
      setIsAutoFilling(false);
    }
  };

  // Handle selection from ExposureLimitPickerModal
  const handleSelectLimit = (item) => {
    const twaParts = [];
    if (item.twa_ppm) twaParts.push(`${item.twa_ppm} ppm`);
    if (item.twa_mg_m3) twaParts.push(`${item.twa_mg_m3} mg/m³`);
    const twaStr = twaParts.length > 0 ? `TWA (8 Saat): ${twaParts.join(' / ')}` : '';

    const stelParts = [];
    if (item.stel_ppm) stelParts.push(`${item.stel_ppm} ppm`);
    if (item.stel_mg_m3) stelParts.push(`${item.stel_mg_m3} mg/m³`);
    const stelStr = stelParts.length > 0 ? `STEL (15 Dak.): ${stelParts.join(' / ')}` : '';

    const ceilingParts = [];
    if (item.ceiling_ppm) ceilingParts.push(`${item.ceiling_ppm} ppm`);
    if (item.ceiling_mg_m3) ceilingParts.push(`${item.ceiling_mg_m3} mg/m³`);
    const ceilingStr = ceilingParts.length > 0 ? `Tavan Değer: ${ceilingParts.join(' / ')}` : '';

    const notesStr = item.notes ? `[${item.notes}]` : '';
    const sinirDegeri = [twaStr, stelStr, ceilingStr, notesStr].filter(Boolean).join(' | ');

    let maddeLabel = item.name;
    const idInfo = [];
    if (item.cas) idInfo.push(`CAS: ${item.cas}`);
    if (item.einecs) idInfo.push(`EC: ${item.einecs}`);
    if (idInfo.length > 0) maddeLabel += ` (${idInfo.join(', ')})`;

    const newRow = {
      madde: maddeLabel,
      sinir_degeri: sinirDegeri || 'Mevzuatta sınır değer belirlenmiştir.',
      birim: 'mg/m³ / ppm',
      yasal_dayanak: item.yasal_dayanak || 'Kimyasal Maddelerle Çalışmalarda Sağlık ve Güvenlik Önlemleri Hakkında Yönetmelik (Ek-1)',
    };

    updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_1_kontrol_parametreleri'], [...b8_1, newRow]);
    setIsPickerOpen(false);
  };

  return (
    <div>
      {/* 8.1 Kontrol Parametreleri */}
      <div className="section-group-title" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
        <span>8.1. Kontrol Parametreleri (Mesleki Maruziyet Sınır Değerleri)</span>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={handleAutoFill}
            disabled={isAutoFilling}
            style={{
              background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
            title="Bölüm 3'teki bileşenleri İSG Yönetmeliği Ek-1 Mesleki Maruziyet Sınır Değerleri tablosuyla eşleştirip otomatik aktarır"
          >
            <Sparkles size={14} />
            {isAutoFilling ? 'Taranıyor...' : '⚡ Bölüm 3.2 Karışımından Otomatik Getir'}
          </button>

          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={() => setIsPickerOpen(true)}
            style={{ borderColor: '#059669', color: '#059669', fontWeight: 600 }}
          >
            <FileSpreadsheet size={14} />
            Kütüphaneden Ara & Ekle
          </button>

          <button type="button" className="btn btn-outline btn-sm" onClick={addExposureRow}>
            <Plus size={14} />
            Manuel Satır Ekle
          </button>
        </div>
      </div>

      <div style={{ overflowX: 'auto', marginBottom: '16px' }}>
        <table className="custom-table">
          <thead>
            <tr>
              <th style={{ width: '35%' }}>Madde / Bileşen</th>
              <th style={{ width: '40%' }}>Mesleki Maruziyet Sınır Değeri (TWA / STEL / Not)</th>
              <th style={{ width: '20%' }}>Yasal Dayanak / Standart</th>
              <th style={{ width: '5%', textAlign: 'center' }}>Sil</th>
            </tr>
          </thead>
          <tbody>
            {b8_1.map((row, idx) => (
              <tr key={idx}>
                <td>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="ör. Ksilen (CAS: 1330-20-7)"
                    value={row.madde || ''}
                    onChange={(e) => updateExposureRow(idx, 'madde', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="ör. TWA (8 Saat): 50 ppm / 221 mg/m³ | STEL (15 Dak.): 100 ppm / 442 mg/m³ [Deri]"
                    value={row.sinir_degeri || ''}
                    onChange={(e) => updateExposureRow(idx, 'sinir_degeri', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Kimyasal Maddelerle Çalışmalarda Sağlık ve Güvenlik Önlemleri Hakkında Yönetmelik"
                    value={row.yasal_dayanak || ''}
                    onChange={(e) => updateExposureRow(idx, 'yasal_dayanak', e.target.value)}
                  />
                </td>
                <td style={{ textAlign: 'center' }}>
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    onClick={() => removeExposureRow(idx)}
                  >
                    <Trash2 size={13} />
                  </button>
                </td>
              </tr>
            ))}
            {b8_1.length === 0 && (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', color: '#94a3b8', padding: '24px' }}>
                  Henüz sınır değer girilmedi. Yukarıdaki <b>"⚡ Bölüm 3.2 Karışımından Otomatik Getir"</b> butonuna basarak formülasyondaki solvent ve kimyasalların sınır değerlerini tek tıkla çekebilirsiniz.
                </td>
              </tr>
            )}
          </tbody>
        </table>
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 8.1"
          tooltip="Bölüm 3'te listelenen maddelerin ulusal mesleki maruziyet sınır değerleri belirtilmelidir."
        />
      </div>

      {/* 8.2 Maruz Kalma Kontrolleri */}
      <div className="section-group-title">
        <span>8.2. Maruz Kalma Kontrolleri</span>
      </div>

      {/* Mühendislik Kontrolleri */}
      <div className="form-group">
        <label className="form-label">
          <span>8.2.1. Uygun Mühendislik Kontrolleri <span className="req-star">*</span></span>
        </label>
        <textarea
          className="form-control"
          placeholder="ör. Yeterli genel ve yerel emişli havalandırma sağlayın. Patlamaya dayanıklı (Ex-proof) havalandırma ekipmanı kullanın. Çalışma alanında acil göz yıkama çeşmesi ve güvenlik duşu bulundurun."
          value={b8_2.muhendislik_kontrolleri || ''}
          onChange={(e) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'muhendislik_kontrolleri'], e.target.value)}
        />
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 8.2.1"
          onInsertText={(val) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'muhendislik_kontrolleri'], val)}
          templates={[
            'Yeterli genel ve yerel emişli havalandırma sağlanmalıdır. Patlamaya dayanıklı (Ex-proof) havalandırma sistemleri kullanılmalı, çalışma ortamında acil göz duşu bulundurulmalıdır.',
          ]}
        />
      </div>

      {/* 8.2.2 Kişisel Koruyucu Donanım (KKD) */}
      <div className="section-group-title" style={{ marginTop: '20px', fontSize: '0.95rem' }}>
        <span>8.2.2. Bireysel Koruyucu Önlemler (Kişisel Koruyucu Donanım - KKD)</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>a) Göz / Yüz Koruması <span className="req-star">*</span></span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. EN 166 standardına uygun tam oturan kimyasal koruyucu gözlük veya yüz siperi."
            value={kkd.goz_yuz || ''}
            onChange={(e) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'goz_yuz'], e.target.value)}
          />
          <FieldHelper
            legalRef="md. 8.2.2.a"
            onInsertText={(val) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'goz_yuz'], val)}
            templates={['EN 166 standardına uygun yan siperlikli koruyucu gözlük veya tam yüz koruyucu siperlik kullanılmalıdır.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>b) Cilt / El Koruması <span className="req-star">*</span></span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. EN 374 standardına uygun nitril veya bütil kauçuk kimyasal koruyucu eldiven (Geçirgenlik süresi > 480 dk)."
            value={kkd.cilt_el || ''}
            onChange={(e) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'cilt_el'], e.target.value)}
          />
          <FieldHelper
            legalRef="md. 8.2.2.b"
            onInsertText={(val) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'cilt_el'], val)}
            templates={['EN 374 standardına uygun çözücülere dayanıklı nitril veya bütil kauçuk koruyucu eldivenler tercih edilmelidir.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>b) Cilt / Vücut Diğer Koruma <span className="req-star">*</span></span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. Antistatik, kimyasal sıçramalara dayanıklı koruyucu iş elbisesi ve antistatik tabanlı güvenlik ayakkabısı."
            value={kkd.cilt_diger || ''}
            onChange={(e) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'cilt_diger'], e.target.value)}
          />
          <FieldHelper
            legalRef="md. 8.2.2.b"
            onInsertText={(val) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'cilt_diger'], val)}
            templates={['Antistatik özellikli, kimyasallara dayanıklı koruyucu önlük/elbise ve EN ISO 20345 güvenlik ayakkabısı giyilmelidir.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>c) Solunum Koruması <span className="req-star">*</span></span>
          </label>
          <input
            type="text"
            className="form-control"
            placeholder="ör. Yetersiz havalandırmada veya maruziyet sınırları aşıldığında EN 14387 uyumlu A2-P2 kombine filtreli solunum maskesi."
            value={kkd.solunum || ''}
            onChange={(e) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'solunum'], e.target.value)}
          />
          <FieldHelper
            legalRef="md. 8.2.2.c"
            onInsertText={(val) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'solunum'], val)}
            templates={['Yetersiz havalandırmada veya sprey uygulamasında EN 14387 standardına uygun A-P2 filtreli yarım/tam yüz maskesi kullanılmalıdır.']}
          />
        </div>
      </div>

      <div className="form-group" style={{ marginTop: '16px' }}>
        <label className="form-label">
          <span>d) Isıl Zararlar</span>
        </label>
        <input
          type="text"
          className="form-control"
          placeholder="ör. Normal kullanım koşullarında ısıl zarar beklenmez / Sıcak ürün elleçlenirken ısıya dayanıklı eldiven kullanın."
          value={kkd.isil || ''}
          onChange={(e) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'isil'], e.target.value)}
        />
        <FieldHelper
          legalRef="md. 8.2.2.d"
          onInsertText={(val) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'isil'], val)}
          templates={['Normal kullanım ve depolama koşullarında ısıl zarar oluşturmaz.']}
        />
      </div>

      {/* 8.2.3 Çevresel Maruz Kalma */}
      <div className="form-group" style={{ marginTop: '16px' }}>
        <label className="form-label">
          <span>8.2.3. Çevresel Maruz Kalma Kontrolleri <span className="req-star">*</span></span>
        </label>
        <textarea
          className="form-control"
          placeholder="ör. Ürünün kanalizasyona, yüzey sularına veya toprağa karışmasını önleyin. Havalandırma ve proses ekipmanlarından kaynaklanan emisyonlar çevre koruma mevzuatına uygun olmalıdır."
          value={b8_2.cevresel_kontroller || ''}
          onChange={(e) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'cevresel_kontroller'], e.target.value)}
        />
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 8.2.3"
          onInsertText={(val) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'cevresel_kontroller'], val)}
          templates={[
            'Kanalizasyona, su kaynaklarına veya toprağa deşarj edilmesini önleyin. Havalandırma bacalarından çıkan emisyonların Çevre Kanunu sınırlarına uygunluğu kontrol edilmelidir.',
          ]}
        />
      </div>

      {/* Exposure Limit Picker Modal */}
      <ExposureLimitPickerModal
        isOpen={isPickerOpen}
        onClose={() => setIsPickerOpen(false)}
        onSelect={handleSelectLimit}
        existingItems={b8_1}
      />
    </div>
  );
}
