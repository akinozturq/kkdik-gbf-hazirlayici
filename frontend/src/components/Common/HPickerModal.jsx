import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Search, X, Plus, Check } from 'lucide-react';

export default function HPickerModal({
  isOpen,
  onClose,
  onSelect,
  selectedCodes = [],
  mode = 'H', // 'H' for hazard statements, 'P' for precautionary statements
}) {
  const { hStatements, pStatements } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState('ALL');

  if (!isOpen) return null;

  const rawList = mode === 'H' ? hStatements : pStatements;

  // Categories
  const categories = mode === 'H'
    ? ['ALL', 'Fiziksel', 'Sağlık', 'Çevre', 'İlave']
    : ['ALL', 'Genel', 'Önlem', 'Müdahale', 'Depolama', 'Bertaraf'];

  const filteredList = rawList.filter((item) => {
    const itemCat = mode === 'H' ? item.category : item.type;
    if (activeCategory !== 'ALL' && itemCat !== activeCategory) {
      return false;
    }
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      return (
        item.code.toLowerCase().includes(q) ||
        item.text.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: '680px' }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>
              {mode === 'H' ? 'Zararlılık İfadesi (H-Kodu) Seç' : 'Önlem İfadesi (P-Kodu) Seç'}
            </h3>
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
              Mevzuat standart Türkçe açıklamalarıyla birlikte liste
            </span>
          </div>
          <button className="btn btn-secondary btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Search Bar */}
          <div style={{ position: 'relative', marginBottom: '14px' }}>
            <input
              type="text"
              className="form-control"
              placeholder="Kod veya açıklama ile ara (ör. H225, alevlenir, soluma)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ paddingLeft: '36px' }}
              autoFocus
            />
            <Search
              size={16}
              style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }}
            />
          </div>

          {/* Category Tabs */}
          <div style={{ display: 'flex', gap: '6px', marginBottom: '14px', overflowX: 'auto', paddingBottom: '4px' }}>
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                className={`btn btn-sm ${activeCategory === cat ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveCategory(cat)}
              >
                {cat === 'ALL' ? 'Tümü' : cat}
              </button>
            ))}
          </div>

          {/* List of items */}
          <div style={{ maxHeight: '380px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {filteredList.map((item) => {
              const isSelected = selectedCodes.includes(item.code);
              return (
                <div
                  key={item.code}
                  onClick={() => onSelect(item)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    border: '1px solid',
                    borderColor: isSelected ? '#93c5fd' : '#e2e8f0',
                    background: isSelected ? '#eff6ff' : '#ffffff',
                    cursor: 'pointer',
                    transition: 'all 0.12s ease',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                    <span
                      style={{
                        fontFamily: 'monospace',
                        fontWeight: 700,
                        fontSize: '0.9rem',
                        padding: '2px 8px',
                        background: mode === 'H' ? '#fee2e2' : '#e0f2fe',
                        color: mode === 'H' ? '#991b1b' : '#0369a1',
                        borderRadius: '4px',
                        flexShrink: 0,
                      }}
                    >
                      {item.code}
                    </span>
                    <div>
                      <div style={{ fontSize: '0.86rem', color: '#1e293b', fontWeight: 500 }}>
                        {item.text}
                      </div>
                      <span style={{ fontSize: '0.72rem', color: '#64748b' }}>
                        {mode === 'H' ? item.category : item.type}
                      </span>
                    </div>
                  </div>

                  <button
                    type="button"
                    className={`btn btn-sm ${isSelected ? 'btn-secondary' : 'btn-outline'}`}
                    style={{ flexShrink: 0, marginLeft: '12px' }}
                  >
                    {isSelected ? (
                      <>
                        <Check size={13} color="#059669" />
                        <span style={{ color: '#059669' }}>Eklendi</span>
                      </>
                    ) : (
                      <>
                        <Plus size={13} />
                        <span>Ekle</span>
                      </>
                    )}
                  </button>
                </div>
              );
            })}

            {filteredList.length === 0 && (
              <div style={{ textAlign: 'center', padding: '32px', color: '#94a3b8' }}>
                Aradığınız kriterlere uygun ifade bulunamadı.
              </div>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn btn-primary" onClick={onClose}>
            Tamam
          </button>
        </div>
      </div>
    </div>
  );
}
