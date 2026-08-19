import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { useApp } from '../../context/AppContext';
import { X, PlusCircle, FolderPlus, ListFilter, Plus } from 'lucide-react';

export default function NewProductModal({ isOpen, onClose, onCreated }) {
  const { openProduct } = useApp();
  const [urunAdi, setUrunAdi] = useState('');
  const [ticariKod, setTicariKod] = useState('');
  const [selectedKategori, setSelectedKategori] = useState('');
  const [customKategori, setCustomKategori] = useState('');
  const [isCustomMode, setIsCustomMode] = useState(false);
  const [categoryOptions, setCategoryOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadCategories();
      // Reset form
      setUrunAdi('');
      setTicariKod('');
      setSelectedKategori('');
      setCustomKategori('');
      setIsCustomMode(false);
      setError(null);
    }
  }, [isOpen]);

  const loadCategories = async () => {
    try {
      const cats = await api.getProductCategories();
      setCategoryOptions(cats || []);
      if (cats && cats.length > 0) {
        setSelectedKategori(cats[0]);
      }
    } catch (err) {
      console.error('Kategoriler yüklenemedi:', err);
    }
  };

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const finalKategori = isCustomMode ? customKategori.trim() : selectedKategori.trim();

    if (!urunAdi.trim() || !ticariKod.trim()) {
      setError('Ürün adı ve ticari kod zorunludur.');
      return;
    }

    if (!finalKategori) {
      setError('Ürün ailesi seçimi veya yeni ürün ailesi girişi zorunludur.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const newProd = await api.createProduct({
        urun_adi: urunAdi.trim(),
        ticari_kod: ticariKod.trim(),
        kategori: finalKategori,
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
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 9999 }}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '560px' }}>
        <form onSubmit={handleSubmit}>
          <div className="modal-header" style={{ padding: '18px 24px', background: '#f8fafc' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <PlusCircle size={20} />
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#0f172a' }}>
                  Yeni Kimyasal Ürün Oluştur
                </h3>
                <p style={{ margin: '2px 0 0', fontSize: '0.78rem', color: '#64748b' }}>
                  Yeni bir ürün ve 16 bölümlük KKDİK SDS taslağı başlatır
                </p>
              </div>
            </div>
            <button type="button" className="btn btn-secondary btn-icon" onClick={onClose}>
              <X size={18} />
            </button>
          </div>

          <div className="modal-body" style={{ padding: '20px 24px' }}>
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
                  fontWeight: 600,
                }}
              >
                {error}
              </div>
            )}

            {/* 1. Ürün Adı */}
            <div className="form-group">
              <label className="form-label">
                <span>Ürün / Ticari Adı <span className="req-star">*</span></span>
              </label>
              <input
                type="text"
                className="form-control"
                placeholder="ör. Selülozik Tiner Ekstra / Epoksi Astar Gri"
                value={urunAdi}
                onChange={(e) => setUrunAdi(e.target.value)}
                required
                autoFocus
              />
              <span className="form-help">Bölüm 1.1'deki Madde/Karışım Adı olarak otomatik tanımlanır.</span>
            </div>

            {/* 2. Ticari Kod */}
            <div className="form-group">
              <label className="form-label">
                <span>Ticari Kod / Stok Kodu <span className="req-star">*</span></span>
              </label>
              <input
                type="text"
                className="form-control"
                placeholder="ör. SLV-TNR-100 / EPX-AST-202"
                value={ticariKod}
                onChange={(e) => setTicariKod(e.target.value)}
                required
              />
              <span className="form-help">Sayfa antetlerinde ve döküman başlığında kullanılacak benzersiz kod.</span>
            </div>

            {/* 3. Ürün Ailesi / Kategori (ZORUNLU) */}
            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label className="form-label" style={{ margin: 0 }}>
                  <span>Ürün Ailesi / Kategori <span className="req-star">*</span></span>
                </label>
                <button
                  type="button"
                  onClick={() => setIsCustomMode(!isCustomMode)}
                  style={{
                    border: 'none',
                    background: 'none',
                    color: '#2563eb',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  {isCustomMode ? (
                    <>
                      <ListFilter size={13} />
                      Mevcut Ailelerden Seç
                    </>
                  ) : (
                    <>
                      <FolderPlus size={13} />
                      + Yeni Ürün Ailesi Oluştur
                    </>
                  )}
                </button>
              </div>

              {!isCustomMode ? (
                <div>
                  <select
                    className="form-control"
                    value={selectedKategori}
                    onChange={(e) => {
                      if (e.target.value === '__new__') {
                        setIsCustomMode(true);
                        setCustomKategori('');
                      } else {
                        setSelectedKategori(e.target.value);
                      }
                    }}
                    required
                    style={{ fontWeight: 600, color: '#0f172a' }}
                  >
                    <option value="" disabled>-- Ürün Ailesi Seçiniz --</option>
                    {categoryOptions.map((cat) => (
                      <option key={cat} value={cat}>
                        📁 {cat}
                      </option>
                    ))}
                    <option value="__new__" style={{ color: '#2563eb', fontWeight: 700 }}>
                      ➕ Yeni Ürün Ailesi Oluştur...
                    </option>
                  </select>
                  <span className="form-help">Ürünün ait olduğu sektörel ürün ailesini seçiniz.</span>
                </div>
              ) : (
                <div>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="ör. Vernikler, Ahşap Koruyucular, Matbaa Mürekkepleri..."
                    value={customKategori}
                    onChange={(e) => setCustomKategori(e.target.value)}
                    required
                    autoFocus
                    style={{ borderColor: '#2563eb', background: '#eff6ff' }}
                  />
                  <span className="form-help">Yeni oluşturulacak ürün ailesinin adını giriniz.</span>
                </div>
              )}
            </div>
          </div>

          <div className="modal-footer" style={{ padding: '16px 24px', background: '#f8fafc' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              İptal
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)', fontWeight: 700 }}
            >
              {loading ? 'Oluşturuluyor...' : 'Oluştur ve Sihirbaza Geç'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
