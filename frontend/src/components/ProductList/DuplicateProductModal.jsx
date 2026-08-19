import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { useApp } from '../../context/AppContext';
import { X, Copy } from 'lucide-react';

export default function DuplicateProductModal({ isOpen, onClose, productToDuplicate, onDuplicated }) {
  const { openProduct } = useApp();
  const [yeniUrunAdi, setYeniUrunAdi] = useState('');
  const [yeniTicariKod, setYeniTicariKod] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (productToDuplicate) {
      setYeniUrunAdi(`${productToDuplicate.urun_adi} - Kopya`);
      setYeniTicariKod(`${productToDuplicate.ticari_kod}-COPY`);
    }
  }, [productToDuplicate]);

  if (!isOpen || !productToDuplicate) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const duplicated = await api.duplicateProduct(productToDuplicate.id, {
        yeni_urun_adi: yeniUrunAdi.trim(),
        yeni_ticari_kod: yeniTicariKod.trim(),
      });
      onClose();
      if (onDuplicated) onDuplicated();
      // Open the duplicated product in wizard
      openProduct(duplicated.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <form onSubmit={handleSubmit}>
          <div className="modal-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Copy size={18} color="#2563eb" />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Ürünü Kopyala</h3>
            </div>
            <button type="button" className="btn btn-secondary btn-icon" onClick={onClose}>
              <X size={18} />
            </button>
          </div>

          <div className="modal-body">
            <div
              style={{
                padding: '10px 14px',
                background: '#f1f5f9',
                borderRadius: '8px',
                marginBottom: '16px',
                fontSize: '0.85rem',
                color: '#334155',
              }}
            >
              Kaynak Ürün: <strong>{productToDuplicate.urun_adi}</strong> ({productToDuplicate.ticari_kod})
              <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '2px' }}>
                16 bölümlük tüm formülasyon ve SDS verileri yeni ürüne kopyalanacaktır.
              </div>
            </div>

            {error && (
              <div
                style={{
                  padding: '10px 14px',
                  background: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '8px',
                  color: '#991b1b',
                  fontSize: '0.85rem',
                  marginBottom: '16px',
                }}
              >
                {error}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">
                <span>Yeni Ürün Adı <span className="req-star">*</span></span>
              </label>
              <input
                type="text"
                className="form-control"
                value={yeniUrunAdi}
                onChange={(e) => setYeniUrunAdi(e.target.value)}
                required
                autoFocus
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <span>Yeni Ticari / Stok Kodu <span className="req-star">*</span></span>
              </label>
              <input
                type="text"
                className="form-control"
                value={yeniTicariKod}
                onChange={(e) => setYeniTicariKod(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              İptal
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Kopyalanıyor...' : 'Kopyala ve Aç'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
