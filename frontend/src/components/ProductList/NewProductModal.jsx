import React, { useState } from 'react';
import { api } from '../../api/client';
import { useApp } from '../../context/AppContext';
import { X, PlusCircle } from 'lucide-react';

export default function NewProductModal({ isOpen, onClose, onCreated }) {
  const { openProduct } = useApp();
  const [urunAdi, setUrunAdi] = useState('');
  const [ticariKod, setTicariKod] = useState('');
  const [kategori, setKategori] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!urunAdi.trim() || !ticariKod.trim()) {
      setError('Ürün adı ve ticari kod zorunludur.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const newProd = await api.createProduct({
        urun_adi: urunAdi.trim(),
        ticari_kod: ticariKod.trim(),
        kategori: kategori.trim() || null,
      });
      onClose();
      if (onCreated) onCreated();
      // Open in wizard immediately
      openProduct(newProd.id);
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
              <PlusCircle size={20} color="#2563eb" />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Yeni Kimyasal Ürün Oluştur</h3>
            </div>
            <button type="button" className="btn btn-secondary btn-icon" onClick={onClose}>
              <X size={18} />
            </button>
          </div>

          <div className="modal-body">
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
                <span>Ürün / Ticari Adı <span className="req-star">*</span></span>
              </label>
              <input
                type="text"
                className="form-control"
                placeholder="ör. Polyester Reçine PRS-100"
                value={urunAdi}
                onChange={(e) => setUrunAdi(e.target.value)}
                required
                autoFocus
              />
              <span className="form-help">Bölüm 1.1'deki Madde/Karışım Adı olarak otomatik tanımlanır.</span>
            </div>

            <div className="form-group">
              <label className="form-label">
                <span>Ticari Kod / Stok Kodu <span className="req-star">*</span></span>
              </label>
              <input
                type="text"
                className="form-control"
                placeholder="ör. AYP-PRS-100"
                value={ticariKod}
                onChange={(e) => setTicariKod(e.target.value)}
                required
              />
              <span className="form-help">Sayfa antetlerinde ve döküman başlığında kullanılacak benzersiz kod.</span>
            </div>

            <div className="form-group">
              <label className="form-label">
                <span>Ürün Ailesi / Kategori (Opsiyonel)</span>
              </label>
              <input
                type="text"
                className="form-control"
                placeholder="ör. Reçineler, Solventler, Astar ve Son Katlar..."
                value={kategori}
                onChange={(e) => setKategori(e.target.value)}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              İptal
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Oluşturuluyor...' : 'Oluştur ve Sihirbaza Geç'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
