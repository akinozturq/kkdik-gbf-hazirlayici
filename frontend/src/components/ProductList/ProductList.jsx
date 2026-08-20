import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { useApp } from '../../context/AppContext';
import NewProductModal from './NewProductModal';
import DuplicateProductModal from './DuplicateProductModal';
import ManageCategoriesModal from './ManageCategoriesModal';
import ExportModal from '../Wizard/ExportModal';
import {
  Search,
  Plus,
  Copy,
  Trash2,
  Edit3,
  FlaskConical,
  Filter,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Clock,
  FileDown,
  Layers,
} from 'lucide-react';

export default function ProductList() {
  const { openProduct } = useApp();
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [categories, setCategories] = useState([]);

  // Modals
  const [isNewModalOpen, setIsNewModalOpen] = useState(false);
  const [isManageCategoriesOpen, setIsManageCategoriesOpen] = useState(false);
  const [duplicateTarget, setDuplicateTarget] = useState(null);
  const [exportTarget, setExportTarget] = useState(null);

  // Load Products
  const loadProducts = async () => {
    setLoading(true);
    try {
      const res = await api.getProducts({
        query: searchTerm || undefined,
        kategori: selectedCategory || undefined,
        page_size: 50,
      });
      setProducts(res.items || []);
      setTotal(res.total || 0);

      // Load active categories from API
      const catData = await api.getProductCategories();
      const catNames = (catData || []).map((c) => (typeof c === 'string' ? c : c.name));
      setCategories(catNames);
    } catch (err) {
      console.error('Ürün listesi yüklenemedi:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadProducts();
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm, selectedCategory]);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`"${name}" adlı ürünü ve ilişkili tüm SDS verilerini silmek istediğinize emin misiniz?`)) {
      return;
    }
    try {
      await api.deleteProduct(id);
      loadProducts();
    } catch (err) {
      alert('Ürün silinirken hata: ' + err.message);
    }
  };

  const handleExportClick = async (p) => {
    await openProduct(p.id);
    setExportTarget(p);
  };

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1240px', margin: '0 auto', width: '100%' }}>
      {/* Top Banner / Actions */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em' }}>
            Kimyasal Ürün Yönetimi
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem', marginTop: '2px' }}>
            KKDİK Ek-2 uyumlu Güvenlik Bilgi Formu (SDS) kayıtları, taslak havuzu ve ihracat motoru
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            className="btn btn-outline"
            onClick={() => setIsManageCategoriesOpen(true)}
            style={{ borderColor: '#6366f1', color: '#4f46e5', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Layers size={16} />
            Ürün Ailelerini Yönet
          </button>

          <button className="btn btn-primary" onClick={() => setIsNewModalOpen(true)}>
            <Plus size={16} />
            Yeni Ürün Oluştur
          </button>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div
        className="card"
        style={{
          padding: '16px 20px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
          <input
            type="text"
            className="form-control"
            placeholder="Ürün adı veya ticari kod ile ara..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ paddingLeft: '38px' }}
          />
          <Search
            size={16}
            style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }}
          />
        </div>

        {categories.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} color="#64748b" />
            <select
              className="form-control"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              style={{ width: 'auto', minWidth: '180px' }}
            >
              <option value="">Tüm Kategoriler</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Product List Table / Grid */}
      <div className="card" style={{ overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '48px', textAlign: 'center', color: '#64748b' }}>
            Yükleniyor...
          </div>
        ) : products.length === 0 ? (
          <div style={{ padding: '64px 20px', textAlign: 'center' }}>
            <div
              style={{
                width: '56px',
                height: '56px',
                background: '#eff6ff',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px auto',
                color: '#2563eb',
              }}
            >
              <FlaskConical size={28} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#1e293b' }}>
              {searchTerm || selectedCategory ? 'Kriterlere uygun ürün bulunamadı' : 'Henüz kayıtlı ürün yok'}
            </h3>
            <p style={{ color: '#64748b', fontSize: '0.88rem', marginTop: '4px', maxWidth: '400px', margin: '4px auto 20px auto' }}>
              {searchTerm || selectedCategory
                ? 'Arama filtrenizi temizleyip tekrar deneyebilirsiniz.'
                : 'Yeni bir kimyasal ürün kaydı oluşturarak 16 bölümlük SDS sihirbazını başlatın.'}
            </p>
            {!searchTerm && !selectedCategory && (
              <button className="btn btn-primary" onClick={() => setIsNewModalOpen(true)}>
                <Plus size={16} />
                İlk Ürünü Oluştur
              </button>
            )}
          </div>
        ) : (
          <table className="custom-table" style={{ margin: 0 }}>
            <thead>
              <tr>
                <th>Ürün Bilgisi</th>
                <th>Kategori</th>
                <th>Tamamlanma</th>
                <th>Durum</th>
                <th>Son Güncelleme</th>
                <th style={{ textAlign: 'right' }}>İşlemler</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => {
                const completion = p.tamamlanma_yuzdesi || 0;
                const status = p.dogrulama_durumu || 'Eksik / Hatalı';

                return (
                  <tr key={p.id}>
                    <td>
                      <div
                        style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column' }}
                        onClick={() => openProduct(p.id)}
                      >
                        <span style={{ fontWeight: 700, color: '#1e40af', fontSize: '0.95rem' }}>
                          {p.urun_adi}
                        </span>
                        <span style={{ fontSize: '0.78rem', color: '#64748b', fontFamily: 'var(--font-mono)' }}>
                          {p.ticari_kod}
                        </span>
                      </div>
                    </td>
                    <td>
                      {p.kategori ? (
                        <span className="badge badge-neutral">{p.kategori}</span>
                      ) : (
                        <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>—</span>
                      )}
                    </td>
                    <td style={{ minWidth: '140px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ flex: 1, height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
                          <div
                            style={{
                              width: `${completion}%`,
                              height: '100%',
                              background: completion === 100 ? '#10b981' : completion > 50 ? '#3b82f6' : '#f59e0b',
                            }}
                          />
                        </div>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', minWidth: '32px' }}>
                          %{completion}
                        </span>
                      </div>
                    </td>
                    <td>
                      {status === 'Eksiksiz' && (
                        <span className="badge badge-success">
                          <CheckCircle2 size={12} />
                          Eksiksiz
                        </span>
                      )}
                      {status === 'Uyarılı' && (
                        <span className="badge badge-warning">
                          <AlertTriangle size={12} />
                          Uyarılı
                        </span>
                      )}
                      {status === 'Eksik / Hatalı' && (
                        <span className="badge badge-danger">
                          <AlertOctagon size={12} />
                          Eksik
                        </span>
                      )}
                    </td>
                    <td>
                      <div style={{ fontSize: '0.8rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Clock size={12} />
                        {new Date(p.son_guncelleme).toLocaleDateString('tr-TR', {
                          day: '2-digit',
                          month: '2-digit',
                          year: 'numeric',
                        })}
                      </div>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '6px' }}>
                        <button
                          className="btn btn-outline btn-sm"
                          onClick={() => openProduct(p.id)}
                          title="16 Adımlı Sihirbazı Aç"
                        >
                          <Edit3 size={14} />
                          Düzenle
                        </button>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => handleExportClick(p)}
                          title="Word / PDF Olarak Dışa Aktar"
                          style={{ color: '#1e40af' }}
                        >
                          <FileDown size={14} />
                        </button>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => setDuplicateTarget(p)}
                          title="Kopyalayarak Yeni Ürün Oluştur"
                        >
                          <Copy size={14} />
                        </button>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(p.id, p.urun_adi)}
                          title="Ürünü Sil"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Modals */}
      <NewProductModal
        isOpen={isNewModalOpen}
        onClose={() => setIsNewModalOpen(false)}
        onCreated={loadProducts}
      />

      <ManageCategoriesModal
        isOpen={isManageCategoriesOpen}
        onClose={() => setIsManageCategoriesOpen(false)}
        onChanged={loadProducts}
      />

      <DuplicateProductModal
        isOpen={Boolean(duplicateTarget)}
        productToDuplicate={duplicateTarget}
        onClose={() => setDuplicateTarget(null)}
        onDuplicated={loadProducts}
      />

      <ExportModal
        isOpen={Boolean(exportTarget)}
        onClose={() => setExportTarget(null)}
      />
    </div>
  );
}

