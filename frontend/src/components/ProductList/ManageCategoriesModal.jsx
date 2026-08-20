import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { X, Trash2, Plus, Folder, AlertTriangle, Check, Layers, ArrowRight } from 'lucide-react';

export default function ManageCategoriesModal({ isOpen, onClose, onChanged }) {
  const [categories, setCategories] = useState([]);
  const [newCatName, setNewCatName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Deletion prompt state
  const [deletingCat, setDeletingCat] = useState(null);
  const [targetCategory, setTargetCategory] = useState('Genel');

  useEffect(() => {
    if (isOpen) {
      loadCategories();
      setNewCatName('');
      setError(null);
      setSuccessMsg(null);
      setDeletingCat(null);
    }
  }, [isOpen]);

  const loadCategories = async () => {
    setLoading(true);
    try {
      const data = await api.getProductCategories();
      setCategories(data || []);
    } catch (err) {
      console.error('Kategoriler yüklenemedi:', err);
      setError('Kategoriler yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newCatName.trim()) return;

    setError(null);
    setSuccessMsg(null);
    try {
      await api.createProductCategory(newCatName.trim());
      setNewCatName('');
      setSuccessMsg(`"${newCatName.trim()}" ürün ailesi başarıyla eklendi.`);
      await loadCategories();
      if (onChanged) onChanged();
    } catch (err) {
      setError(err.message || 'Ürün ailesi eklenemedi.');
    }
  };

  const initiateDelete = (cat) => {
    setError(null);
    setSuccessMsg(null);
    if (cat.product_count === 0) {
      if (window.confirm(`"${cat.name}" ürün ailesini silmek istediğinize emin misiniz?`)) {
        executeDelete(cat.name, null);
      }
    } else {
      // Prompt for reassignment
      setDeletingCat(cat);
      const others = categories.filter((c) => c.name !== cat.name);
      setTargetCategory(others.length > 0 ? others[0].name : 'Genel');
    }
  };

  const executeDelete = async (catName, target) => {
    setLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const res = await api.deleteProductCategory(catName, target);
      setDeletingCat(null);
      setSuccessMsg(
        res.affected_products > 0
          ? `"${catName}" silindi ve ${res.affected_products} adet ürün "${res.reassigned_to}" ailesine aktarıldı.`
          : `"${catName}" ürün ailesi başarıyla silindi.`
      );
      await loadCategories();
      if (onChanged) onChanged();
    } catch (err) {
      setError(err.message || 'Silme işlemi başarısız oldu.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 9999 }}>
      <div
        className="modal-content"
        style={{ maxWidth: '580px', width: '95%', maxHeight: '85vh', display: 'flex', flexDirection: 'column' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="modal-header" style={{ padding: '18px 24px', background: '#f8fafc' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Layers size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#0f172a' }}>
                Ürün Ailelerini Yönet & Sil
              </h3>
              <p style={{ margin: '2px 0 0', fontSize: '0.78rem', color: '#64748b' }}>
                Mevcut ürün ailelerini görüntüleyin, yenilerini ekleyin veya silin
              </p>
            </div>
          </div>
          <button className="btn btn-secondary btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="modal-body" style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
          {error && (
            <div
              style={{
                padding: '10px 14px',
                background: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: '8px',
                color: '#991b1b',
                fontSize: '0.84rem',
                marginBottom: '14px',
                fontWeight: 600,
              }}
            >
              {error}
            </div>
          )}

          {successMsg && (
            <div
              style={{
                padding: '10px 14px',
                background: '#f0fdf4',
                border: '1px solid #bbf7d0',
                borderRadius: '8px',
                color: '#166534',
                fontSize: '0.84rem',
                marginBottom: '14px',
                fontWeight: 600,
              }}
            >
              ✓ {successMsg}
            </div>
          )}

          {/* Add New Category Form */}
          <form onSubmit={handleCreate} style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
            <input
              type="text"
              className="form-control"
              placeholder="Yeni ürün ailesi adı yazın... (ör. Vernikler)"
              value={newCatName}
              onChange={(e) => setNewCatName(e.target.value)}
              style={{ flex: 1 }}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!newCatName.trim() || loading}
              style={{ display: 'flex', alignItems: 'center', gap: '6px', whiteSpace: 'nowrap' }}
            >
              <Plus size={16} /> Ekle
            </button>
          </form>

          {/* Reassignment / Delete Prompt Confirmation Box */}
          {deletingCat && (
            <div
              style={{
                padding: '16px',
                background: '#fffbeb',
                border: '1px solid #fde68a',
                borderRadius: '10px',
                marginBottom: '20px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <AlertTriangle size={20} color="#d97706" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, color: '#92400e', fontSize: '0.92rem' }}>
                    "{deletingCat.name}" Ailesine Bağlı {deletingCat.product_count} Ürün Var
                  </div>
                  <p style={{ margin: '4px 0 12px', fontSize: '0.8rem', color: '#b45309' }}>
                    Bu ürün ailesini sildiğinizde, içerisindeki ürünlerin silinmemesi için başka bir ürün ailesine aktarılması gerekir:
                  </p>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label style={{ fontSize: '0.78rem', fontWeight: 700, color: '#78350f' }}>
                      Ürünlerin Aktarılacağı Hedef Aile:
                    </label>
                    <select
                      className="form-control"
                      value={targetCategory}
                      onChange={(e) => setTargetCategory(e.target.value)}
                      style={{ fontSize: '0.84rem' }}
                    >
                      <option value="Genel">📁 Genel (Varsayılan)</option>
                      {categories
                        .filter((c) => c.name !== deletingCat.name)
                        .map((c) => (
                          <option key={c.name} value={c.name}>
                            📁 {c.name}
                          </option>
                        ))}
                    </select>

                    <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => executeDelete(deletingCat.name, targetCategory)}
                        disabled={loading}
                        style={{ display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 700 }}
                      >
                        <Trash2 size={14} /> Sil ve Ürünleri Aktar
                      </button>
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => setDeletingCat(null)}
                      >
                        Vazgeç
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Category List Table */}
          <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
            <div
              style={{
                padding: '10px 14px',
                background: '#f8fafc',
                borderBottom: '1px solid #e2e8f0',
                fontSize: '0.78rem',
                fontWeight: 700,
                color: '#64748b',
                display: 'flex',
                justifyContent: 'space-between',
              }}
            >
              <span>ÜRÜN AİLESİ ADI</span>
              <span>BAĞLI ÜRÜN / İŞLEM</span>
            </div>

            {loading && categories.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>Yükleniyor...</div>
            ) : categories.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '24px', color: '#94a3b8' }}>
                Kayıtlı ürün ailesi bulunmamaktadır.
              </div>
            ) : (
              <div style={{ maxHeight: '320px', overflowY: 'auto' }}>
                {categories.map((cat, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '12px 14px',
                      borderBottom: idx === categories.length - 1 ? 'none' : '1px solid #f1f5f9',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      background: deletingCat?.name === cat.name ? '#fef2f2' : '#ffffff',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Folder size={16} color="#6366f1" />
                      <span style={{ fontWeight: 600, color: '#0f172a', fontSize: '0.88rem' }}>
                        {cat.name}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span
                        style={{
                          padding: '2px 8px',
                          borderRadius: '12px',
                          background: cat.product_count > 0 ? '#eff6ff' : '#f1f5f9',
                          color: cat.product_count > 0 ? '#1e40af' : '#64748b',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                        }}
                      >
                        {cat.product_count} ürün
                      </span>

                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => initiateDelete(cat)}
                        disabled={loading}
                        title={`"${cat.name}" ürün ailesini sil`}
                        style={{ padding: '4px 8px', borderRadius: '6px' }}
                      >
                        <Trash2 size={13} /> Sil
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer" style={{ padding: '14px 24px', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
            Toplam <b>{categories.length}</b> adet ürün ailesi tanımlı.
          </span>
          <button className="btn btn-secondary" onClick={onClose}>
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
}
