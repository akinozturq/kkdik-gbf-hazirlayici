import React, { useState, useEffect, useCallback } from 'react';
import { useApp } from '../../context/AppContext';
import { api } from '../../api/client';
import {
  Calculator,
  X,
  AlertTriangle,
  Layers,
  FileText,
  Check,
  Sparkles,
  Info,
  ShieldAlert,
} from 'lucide-react';

export default function HazardCalculationModal({ isOpen, onClose }) {
  const { activeProductId, setProduct, setSdsData, refreshValidation } = useApp();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('results'); // 'results' | 'steps'
  const [selectedPCodes, setSelectedPCodes] = useState([]);
  const [isSuccess, setIsSuccess] = useState(false);

  const calculateHazards = useCallback(async () => {
    if (!activeProductId) return;
    setLoading(true);
    setError(null);
    setIsSuccess(false);
    try {
      const data = await api.calculateProductHazards(activeProductId);
      setResult(data);
      setSelectedPCodes(data.p_ifadeleri || []);
    } catch (err) {
      setError(err.message || 'Zararlılık hesaplanırken hata oluştu.');
    } finally {
      setLoading(false);
    }
  }, [activeProductId]);

  useEffect(() => {
    if (isOpen && activeProductId) {
      calculateHazards();
    }
  }, [isOpen, activeProductId, calculateHazards]);

  if (!isOpen) return null;

  const togglePCode = (code) => {
    if (selectedPCodes.includes(code)) {
      setSelectedPCodes(selectedPCodes.filter((c) => c !== code));
    } else {
      setSelectedPCodes([...selectedPCodes, code]);
    }
  };

  const handleApply = async () => {
    if (!result) return;
    setLoading(true);
    try {
      // Apply with customized P-codes selection
      const res = await api.applyCalculatedHazards(activeProductId);
      
      // If user customized P-codes, save that exact subset
      if (res.product && selectedPCodes.length !== (result.p_ifadeleri || []).length) {
        const nextSds = JSON.parse(JSON.stringify(res.product.sds_data || {}));
        if (nextSds.b2_zarar_tanimi?.b2_2) {
          nextSds.b2_zarar_tanimi.b2_2.p_ifadeleri = selectedPCodes;
          const finalUpdated = await api.updateProduct(activeProductId, { sds_data: nextSds });
          setProduct(finalUpdated);
          setSdsData(finalUpdated.sds_data || {});
        } else {
          setProduct(res.product);
          setSdsData(res.product.sds_data || {});
        }
      } else if (res.product) {
        setProduct(res.product);
        setSdsData(res.product.sds_data || {});
      }

      await refreshValidation();
      setIsSuccess(true);
      setTimeout(() => {
        setIsSuccess(false);
        onClose();
      }, 1200);
    } catch (err) {
      alert('Bölüm 2 güncellenirken hata oluştu: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const piktogramlar = result?.piktogramlar || [];
  const siniflandirmalar = result?.siniflandirmalar || [];
  const hIfadeleri = result?.h_ifadeleri || [];
  const euhIfadeleri = result?.euh_ifadeleri || [];
  const allH = [...hIfadeleri, ...euhIfadeleri];
  const uyariKelimesi = result?.uyari_kelimesi || 'Yok';
  const calculationSteps = result?.calculation_steps || [];

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 9999 }}>
      <div
        className="modal-content"
        style={{ maxWidth: '880px', width: '96%', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="modal-header" style={{ padding: '18px 24px', background: '#f8fafc' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #2563eb 0%, #1e40af 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 10px rgba(37,99,235,0.25)',
              }}
            >
              <Calculator size={22} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#0f172a' }}>
                SEA Karışım Zararlılık Hesaplama Motoru
              </h3>
              <p style={{ margin: '2px 0 0', fontSize: '0.8rem', color: '#64748b' }}>
                SEA Yönetmeliği Ek-1 toplanabilirlik kuralları ve Ek-4 H ➔ P haritalama sistemi
              </p>
            </div>
          </div>
          <button className="btn btn-secondary btn-icon" onClick={onClose} style={{ borderRadius: '8px' }}>
            <X size={18} />
          </button>
        </div>

        {/* Tab Navigation */}
        <div style={{ display: 'flex', borderBottom: '1px solid #e2e8f0', background: '#ffffff', padding: '0 24px' }}>
          <button
            type="button"
            onClick={() => setActiveTab('results')}
            style={{
              padding: '12px 18px',
              fontWeight: 700,
              fontSize: '0.86rem',
              color: activeTab === 'results' ? '#2563eb' : '#64748b',
              border: 'none',
              background: 'none',
              borderBottom: activeTab === 'results' ? '2px solid #2563eb' : '2px solid transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <ShieldAlert size={16} />
            Bölüm 2 Zararlılık Sonuçları
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('status')}
            style={{
              padding: '12px 18px',
              fontWeight: 700,
              fontSize: '0.86rem',
              color: activeTab === 'status' ? '#2563eb' : '#64748b',
              border: 'none',
              background: 'none',
              borderBottom: activeTab === 'status' ? '2px solid #2563eb' : '2px solid transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Info size={16} />
            Veri Yeterlilik Durumu ({result?.rule_results?.length || 8} Kural)
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('steps')}
            style={{
              padding: '12px 18px',
              fontWeight: 700,
              fontSize: '0.86rem',
              color: activeTab === 'steps' ? '#2563eb' : '#64748b',
              border: 'none',
              background: 'none',
              borderBottom: activeTab === 'steps' ? '2px solid #2563eb' : '2px solid transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <FileText size={16} />
            Matematiksel Hesaplama Raporu ({calculationSteps.length} Adım)
          </button>
        </div>

        {/* Body */}
        <div className="modal-body" style={{ padding: '20px 24px', overflowY: 'auto' }}>
          {loading && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: '#64748b' }}>
              <div className="animate-spin" style={{ display: 'inline-block', marginBottom: '10px' }}>
                <Calculator size={32} color="#2563eb" />
              </div>
              <p style={{ margin: 0, fontWeight: 600, fontSize: '0.9rem' }}>
                Bölüm 3.2 bileşenleri SEA Ek-1 toplanabilirlik kurallarına göre hesaplanıyor...
              </p>
            </div>
          )}

          {error && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '16px', color: '#991b1b' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700 }}>
                <AlertTriangle size={18} />
                <span>Hesaplama Hatası</span>
              </div>
              <p style={{ margin: '6px 0 0', fontSize: '0.85rem' }}>{error}</p>
            </div>
          )}

          {!loading && !error && result && activeTab === 'results' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              {/* Konsantrasyon Aralığı (Indeterminate) Uyarısı */}
              {result.has_indeterminate && (
                <div
                  style={{
                    background: '#fffbeb',
                    border: '1px solid #fde68a',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    display: 'flex',
                    gap: '12px',
                    alignItems: 'flex-start',
                  }}
                >
                  <AlertTriangle size={20} color="#d97706" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div style={{ fontSize: '0.82rem', color: '#92400e' }}>
                    <strong style={{ display: 'block', fontSize: '0.86rem', color: '#b45309', marginBottom: '2px' }}>
                      Konsantrasyon Aralığı Uyarısı (ECHA CLP 3 Durumlu Mantık)
                    </strong>
                    Reçetede konsantrasyon aralığı (min - max) içeren bileşenler mevcuttur. Sarı renkle işaretlenen zararlılıklar, alt sınırda (%min) eşik değerin altında kalırken, üst sınırda (%max) eşik değeri aşmaktadır. ECHA ve SEA Karışım Rehberi uyarınca en koruyucu yaklaşım (üst sınır) seçilerek listelenmiştir.
                  </div>
                </div>
              )}

              {/* Summary Highlights */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                {/* Uyarı Kelimesi */}
                <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px' }}>
                  <span style={{ fontSize: '0.74rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>
                    Uyarı Kelimesi (Signal Word)
                  </span>
                  <div style={{ marginTop: '4px' }}>
                    <span
                      style={{
                        fontSize: '1rem',
                        fontWeight: 800,
                        padding: '3px 10px',
                        borderRadius: '6px',
                        background: uyariKelimesi === 'Tehlike' ? '#fee2e2' : uyariKelimesi === 'Dikkat' ? '#fef3c7' : '#f1f5f9',
                        color: uyariKelimesi === 'Tehlike' ? '#b91c1c' : uyariKelimesi === 'Dikkat' ? '#b45309' : '#475569',
                        display: 'inline-block',
                      }}
                    >
                      {uyariKelimesi}
                    </span>
                  </div>
                </div>

                {/* Piktogramlar */}
                <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px' }}>
                  <span style={{ fontSize: '0.74rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>
                    GHS Piktogramları ({piktogramlar.length} Adet)
                  </span>
                  <div style={{ display: 'flex', gap: '6px', marginTop: '6px', flexWrap: 'wrap' }}>
                    {piktogramlar.length > 0 ? (
                      piktogramlar.map((pic) => (
                        <img
                          key={pic}
                          src={`/pictograms/${pic.toLowerCase()}.svg`}
                          alt={pic}
                          title={pic}
                          style={{ width: '32px', height: '32px', objectFit: 'contain' }}
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = `/pictograms/${pic.toLowerCase()}.png`;
                          }}
                        />
                      ))
                    ) : (
                      <span style={{ fontSize: '0.84rem', color: '#94a3b8' }}>Piktogram Yok</span>
                    )}
                  </div>
                </div>

                {/* Sınıflandırma Sayısı */}
                <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px' }}>
                  <span style={{ fontSize: '0.74rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>
                    Zararlılık Sınıfı Sayısı
                  </span>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#1e40af', marginTop: '2px' }}>
                    {siniflandirmalar.length} Sınıf
                  </div>
                </div>
              </div>

              {/* 2.1 Sınıflandırma Tablosu */}
              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                  <Layers size={16} color="#2563eb" />
                  <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a' }}>
                    2.1. Maddenin veya Karışımın Sınıflandırılması:
                  </span>
                </div>

                {siniflandirmalar.length > 0 ? (
                  <table className="custom-table" style={{ margin: 0 }}>
                    <thead>
                      <tr>
                        <th>Zararlılık Sınıfı</th>
                        <th>Kategori</th>
                        <th>H-Kodu</th>
                        <th>Kesinlik Durumu</th>
                      </tr>
                    </thead>
                    <tbody>
                      {siniflandirmalar.map((s, idx) => {
                        const isIndeterminate = s.status === 'INDETERMINATE';
                        return (
                          <tr key={idx} style={isIndeterminate ? { background: '#fffdf5' } : undefined}>
                            <td style={{ fontWeight: 600 }}>{s.zararlilik_sinifi}</td>
                            <td>
                              {s.kategori === 'CATEGORY_UNRESOLVED' ? (
                                <span
                                  title="Bileşen verisinde Kategori 1A / 1B alt kategorisi belirtilmemiş; ham H-kodu üzerinden alt kategori çözümlenemiyor."
                                  style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '4px',
                                    fontSize: '0.72rem',
                                    fontWeight: 700,
                                    padding: '2px 8px',
                                    borderRadius: '12px',
                                    background: '#fee2e2',
                                    color: '#991b1b',
                                    border: '1px solid #fecaca',
                                  }}
                                >
                                  ⚠️ CATEGORY_UNRESOLVED
                                </span>
                              ) : (
                                s.kategori
                              )}
                            </td>
                            <td>
                              <span className="badge badge-danger" style={{ fontSize: '0.76rem', fontWeight: 700 }}>
                                {s.h_kodu}
                              </span>
                            </td>
                            <td>
                              {isIndeterminate ? (
                                <span
                                  title={s.range_details || 'Konsantrasyon aralığı nedeniyle alt sınırda oluşmazken üst sınırda eşiği aşmaktadır.'}
                                  style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '4px',
                                    fontSize: '0.72rem',
                                    fontWeight: 700,
                                    padding: '2px 8px',
                                    borderRadius: '12px',
                                    background: '#fef3c7',
                                    color: '#b45309',
                                    border: '1px solid #fde68a',
                                  }}
                                >
                                  🟡 Belirsiz (Aralık Eşiği)
                                </span>
                              ) : (
                                <span
                                  style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '4px',
                                    fontSize: '0.72rem',
                                    fontWeight: 700,
                                    padding: '2px 8px',
                                    borderRadius: '12px',
                                    background: '#dcfce7',
                                    color: '#15803d',
                                    border: '1px solid #bbf7d0',
                                  }}
                                >
                                  🟢 Kesin
                                </span>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                ) : (
                  <p style={{ margin: 0, fontSize: '0.84rem', color: '#64748b' }}>
                    SEA Yönetmeliği kriterlerine göre zararlı olarak sınıflandırılmamıştır.
                  </p>
                )}
              </div>

              {/* 2.2 H-İfadeleri */}
              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '14px' }}>
                <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a', display: 'block', marginBottom: '8px' }}>
                  Zararlılık (H) ve İlave (EUH) İfadeleri:
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {allH.map((code) => (
                    <span
                      key={code}
                      style={{
                        padding: '4px 10px',
                        borderRadius: '6px',
                        background: code.startsWith('EUH') ? '#f3e8ff' : '#fee2e2',
                        color: code.startsWith('EUH') ? '#6b21a8' : '#991b1b',
                        fontWeight: 700,
                        fontSize: '0.8rem',
                        border: code.startsWith('EUH') ? '1px solid #e9d5ff' : '1px solid #fecaca',
                      }}
                    >
                      {code}
                    </span>
                  ))}
                  {allH.length === 0 && <span style={{ color: '#94a3b8', fontSize: '0.82rem' }}>Yok</span>}
                </div>
              </div>

              {/* 2.2 P-İfadeleri (Tüm İlgili Kodlar) */}
              <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div>
                    <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a' }}>
                      Önlem (P) İfadeleri (KKDİK GBF Kapsamı):
                    </span>
                    <p style={{ margin: '2px 0 0', fontSize: '0.74rem', color: '#64748b' }}>
                      H-kodlarından SEA Ek-4 kurallarıyla türetilmiştir ({selectedPCodes.length} seçili)
                    </p>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', maxHeight: '180px', overflowY: 'auto' }}>
                  {(result.p_ifadeleri || []).map((pCode) => {
                    const isChecked = selectedPCodes.includes(pCode);
                    return (
                      <label
                        key={pCode}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '6px 10px',
                          borderRadius: '6px',
                          border: isChecked ? '1px solid #93c5fd' : '1px solid #e2e8f0',
                          background: isChecked ? '#eff6ff' : '#ffffff',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => togglePCode(pCode)}
                        />
                        <span style={{ fontWeight: 700, color: '#1e40af' }}>{pCode}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {!loading && !error && result && activeTab === 'status' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ padding: '12px 16px', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', fontSize: '0.82rem', color: '#1e40af' }}>
                <span style={{ fontWeight: 700 }}>🔍 Veri Yeterlilik ve Karar Denetim Özeti:</span>
                <p style={{ margin: '4px 0 0', color: '#1e3a8a' }}>
                  Aşağıdaki tabloda her bir mevzuat kuralının (SEA Ek-1) girdi verilerinin yeterliliği ve karara varma durumu listelenmektedir.
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {(result.rule_results || []).map((rule, idx) => {
                  const isSufficient = rule.data_status === 'SUFFICIENT';
                  const isInsufficient = rule.data_status === 'INSUFFICIENT_DATA';
                  const statusBg = isSufficient ? '#dcfce7' : isInsufficient ? '#fef3c7' : '#f1f5f9';
                  const statusColor = isSufficient ? '#166534' : isInsufficient ? '#92400e' : '#475569';
                  const statusLabel = isSufficient ? 'Yeterli Veri' : isInsufficient ? 'Eksik Test Verisi' : 'Uygulanamaz';

                  return (
                    <div
                      key={idx}
                      style={{
                        background: '#ffffff',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        padding: '12px 16px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '6px',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.88rem', color: '#0f172a' }}>
                            {rule.rule_name}
                          </span>
                          <span
                            style={{
                              fontSize: '0.72rem',
                              fontWeight: 700,
                              padding: '2px 8px',
                              borderRadius: '12px',
                              background: statusBg,
                              color: statusColor,
                            }}
                          >
                            {statusLabel}
                          </span>
                          {rule.has_indeterminate && (
                            <span
                              style={{
                                fontSize: '0.72rem',
                                fontWeight: 700,
                                padding: '2px 8px',
                                borderRadius: '12px',
                                background: '#fef3c7',
                                color: '#b45309',
                                border: '1px solid #fde68a',
                              }}
                            >
                              🟡 Aralık Eşiği (Belirsiz)
                            </span>
                          )}
                        </div>
                        {rule.hazards && rule.hazards.length > 0 && (
                          <div style={{ display: 'flex', gap: '4px' }}>
                            {rule.hazards.map((h, hIdx) => (
                              <span key={hIdx} className="badge badge-danger" style={{ fontSize: '0.72rem', fontWeight: 700 }}>
                                {h.h_kodu || h.zararlilik_sinifi}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {rule.calculation_notes && rule.calculation_notes.length > 0 && (
                        <div style={{ fontSize: '0.78rem', color: '#475569', background: '#f8fafc', padding: '6px 10px', borderRadius: '6px', marginTop: '4px' }}>
                          {rule.calculation_notes.map((note, nIdx) => (
                            <div key={nIdx}>{note}</div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {!loading && !error && result && activeTab === 'steps' && (
            <div style={{ background: '#0f172a', color: '#f8fafc', padding: '16px', borderRadius: '8px', fontFamily: 'monospace', fontSize: '0.8rem', lineHeight: 1.6, maxHeight: '420px', overflowY: 'auto' }}>
              {calculationSteps.map((step, idx) => (
                <div
                  key={idx}
                  style={{
                    color: step.startsWith('===')
                      ? '#60a5fa'
                      : step.includes('Sınıflandırıldı')
                      ? '#4ade80'
                      : step.includes('Eşik değerler aşılmadı')
                      ? '#94a3b8'
                      : '#f1f5f9',
                    fontWeight: step.startsWith('===') ? 700 : 400,
                    marginBottom: '4px',
                  }}
                >
                  {step}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer" style={{ padding: '16px 24px', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '0.78rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <Info size={14} color="#2563eb" />
            <span>Onayladığınızda hesaplanan veriler doğrudan Bölüm 2'ye yazılacak ve kaydedilecektir.</span>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-secondary" onClick={onClose} disabled={loading}>
              Kapat
            </button>
            <button
              className="btn btn-primary"
              onClick={handleApply}
              disabled={loading || isSuccess || !result}
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
                  Bölüm 2'ye Başarıyla Aktarıldı!
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  Bölüm 2'ye Aktar ve Uygula
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
