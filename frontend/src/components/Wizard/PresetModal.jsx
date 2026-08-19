import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { SECTOR_PRESETS } from '../../data/sectorPresets';
import { X, Sparkles, Check, AlertCircle, Layers, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function PresetModal({ isOpen, onClose }) {
  const { sdsData, activeStep, applySectorPreset } = useApp();
  const [selectedPresetId, setSelectedPresetId] = useState('tiner');
  const [scope, setScope] = useState('all'); // 'all' | 'current'
  const [overwrite, setOverwrite] = useState(false); // false: fill blanks only, true: overwrite
  const [isSuccess, setIsSuccess] = useState(false);

  if (!isOpen) return null;

  const selectedPreset = SECTOR_PRESETS.find((p) => p.id === selectedPresetId) || SECTOR_PRESETS[0];

  const handleApply = async () => {
    await applySectorPreset(selectedPresetId, {
      scope,
      overwrite,
      targetStep: activeStep,
    });
    setIsSuccess(true);
    setTimeout(() => {
      setIsSuccess(false);
      onClose();
    }, 1200);
  };

  const getStepName = (step) => {
    const names = {
      1: 'Bölüm 1: Kimlik',
      2: 'Bölüm 2: Zararlılık Tanımı',
      3: 'Bölüm 3: Bileşim',
      4: 'Bölüm 4: İlk Yardım Önlemleri',
      5: 'Bölüm 5: Yangınla Mücadele',
      6: 'Bölüm 6: Kaza Sonucu Yayılma',
      7: 'Bölüm 7: Elleçleme ve Depolama',
      8: 'Bölüm 8: Maruz Kalma Kontrolleri / KKD',
      9: 'Bölüm 9: Fiziksel & Kimyasal',
      10: 'Bölüm 10: Kararlılık ve Tepkime',
      11: 'Bölüm 11: Toksikolojik Bilgiler',
      12: 'Bölüm 12: Ekolojik Bilgiler',
      13: 'Bölüm 13: Bertaraf Etme Bilgileri',
      14: 'Bölüm 14: Taşımacılık Bilgisi',
      15: 'Bölüm 15: Mevzuat Bilgisi',
      16: 'Bölüm 16: Diğer Bilgiler',
    };
    return names[step] || `Bölüm ${step}`;
  };

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 9999 }}>
      <div
        className="modal-content"
        style={{ maxWidth: '820px', width: '96%', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="modal-header" style={{ padding: '18px 24px', background: '#f8fafc' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 8px rgba(37,99,235,0.25)',
              }}
            >
              <Sparkles size={22} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#0f172a' }}>
                Sektörel GBF Şablonu Uygula
              </h3>
              <p style={{ margin: '2px 0 0', fontSize: '0.8rem', color: '#64748b' }}>
                Boya, tiner ve sertleştiriciler için KKDİK Ek-2 uyumlu hazır mevzuat metinleri
              </p>
            </div>
          </div>
          <button className="btn btn-secondary btn-icon" onClick={onClose} style={{ borderRadius: '8px' }}>
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body" style={{ padding: '20px 24px', overflowY: 'auto' }}>
          {/* Preset Cards Selection */}
          <div style={{ marginBottom: '18px' }}>
            <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 700, color: '#334155', marginBottom: '8px' }}>
              1. Ürün Kimyasal Türünü Seçin:
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
              {SECTOR_PRESETS.map((preset) => {
                const isSelected = selectedPresetId === preset.id;
                return (
                  <div
                    key={preset.id}
                    onClick={() => setSelectedPresetId(preset.id)}
                    style={{
                      border: isSelected ? '2px solid #2563eb' : '1px solid #e2e8f0',
                      background: isSelected ? '#eff6ff' : '#ffffff',
                      borderRadius: '10px',
                      padding: '14px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      boxShadow: isSelected ? '0 4px 12px rgba(37,99,235,0.12)' : 'none',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '1.4rem' }}>{preset.icon}</span>
                        <span style={{ fontWeight: 700, fontSize: '0.92rem', color: isSelected ? '#1e40af' : '#0f172a' }}>
                          {preset.name}
                        </span>
                      </div>
                      {isSelected && <CheckCircle2 size={18} color="#2563eb" />}
                    </div>

                    <p style={{ margin: 0, fontSize: '0.76rem', color: '#64748b', lineHeight: 1.35 }}>
                      {preset.description}
                    </p>

                    <div style={{ marginTop: '8px' }}>
                      <span
                        style={{
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '4px',
                          background: isSelected ? '#dbeafe' : '#f1f5f9',
                          color: isSelected ? '#1e40af' : '#475569',
                          display: 'inline-block',
                        }}
                      >
                        {preset.badge}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Scope & Overwrite Options */}
          <div
            style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '10px',
              padding: '16px',
              marginBottom: '18px',
            }}
          >
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#1e293b', marginBottom: '8px' }}>
                  2. Uygulama Kapsamı:
                </label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.84rem', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="presetScope"
                      checked={scope === 'all'}
                      onChange={() => setScope('all')}
                    />
                    <span>
                      <b>Tüm İlgili Bölümler</b> (4, 5, 6, 7, 8, 10, 13)
                    </span>
                  </label>

                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.84rem', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="presetScope"
                      checked={scope === 'current'}
                      onChange={() => setScope('current')}
                    />
                    <span>
                      Yalnızca <b>Şu Anki Bölüm</b> ({getStepName(activeStep)})
                    </span>
                  </label>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#1e293b', marginBottom: '8px' }}>
                  3. Alan Doldurma Modu:
                </label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.84rem', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="presetOverwrite"
                      checked={!overwrite}
                      onChange={() => setOverwrite(false)}
                    />
                    <span>
                      <b>Sadece Boş Alanları Doldur</b> (Mevcut metinleri koru)
                    </span>
                  </label>

                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.84rem', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="presetOverwrite"
                      checked={overwrite}
                      onChange={() => setOverwrite(true)}
                    />
                    <span>
                      <b>Tümünü Güncelle</b> (Mevcut metinlerin üzerine yaz)
                    </span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Preview */}
          <div style={{ border: '1px solid #e2e8f0', borderRadius: '10px', padding: '14px', background: '#ffffff' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <Layers size={15} color="#2563eb" />
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0f172a' }}>
                Seçilen Şablon İçerik Özeti ({selectedPreset.name}):
              </span>
            </div>

            <div style={{ fontSize: '0.78rem', color: '#334155', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div>
                <b style={{ color: '#0f172a' }}>Bölüm 4 (İlk Yardım - Yutma):</b>{' '}
                <span style={{ color: '#64748b' }}>
                  {selectedPreset.sections.b4_ilk_yardim.b4_1.yutma}
                </span>
              </div>
              <div>
                <b style={{ color: '#0f172a' }}>Bölüm 5 (Yangın Özel Zararlar):</b>{' '}
                <span style={{ color: '#64748b' }}>
                  {selectedPreset.sections.b5_yangin_mucadele.b5_2_ozel_zararlar}
                </span>
              </div>
              <div>
                <b style={{ color: '#0f172a' }}>Bölüm 7 (Saklama Koşulları):</b>{' '}
                <span style={{ color: '#64748b' }}>
                  {selectedPreset.sections.b7_ellecme_depolama.b7_2.guvenli_depolama_kosullari}
                </span>
              </div>
              <div>
                <b style={{ color: '#0f172a' }}>Bölüm 13 (Atık Bertaraf Kodu):</b>{' '}
                <span style={{ color: '#64748b' }}>
                  {selectedPreset.sections.b13_bertaraf.b13_1_atik_isleme_yontemleri}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer" style={{ padding: '16px 24px', background: '#f8fafc' }}>
          <div style={{ fontSize: '0.78rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '5px', marginRight: 'auto' }}>
            <AlertCircle size={14} color="#2563eb" />
            <span>Şablon uygulandıktan sonra metinleri dilediğiniz gibi düzenleyebilirsiniz.</span>
          </div>

          <button className="btn btn-secondary" onClick={onClose}>
            Vazgeç
          </button>
          <button
            className="btn btn-primary"
            onClick={handleApply}
            disabled={isSuccess}
            style={{
              background: isSuccess ? '#059669' : '#2563eb',
              borderColor: isSuccess ? '#047857' : '#1d4ed8',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            {isSuccess ? (
              <>
                <Check size={16} />
                Şablon Başarıyla Uygulandı!
              </>
            ) : (
              <>
                <Sparkles size={16} />
                Şablonu Forma Uygula
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
