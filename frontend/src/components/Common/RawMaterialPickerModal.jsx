import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { Search, X, Plus, Package, Edit3, Trash2, CheckCircle2 } from 'lucide-react';
import RawMaterialFormModal from './RawMaterialFormModal';

export default function RawMaterialPickerModal({ isOpen, onClose, onSelect }) {
  const [materials, setMaterials] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  // Form Modal state (Create & Edit)
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editingMaterial, setEditingMaterial] = useState(null);
  const [toastMsg, setToastMsg] = useState(null);

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

  const showToast = (msg) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  const handleAddNew = () => {
    setEditingMaterial(null);
    setIsFormModalOpen(true);
  };

  const handleEdit = (mat, e) => {
    e?.stopPropagation();
    setEditingMaterial(mat);
    setIsFormModalOpen(true);
  };

  const handleDelete = async (mat, e) => {
    e?.stopPropagation();
    const confirmText = `"${mat.ad}" (${mat.cas_no || 'CAS yok'}) adlı hammadde kütüphaneden kalıcı olarak silinecek.\n\nEmin misiniz?`;
    if (!window.confirm(confirmText)) {
      return;
    }
    try {
      await api.deleteRawMaterial(mat.id);
      showToast(`"${mat.ad}" başarıyla silindi.`);
      loadMaterials(searchTerm);
    } catch (err) {
      alert('Hammadde silinirken bir hata oluştu: ' + (err.message || err));
    }
  };

  const handleSaved = (savedMat) => {
    showToast(editingMaterial ? `"${savedMat.ad}" güncellendi.` : `"${savedMat.ad}" kütüphaneye eklendi.`);
    loadMaterials(searchTerm);
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={onClose} style={{ zIndex: 9999 }}>
        <div
          className="modal-content"
          style={{ maxWidth: '920px', width: '95%', maxHeight: '88vh', display: 'flex', flexDirection: 'column', position: 'relative' }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Toast Notification */}
          {toastMsg && (
            <div
              style={{
                position: 'absolute',
                top: '16px',
                right: '70px',
                zIndex: 10001,
                background: '#065f46',
                color: '#ecfdf5',
                padding: '8px 16px',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.84rem',
                fontWeight: 600,
                animation: 'fadeIn 0.2s ease',
              }}
            >
              <CheckCircle2 size={16} />
              <span>{toastMsg}</span>
            </div>
          )}

          {/* Header */}
          <div className="modal-header" style={{ padding: '18px 24px', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
                  Formülasyon ve GBF hazırlamada kullanılacak standart onaylı kimyasal hammaddeler ({materials.length} hammadde)
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleAddNew}
                style={{
                  background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontWeight: 700,
                  padding: '8px 14px',
                  fontSize: '0.84rem',
                  boxShadow: '0 2px 6px rgba(2,132,199,0.25)',
                }}
              >
                <Plus size={16} />
                <span>Yeni Hammadde Ekle</span>
              </button>

              <button className="btn btn-secondary btn-icon" onClick={onClose}>
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Search Bar */}
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
                placeholder="Hammadde adı, ticari kod veya CAS numarası ile ara... (ör. Aseton, Toluen, 108-88-3, Desmodur)"
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
              <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                <p style={{ margin: 0, fontSize: '0.95rem' }}>Aramanıza uygun hammadde bulunamadı.</p>
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={handleAddNew}
                  style={{ marginTop: '12px', borderColor: '#0284c7', color: '#0284c7' }}
                >
                  <Plus size={15} /> Bu isimle yeni hammadde ekle
                </button>
              </div>
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
                    {/* Top Row: Name, Category & Actions */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                          <h4 style={{ margin: 0, fontSize: '1.08rem', fontWeight: 800, color: '#0f172a' }}>
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
                          {mat.is_isocyanate && (
                            <span
                              style={{
                                padding: '2px 8px',
                                borderRadius: '4px',
                                background: '#fef3c7',
                                color: '#92400e',
                                fontSize: '0.72rem',
                                fontWeight: 700,
                              }}
                            >
                              İzosiyanat (EUH204)
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '3px' }}>
                          <b>IUPAC:</b> {mat.iupac_adi || '-'} | <b>Ticari:</b> {mat.ticari_ad || '-'}
                        </div>
                      </div>

                      {/* Action Buttons: Karışıma Ekle (if onSelect), Düzenle, Sil */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {onSelect && (
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
                              padding: '7px 14px',
                              fontSize: '0.82rem',
                            }}
                          >
                            <Plus size={15} />
                            Karışıma Ekle (Bölüm 3.2)
                          </button>
                        )}
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={(e) => handleEdit(mat, e)}
                          title="Hammadde özelliklerini düzenle"
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            padding: '7px 10px',
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            color: '#0369a1',
                            borderColor: '#bae6fd',
                            background: '#f0f9ff',
                          }}
                        >
                          <Edit3 size={14} />
                          <span>Düzenle</span>
                        </button>
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={(e) => handleDelete(mat, e)}
                          title="Hammaddeyi kütüphaneden sil"
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            padding: '7px 9px',
                            color: '#dc2626',
                            borderColor: '#fecaca',
                            background: '#fef2f2',
                          }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
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
                        <b style={{ color: '#0f172a', fontFamily: 'monospace' }}>{mat.cas_no || '-'}</b>
                      </div>
                      <div>
                        <span style={{ color: '#64748b', display: 'block' }}>EC No:</span>
                        <b style={{ color: '#0f172a', fontFamily: 'monospace' }}>{mat.ec_no || '-'}</b>
                      </div>
                      <div>
                        <span style={{ color: '#64748b', display: 'block' }}>KKDİK / REACH Kayıt:</span>
                        <b style={{ color: '#0f172a', fontFamily: 'monospace' }}>{mat.kayit_no || '-'}</b>
                      </div>
                      <div>
                        <span style={{ color: '#64748b', display: 'block' }}>Formül / Mol. Ağırlık:</span>
                        <b style={{ color: '#0f172a' }}>
                          {mat.molekul_formulu || '-'} {mat.molekul_agirligi ? `(${mat.molekul_agirligi})` : ''}
                        </b>
                      </div>
                    </div>

                    {/* SEA Classification & Pictograms */}
                    <div style={{ marginBottom: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#475569' }}>
                          SEA Sınıflandırması:
                        </span>
                        {mat.uyari_kelimesi && (
                          <span
                            style={{
                              padding: '2px 7px',
                              borderRadius: '4px',
                              background: mat.uyari_kelimesi === 'Tehlike' ? '#fee2e2' : '#fef3c7',
                              color: mat.uyari_kelimesi === 'Tehlike' ? '#991b1b' : '#92400e',
                              fontSize: '0.75rem',
                              fontWeight: 700,
                            }}
                          >
                            {mat.uyari_kelimesi}
                          </span>
                        )}
                        <span style={{ fontSize: '0.8rem', color: '#1e293b', fontWeight: 600 }}>
                          {mat.siniflandirma_str || '-'}
                        </span>
                      </div>

                      {mat.piktogramlar && mat.piktogramlar.length > 0 && (
                        <div style={{ display: 'flex', gap: '6px', marginTop: '8px', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.74rem', color: '#64748b', marginRight: '4px' }}>Piktogramlar:</span>
                          {mat.piktogramlar.map((pic) => (
                            <img
                              key={pic}
                              src={`/pictograms/${pic.toLowerCase()}.svg`}
                              alt={pic}
                              title={pic}
                              style={{ width: '26px', height: '26px', objectFit: 'contain' }}
                              onError={(e) => {
                                e.target.onerror = null;
                                e.target.src = `/pictograms/${pic.toLowerCase()}.png`;
                              }}
                            />
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Physical & OEL & Transport Summary */}
                    <div style={{ display: 'flex', gap: '16px', fontSize: '0.76rem', color: '#64748b', borderTop: '1px solid #f1f5f9', paddingTop: '10px', flexWrap: 'wrap' }}>
                      {mat.fiziksel_ozellikler?.parlama_noktasi && (
                        <div>
                          <b>Parlama Noktası:</b> {mat.fiziksel_ozellikler.parlama_noktasi}
                        </div>
                      )}
                      {mat.fiziksel_ozellikler?.kaynama_noktasi && (
                        <div>
                          <b>Kaynama Noktası:</b> {mat.fiziksel_ozellikler.kaynama_noktasi}
                        </div>
                      )}
                      {mat.fiziksel_ozellikler?.yogunluk && (
                        <div>
                          <b>Yoğunluk:</b> {mat.fiziksel_ozellikler.yogunluk}
                        </div>
                      )}
                      {mat.tasimacilik_bilgileri?.un_no && (
                        <div>
                          <b>UN No:</b> {mat.tasimacilik_bilgileri.un_no} {mat.tasimacilik_bilgileri.uygun_tasima_adi ? `(${mat.tasimacilik_bilgileri.uygun_tasima_adi})` : ''}
                        </div>
                      )}
                    </div>

                    {/* ATE / Toksisite Sınırları */}
                    {(mat.akut_toksisite_oral || mat.akut_toksisite_dermal || mat.akut_toksisite_soluma) && (
                      <div style={{ display: 'flex', gap: '16px', fontSize: '0.76rem', color: '#64748b', borderTop: '1px solid #f1f5f9', paddingTop: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
                        {mat.akut_toksisite_oral && (
                          <div>
                            <b>ATE Oral LD50:</b> {mat.akut_toksisite_oral} mg/kg
                          </div>
                        )}
                        {mat.akut_toksisite_dermal && (
                          <div>
                            <b>ATE Dermal LD50:</b> {mat.akut_toksisite_dermal} mg/kg
                          </div>
                        )}
                        {mat.akut_toksisite_soluma && (
                          <div>
                            <b>ATE Soluma LC50:</b> {mat.akut_toksisite_soluma} mg/L
                          </div>
                        )}
                        {mat.m_faktoru_akut && (
                          <div>
                            <b>M (Akut):</b> {mat.m_faktoru_akut}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="modal-footer" style={{ padding: '14px 24px', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
              {onSelect
                ? 'Hammadde seçildiğinde Bölüm 3.2 formuna kimyasal adı, CAS, EC, kayıt no ve SEA sınıflandırması otomatik aktarılır.'
                : 'Kütüphanede eklediğiniz veya güncellediğiniz hammaddeler anında tüm ürünlerin Bölüm 3 reçetesinde kullanılabilir hale gelir.'}
            </span>
            <button className="btn btn-secondary" onClick={onClose}>
              Kapat
            </button>
          </div>
        </div>
      </div>

      {/* Raw Material Create / Edit Modal */}
      <RawMaterialFormModal
        isOpen={isFormModalOpen}
        onClose={() => setIsFormModalOpen(false)}
        initialData={editingMaterial}
        onSaved={handleSaved}
      />
    </>
  );
}
