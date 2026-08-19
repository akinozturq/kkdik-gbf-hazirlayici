import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { Search, X, Plus, Check, ShieldCheck, FileSpreadsheet } from 'lucide-react';

export default function ExposureLimitPickerModal({ isOpen, onClose, onSelect, existingItems = [] }) {
  const [limits, setLimits] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadLimits();
    }
  }, [isOpen]);

  const loadLimits = async (search = null) => {
    setLoading(true);
    try {
      const data = await api.getExposureLimits(search);
      setLimits(data);
    } catch (err) {
      console.error('Maruziyet limitleri yüklenemedi:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearchTerm(val);
    loadLimits(val);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 9999 }}>
      <div
        className="modal-content"
        style={{ maxWidth: '850px', width: '95%', maxHeight: '85vh', display: 'flex', flexDirection: 'column' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="modal-header" style={{ padding: '18px 24px', background: '#f8fafc' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <FileSpreadsheet size={22} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800, color: '#0f172a' }}>
                Mesleki Maruziyet Sınır Değerleri Kütüphanesi
              </h3>
              <p style={{ margin: '2px 0 0', fontSize: '0.78rem', color: '#64748b' }}>
                Kimyasal Maddelerle Çalışmalarda Sağlık ve Güvenlik Önlemleri Hakkında Yönetmelik (Ek-1)
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
              placeholder="Madde adı, CAS no veya EC no ile ara... (ör. Ksilen, 108-88-3, Aseton, 203-625-9)"
              value={searchTerm}
              onChange={handleSearchChange}
              autoFocus
            />
          </div>
        </div>

        {/* List */}
        <div className="modal-body" style={{ padding: '16px 24px', overflowY: 'auto', flex: 1 }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '30px', color: '#64748b' }}>Yükleniyor...</div>
          ) : limits.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>Aramanıza uygun sınır değer bulunamadı.</div>
          ) : (
            <table className="custom-table" style={{ margin: 0, fontSize: '0.82rem' }}>
              <thead>
                <tr>
                  <th style={{ width: '28%' }}>Madde Adı</th>
                  <th style={{ width: '18%' }}>CAS / EC No</th>
                  <th style={{ width: '22%' }}>TWA (8 Saat)</th>
                  <th style={{ width: '20%' }}>STEL (15 Dak.)</th>
                  <th style={{ width: '12%', textAlign: 'center' }}>İşlem</th>
                </tr>
              </thead>
              <tbody>
                {limits.map((item, idx) => {
                  const twaParts = [];
                  if (item.twa_ppm) twaParts.push(`${item.twa_ppm} ppm`);
                  if (item.twa_mg_m3) twaParts.push(`${item.twa_mg_m3} mg/m³`);

                  const stelParts = [];
                  if (item.stel_ppm) stelParts.push(`${item.stel_ppm} ppm`);
                  if (item.stel_mg_m3) stelParts.push(`${item.stel_mg_m3} mg/m³`);

                  return (
                    <tr key={idx}>
                      <td style={{ fontWeight: 600, color: '#0f172a' }}>
                        {item.name}
                        {item.notes && (
                          <span
                            style={{
                              marginLeft: '6px',
                              padding: '2px 6px',
                              borderRadius: '4px',
                              background: '#fef3c7',
                              color: '#92400e',
                              fontSize: '0.72rem',
                              fontWeight: 700,
                            }}
                          >
                            {item.notes}
                          </span>
                        )}
                      </td>
                      <td style={{ fontFamily: 'monospace', color: '#475569' }}>
                        {item.cas && <div>CAS: {item.cas}</div>}
                        {item.einecs && <div>EC: {item.einecs}</div>}
                      </td>
                      <td>{twaParts.join(' / ') || '—'}</td>
                      <td>{stelParts.join(' / ') || '—'}</td>
                      <td style={{ textAlign: 'center' }}>
                        <button
                          type="button"
                          className="btn btn-outline btn-sm"
                          onClick={() => {
                            onSelect(item);
                          }}
                          style={{ borderColor: '#059669', color: '#059669', padding: '4px 8px' }}
                        >
                          <Plus size={13} /> Ekle
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer" style={{ padding: '14px 24px', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
            Toplam <b>{limits.length}</b> mesleki maruziyet sınır değeri listeleniyor.
          </span>
          <button className="btn btn-secondary" onClick={onClose}>
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
}
