import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { Search, X, Plus, Package, FlaskConical, AlertTriangle, ShieldCheck, Flame, Info, Check } from 'lucide-react';

export default function RawMaterialPickerModal({ isOpen, onClose, onSelect }) {
  const [materials, setMaterials] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedItemDetail, setSelectedItemDetail] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadMaterials();
    }
  }, [isOpen]);

  const loadMaterials = async (search = null) => {
    setLoading(true);
    try {
      const data = await api.getRawMaterials(search);
      setMaterials(data);
    } catch (err) {
      console.error('Hammadde kütüphanesi yüklenemedi:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearchTerm(val);
    loadMaterials(val);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 9999 }}>
      <div
        className="modal-content"
        style={{ maxWidth: '880px', width: '95%', maxHeight: '88vh', display: 'flex', flexDirection: 'column' }}
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
                background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 10px rgba(2,132,199,0.25)',
              }}
            >
              <Package size={22} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#0f172a' }}>
                Hammadde Kütüphanesi
              </h3>
              <p style={{ margin: '2px 0 0', fontSize: '0.8rem', color: '#64748b' }}>
                Formülasyon ve GBF hazırlamada kullanılacak standart onaylı kimyasal hammaddeler
              </p>
            </div>
          </div>
          <button className="btn btn-secondary btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Search */}
        <div style={{ padding: '14px 24px', borderBottom: '1px solid #e2e8f0', background: '#ffffff' }}>
          <div style={{ position: 'relative' }}>
            <Search
              size={18}
              style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }}
            />
            <input
              type="text"
              className="form-control"
              style={{ paddingLeft: '38px', fontSize: '0.88rem' }}
              placeholder="Hammadde adı, ticari kod veya CAS numarası ile ara... (ör. Aseton, Toluen, 108-88-3)"
              value={searchTerm}
              onChange={handleSearchChange}
              autoFocus
            />
          </div>
        </div>

        {/* Body - Cards */}
        <div className="modal-body" style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>Yükleniyor...</div>
          ) : materials.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>Aramanıza uygun hammadde bulunamadı.</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {materials.map((mat) => (
                <div
                  key={mat.id}
                  style={{
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    padding: '18px',
                    background: '#ffffff',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {/* Top Row: Name & Action */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <h4 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800, color: '#0f172a' }}>
                          {mat.ad}
                        </h4>
                        <span
                          style={{
                            padding: '2px 8px',
                            borderRadius: '4px',
                            background: '#e0f2fe',
                            color: '#0369a1',
                            fontSize: '0.74rem',
                            fontWeight: 700,
                          }}
                        >
                          {mat.kategori}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '3px' }}>
                        <b>IUPAC:</b> {mat.iupac_adi} | <b>Ticari:</b> {mat.ticari_ad}
                      </div>
                    </div>

                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={() => onSelect(mat)}
                      style={{
                        background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontWeight: 700,
                        padding: '8px 16px',
                      }}
                    >
                      <Plus size={16} />
                      Karışıma Ekle (Bölüm 3.2)
                    </button>
                  </div>

                  {/* Identification Grid */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(4, 1fr)',
                      gap: '8px',
                      padding: '10px',
                      background: '#f8fafc',
                      borderRadius: '8px',
                      marginBottom: '12px',
                      fontSize: '0.78rem',
                    }}
                  >
                    <div>
                      <span style={{ color: '#64748b', display: 'block' }}>CAS No:</span>
                      <b style={{ color: '#0f172a', fontFamily: 'monospace' }}>{mat.cas_no}</b>
                    </div>
                    <div>
                      <span style={{ color: '#64748b', display: 'block' }}>EC No:</span>
                      <b style={{ color: '#0f172a', fontFamily: 'monospace' }}>{mat.ec_no}</b>
                    </div>
                    <div>
                      <span style={{ color: '#64748b', display: 'block' }}>KKDİK / REACH Kayıt:</span>
                      <b style={{ color: '#0f172a', fontFamily: 'monospace' }}>{mat.kayit_no}</b>
                    </div>
                    <div>
                      <span style={{ color: '#64748b', display: 'block' }}>Formül / Mol. Ağırlık:</span>
                      <b style={{ color: '#0f172a' }}>{mat.molekul_formulu} ({mat.molekul_agirligi})</b>
                    </div>
                  </div>

                  {/* SEA Classification & Pictograms */}
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#475569' }}>
                        SEA Sınıflandırması:
                      </span>
                      <span
                        style={{
                          padding: '3px 8px',
                          borderRadius: '6px',
                          background: '#fee2e2',
                          color: '#991b1b',
                          fontSize: '0.78rem',
                          fontWeight: 700,
                        }}
                      >
                        {mat.uyari_kelimesi}
                      </span>
                      <span style={{ fontSize: '0.8rem', color: '#1e293b', fontWeight: 600 }}>
                        {mat.siniflandirma_str}
                      </span>
                    </div>

                    <div style={{ display: 'flex', gap: '6px', marginTop: '8px', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.74rem', color: '#64748b', marginRight: '4px' }}>Piktogramlar:</span>
                      {mat.piktogramlar.map((pic) => (
                        <img
                          key={pic}
                          src={`/pictograms/${pic.toLowerCase()}.svg`}
                          alt={pic}
                          title={pic}
                          style={{ width: '28px', height: '28px', objectFit: 'contain' }}
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = `/pictograms/${pic.toLowerCase()}.png`;
                          }}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Physical & OEL Summary */}
                  <div style={{ display: 'flex', gap: '16px', fontSize: '0.76rem', color: '#64748b', borderTop: '1px solid #f1f5f9', paddingTop: '10px' }}>
                    <div>
                      <b>Parlama Noktası:</b> {mat.fiziksel_ozellikler.parlama_noktasi}
                    </div>
                    <div>
                      <b>Kaynama Noktası:</b> {mat.fiziksel_ozellikler.kaynama_noktasi}
                    </div>
                    <div>
                      <b>Yoğunluk:</b> {mat.fiziksel_ozellikler.yogunluk}
                    </div>
                    <div>
                      <b>UN No:</b> {mat.tasimacilik_bilgileri.un_no} ({mat.tasimacilik_bilgileri.uygun_tasima_adi})
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer" style={{ padding: '14px 24px', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
            Hammadde seçildiğinde Bölüm 3.2 formuna kimyasal adı, CAS, EC, kayıt numarası ve SEA sınıflandırması otomatik işlenir.
          </span>
          <button className="btn btn-secondary" onClick={onClose}>
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
}
