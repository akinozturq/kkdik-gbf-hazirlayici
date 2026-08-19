import React, { useState } from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';
import HPickerModal from '../../Common/HPickerModal';
import HazardCalculationModal from '../HazardCalculationModal';
import { api } from '../../../api/client';
import { Plus, Trash2, ShieldAlert, Sparkles, Check, X, Calculator, RefreshCw } from 'lucide-react';

export default function Step2_ZararTanimi() {
  const { sdsData, updateSdsField, pictograms } = useApp();
  const [isHPickerOpen, setIsHPickerOpen] = useState(false);
  const [isPPickerOpen, setIsPPickerOpen] = useState(false);
  const [isHazardModalOpen, setIsHazardModalOpen] = useState(false);
  const [derivingP, setDerivingP] = useState(false);

  const b2 = sdsData?.b2_zarar_tanimi || {};
  const b2_1 = b2.b2_1 || {};
  const b2_2 = b2.b2_2 || {};
  const b2_3 = b2.b2_3 || {};

  const siniflandirmalar = b2_1.siniflandirmalar || [];
  const seciliPiktogramlar = b2_2.piktogramlar || [];
  const hIfadeleri = b2_2.h_ifadeleri || [];
  const pIfadeleri = b2_2.p_ifadeleri || [];

  // Add Row to Classifications Table
  const addClassificationRow = () => {
    const updated = [
      ...siniflandirmalar,
      { zararlilik_sinifi: '', kategori: '', h_kodu: '' },
    ];
    updateSdsField(['b2_zarar_tanimi', 'b2_1', 'siniflandirmalar'], updated);
  };

  // Remove Row from Classifications Table
  const removeClassificationRow = (index) => {
    const updated = siniflandirmalar.filter((_, i) => i !== index);
    updateSdsField(['b2_zarar_tanimi', 'b2_1', 'siniflandirmalar'], updated);
  };

  // Update specific classification row field
  const updateClassificationRow = (index, field, value) => {
    const updated = [...siniflandirmalar];
    updated[index] = { ...updated[index], [field]: value };
    updateSdsField(['b2_zarar_tanimi', 'b2_1', 'siniflandirmalar'], updated);
  };

  // Toggle Pictogram
  const togglePictogram = (code) => {
    const exists = seciliPiktogramlar.includes(code);
    let updated;
    if (exists) {
      updated = seciliPiktogramlar.filter((c) => c !== code);
    } else {
      updated = [...seciliPiktogramlar, code];
    }
    updateSdsField(['b2_zarar_tanimi', 'b2_2', 'piktogramlar'], updated);
  };

  // Add H-Statement from Modal
  const handleSelectH = (item) => {
    if (!hIfadeleri.includes(item.code)) {
      updateSdsField(['b2_zarar_tanimi', 'b2_2', 'h_ifadeleri'], [...hIfadeleri, item.code]);
    }
  };

  const removeHCode = (code) => {
    updateSdsField(
      ['b2_zarar_tanimi', 'b2_2', 'h_ifadeleri'],
      hIfadeleri.filter((c) => c !== code)
    );
  };

  // Add P-Statement from Modal
  const handleSelectP = (item) => {
    if (!pIfadeleri.includes(item.code)) {
      updateSdsField(['b2_zarar_tanimi', 'b2_2', 'p_ifadeleri'], [...pIfadeleri, item.code]);
    }
  };

  const removePCode = (code) => {
    updateSdsField(
      ['b2_zarar_tanimi', 'b2_2', 'p_ifadeleri'],
      pIfadeleri.filter((c) => c !== code)
    );
  };

  // Quick derive P-statements from existing H-codes
  const handleDerivePFromH = async () => {
    if (hIfadeleri.length === 0) {
      alert('Lütfen önce en az bir H-ifadesi ekleyin veya Karışım Hesaplama Motorunu çalıştırın.');
      return;
    }
    setDerivingP(true);
    try {
      const res = await api.derivePFromH(hIfadeleri);
      if (res.p_codes && res.p_codes.length > 0) {
        updateSdsField(['b2_zarar_tanimi', 'b2_2', 'p_ifadeleri'], res.p_codes);
      }
    } catch (err) {
      alert('P-ifadeleri türetilirken hata: ' + err.message);
    } finally {
      setDerivingP(false);
    }
  };

  return (
    <div>
      {/* 2.1 Sınıflandırma */}
      <div className="section-group-title" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span>2.1. Maddenin veya Karışımın Sınıflandırılması</span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => setIsHazardModalOpen(true)}
            style={{
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
            title="Bölüm 3.2 bileşen konsantrasyonlarından SEA Ek-1 toplanabilirlik kurallarıyla otomatik hesapla"
          >
            <Calculator size={14} />
            ⚡ Karışım Tablosundan Hesapla
          </button>

          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={addClassificationRow}
            disabled={b2_1.siniflandirilmamis}
          >
            <Plus size={14} />
            Manuel Satır Ekle
          </button>
        </div>
      </div>

      <div style={{ marginBottom: '14px' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.9rem', fontWeight: 600 }}>
          <input
            type="checkbox"
            checked={b2_1.siniflandirilmamis || false}
            onChange={(e) => {
              const checked = e.target.checked;
              updateSdsField(['b2_zarar_tanimi', 'b2_1', 'siniflandirilmamis'], checked);
              if (checked) {
                updateSdsField(['b2_zarar_tanimi', 'b2_1', 'siniflandirmalar'], []);
              }
            }}
          />
          <span>Bu madde / karışım SEA Yönetmeliği kriterlerine göre zararlı olarak sınıflandırılmamıştır.</span>
        </label>
      </div>

      {b2_1.siniflandirilmamis ? (
        <div className="form-group">
          <label className="form-label">
            <span>Sınıflandırılmama Gerekçesi (Mevzuat Uyarınca Zorunlu) <span className="req-star">*</span></span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. SEA Yönetmeliği (RG: 28848) Ek-1 kriterlerine göre fiziksel, sağlık ve çevresel zararlılık sınırlarının altındadır."
            value={b2_1.siniflandirilmama_gerekcesi || ''}
            onChange={(e) => updateSdsField(['b2_zarar_tanimi', 'b2_1', 'siniflandirilmama_gerekcesi'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 2.1"
            onInsertText={(val) => updateSdsField(['b2_zarar_tanimi', 'b2_1', 'siniflandirilmama_gerekcesi'], val)}
            templates={['SEA Yönetmeliği kriterlerine göre tehlikeli/zararlı sınıflandırma eşik değerlerinin altındadır.']}
          />
        </div>
      ) : (
        <div style={{ marginBottom: '16px' }}>
          <table className="custom-table">
            <thead>
              <tr>
                <th style={{ width: '45%' }}>Zararlılık Sınıfı</th>
                <th style={{ width: '25%' }}>Kategori</th>
                <th style={{ width: '20%' }}>H-Kodu</th>
                <th style={{ width: '10%', textAlign: 'center' }}>Sil</th>
              </tr>
            </thead>
            <tbody>
              {siniflandirmalar.map((row, idx) => (
                <tr key={idx}>
                  <td>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="ör. Alevlenir Sıvılar"
                      value={row.zararlilik_sinifi || ''}
                      onChange={(e) => updateClassificationRow(idx, 'zararlilik_sinifi', e.target.value)}
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="ör. Kategori 2"
                      value={row.kategori || ''}
                      onChange={(e) => updateClassificationRow(idx, 'kategori', e.target.value)}
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="ör. H225"
                      value={row.h_kodu || ''}
                      onChange={(e) => updateClassificationRow(idx, 'h_kodu', e.target.value)}
                    />
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <button
                      type="button"
                      className="btn btn-danger btn-sm"
                      onClick={() => removeClassificationRow(idx)}
                    >
                      <Trash2 size={13} />
                    </button>
                  </td>
                </tr>
              ))}
              {siniflandirmalar.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', color: '#94a3b8', padding: '24px' }}>
                    Henüz sınıflandırma girilmedi. Yukarıdaki <b>"⚡ Karışım Tablosundan Hesapla"</b> butonunu kullanarak tek tıkla hesaplayabilirsiniz.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          <FieldHelper legalRef="KKDİK Ek-2 md. 2.1" tooltip="SEA Yönetmeliği sınıflandırma tablosu." />
        </div>
      )}

      {/* 2.2 Etiket Unsurları */}
      <div className="section-group-title">
        <span>2.2. Etiket Unsurları (GHS / SEA)</span>
      </div>

      {/* Piktogramlar */}
      <div className="form-group">
        <label className="form-label">
          <span>GHS Tehlike Piktogramları (Seçmek için tıklayınız)</span>
        </label>
        <div className="pictogram-selector-grid">
          {pictograms.map((pic) => {
            const isSelected = seciliPiktogramlar.includes(pic.code);
            const picCodeLower = pic.code.toLowerCase();
            return (
              <div
                key={pic.code}
                className={`pictogram-choice-card ${isSelected ? 'selected' : ''}`}
                onClick={() => togglePictogram(pic.code)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  padding: '12px 8px',
                  borderRadius: '10px',
                  border: isSelected ? '2px solid #2563eb' : '1px solid #e2e8f0',
                  background: isSelected ? '#eff6ff' : '#ffffff',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  boxShadow: isSelected ? '0 4px 10px rgba(37,99,235,0.15)' : 'none',
                }}
              >
                <div style={{ width: '64px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '8px' }}>
                  <img
                    src={`/pictograms/${picCodeLower}.svg`}
                    alt={pic.code}
                    style={{ width: '56px', height: '56px', objectFit: 'contain' }}
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = `/pictograms/${picCodeLower}.png`;
                    }}
                  />
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 800, color: isSelected ? '#1e40af' : '#0f172a' }}>
                  {pic.code}
                </div>
                <div style={{ fontSize: '0.78rem', fontWeight: 600, color: isSelected ? '#1d4ed8' : '#334155', textAlign: 'center', marginTop: '2px' }}>
                  {pic.name}
                </div>
                <div style={{ fontSize: '0.7rem', color: '#64748b', textAlign: 'center', marginTop: '2px' }}>
                  {pic.symbol}
                </div>
              </div>
            );
          })}
        </div>
        <FieldHelper legalRef="KKDİK Ek-2 md. 2.2" tooltip="Zararlılık sınıflandırmasına karşılık gelen piktogramlar seçilmelidir." />
      </div>

      {/* Uyarı Kelimesi */}
      <div className="form-group" style={{ marginTop: '16px' }}>
        <label className="form-label">
          <span>Uyarı Kelimesi (Signal Word)</span>
        </label>
        <div style={{ display: 'flex', gap: '12px' }}>
          {['Tehlike', 'Dikkat', 'Yok'].map((word) => (
            <label
              key={word}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                border: '1px solid',
                borderColor: b2_2.uyari_kelimesi === word ? '#2563eb' : '#cbd5e1',
                background: b2_2.uyari_kelimesi === word ? '#eff6ff' : '#ffffff',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 600,
                color: b2_2.uyari_kelimesi === word ? '#1e40af' : '#334155',
              }}
            >
              <input
                type="radio"
                name="uyari_kelimesi"
                value={word}
                checked={b2_2.uyari_kelimesi === word}
                onChange={(e) => updateSdsField(['b2_zarar_tanimi', 'b2_2', 'uyari_kelimesi'], e.target.value)}
              />
              <span>{word}</span>
            </label>
          ))}
        </div>
      </div>

      {/* H-İfadeleri */}
      <div className="form-group" style={{ marginTop: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
          <label className="form-label" style={{ margin: 0 }}>
            <span>Zararlılık İfadeleri (H-Kodları)</span>
          </label>
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={() => setIsHPickerOpen(true)}
          >
            <Plus size={13} />
            H-Kodu Seç / Ekle
          </button>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', minHeight: '38px', padding: '8px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
          {hIfadeleri.map((code) => (
            <span
              key={code}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                background: '#fee2e2',
                color: '#991b1b',
                borderRadius: '20px',
                fontSize: '0.82rem',
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
              }}
            >
              {code}
              <button
                type="button"
                onClick={() => removeHCode(code)}
                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#991b1b', display: 'flex' }}
              >
                <X size={13} />
              </button>
            </span>
          ))}
          {hIfadeleri.length === 0 && (
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', margin: 'auto 0' }}>
              Henüz H-ifadesi eklenmedi.
            </span>
          )}
        </div>
      </div>

      {/* P-İfadeleri */}
      <div className="form-group" style={{ marginTop: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
          <label className="form-label" style={{ margin: 0 }}>
            <span>Önlem İfadeleri (P-Kodları)</span>
          </label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={handleDerivePFromH}
              disabled={derivingP || hIfadeleri.length === 0}
              style={{ borderColor: '#93c5fd', color: '#1d4ed8', background: '#eff6ff', fontWeight: 600 }}
              title="Mevcut H-kodlarına karşılık gelen tüm SEA Ek-4 P-kodlarını otomatik türetir"
            >
              <Sparkles size={13} />
              {derivingP ? 'Türetiliyor...' : '⚡ H-Kodlarından P-Türet'}
            </button>

            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={() => setIsPPickerOpen(true)}
            >
              <Plus size={13} />
              Manuel P-Kodu Ekle
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', minHeight: '38px', padding: '8px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
          {pIfadeleri.map((code) => (
            <span
              key={code}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                background: '#e0f2fe',
                color: '#0369a1',
                borderRadius: '20px',
                fontSize: '0.82rem',
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
              }}
            >
              {code}
              <button
                type="button"
                onClick={() => removePCode(code)}
                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#0369a1', display: 'flex' }}
              >
                <X size={13} />
              </button>
            </span>
          ))}
          {pIfadeleri.length === 0 && (
            <span style={{ fontSize: '0.8rem', color: '#94a3b8', margin: 'auto 0' }}>
              Henüz P-ifadesi eklenmedi.
            </span>
          )}
        </div>
      </div>

      {/* 2.3 Diğer Zararlar */}
      <div className="section-group-title">
        <span>2.3. Diğer Zararlar</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label className="form-label">
            <span>PBT / vPvB Değerlendirme Sonuçları</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Karışım, KKDİK Ek-XIII kriterlerine göre PBT veya vPvB olarak değerlendirilen maddeler içermez."
            value={b2_3.pbt_vpvb_degerlendirme || ''}
            onChange={(e) => updateSdsField(['b2_zarar_tanimi', 'b2_3', 'pbt_vpvb_degerlendirme'], e.target.value)}
          />
          <FieldHelper
            legalRef="KKDİK Ek-2 md. 2.3"
            onInsertText={(val) => updateSdsField(['b2_zarar_tanimi', 'b2_3', 'pbt_vpvb_degerlendirme'], val)}
            templates={['PBT veya vPvB değerlendirmesi kapsamındaki kriterleri karşılamamaktadır.']}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            <span>Diğer Zararlar Açıklaması</span>
          </label>
          <textarea
            className="form-control"
            placeholder="ör. Buharları hava ile patlayıcı karışım oluşturabilir. Statik elektrik yükü birikebilir."
            value={b2_3.diger_zararlar_aciklama || ''}
            onChange={(e) => updateSdsField(['b2_zarar_tanimi', 'b2_3', 'diger_zararlar_aciklama'], e.target.value)}
          />
          <FieldHelper
            legalRef="md. 2.3"
            onInsertText={(val) => updateSdsField(['b2_zarar_tanimi', 'b2_3', 'diger_zararlar_aciklama'], val)}
            templates={['Bilinen başka bir zararı bulunmamaktadır.']}
          />
        </div>
      </div>

      {/* SEA Karışım Hesaplama Modalı */}
      <HazardCalculationModal
        isOpen={isHazardModalOpen}
        onClose={() => setIsHazardModalOpen(false)}
      />

      {/* Pickers */}
      <HPickerModal
        isOpen={isHPickerOpen}
        onClose={() => setIsHPickerOpen(false)}
        onSelect={handleSelectH}
        selectedCodes={hIfadeleri}
        mode="H"
      />

      <HPickerModal
        isOpen={isPPickerOpen}
        onClose={() => setIsPPickerOpen(false)}
        onSelect={handleSelectP}
        selectedCodes={pIfadeleri}
        mode="P"
      />
    </div>
  );
}
