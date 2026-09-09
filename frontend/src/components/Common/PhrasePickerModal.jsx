import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { X, Search, BookOpen, Check, Globe } from 'lucide-react';

const SECTIONS = [
  { key: '', label: 'Tüm Bölümler' },
  { key: 'b4', label: 'Bölüm 4: İlk Yardım' },
  { key: 'b5', label: 'Bölüm 5: Yangın' },
  { key: 'b6', label: 'Bölüm 6: Kaza / Dökülme' },
  { key: 'b7', label: 'Bölüm 7: Elleçleme / Depolama' },
  { key: 'b8', label: 'Bölüm 8: KKD / Maruziyet' },
  { key: 'b10', label: 'Bölüm 10: Kararlılık' },
  { key: 'b13', label: 'Bölüm 13: Bertaraf' },
];

export default function PhrasePickerModal({
  isOpen,
  onClose,
  onSelect,
  initialSection = '',
  fieldLabel = '',
}) {
  const [phrases, setPhrases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSection, setSelectedSection] = useState(initialSection);
  const [searchTerm, setSearchTerm] = useState('');
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    if (isOpen) {
      setSelectedSection(initialSection);
      fetchPhrases(initialSection, searchTerm);
    }
  }, [isOpen, initialSection]);

  const fetchPhrases = async (section, query) => {
    setLoading(true);
    try {
      const data = await api.getStandardPhrases({
        section: section || undefined,
        search: query || undefined,
      });
      setPhrases(data || []);
    } catch (err) {
      console.error('Standart ifadeler yüklenemedi:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSectionChange = (sec) => {
    setSelectedSection(sec);
    fetchPhrases(sec, searchTerm);
  };

  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearchTerm(val);
    fetchPhrases(selectedSection, val);
  };

  const handleSelectPhrase = (phrase) => {
    onSelect(phrase.text_tr);
    setCopiedId(phrase.id);
    setTimeout(() => {
      onClose();
    }, 250);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" style={{ zIndex: 1100 }}>
      <div
        className="modal-container"
        style={{
          maxWidth: '850px',
          width: '90%',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Başlık */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BookOpen size={20} color="#0284c7" />
            <div>
              <h3 style={{ margin: 0, fontSize: '1.1rem' }}>
                Standart Cümle Kataloğu (EuPhraC Phrase Bank)
              </h3>
              {fieldLabel && (
                <div style={{ fontSize: '0.78rem', color: '#64748b' }}>
                  Hedef Alan: <strong>{fieldLabel}</strong>
                </div>
              )}
            </div>
          </div>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Filtre ve Arama Alanı */}
        <div style={{ padding: '12px 20px', background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search
                size={16}
                style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }}
              />
              <input
                type="text"
                className="form-control"
                style={{ paddingLeft: '32px' }}
                placeholder="İfade başlığı, Türkçe veya İngilizce metin ara..."
                value={searchTerm}
                onChange={handleSearchChange}
              />
            </div>
          </div>

          {/* Bölüm Sekmeleri */}
          <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px' }}>
            {SECTIONS.map((sec) => (
              <button
                key={sec.key}
                type="button"
                className={`btn btn-sm ${selectedSection === sec.key ? 'btn-primary' : 'btn-outline'}`}
                style={{
                  whiteSpace: 'nowrap',
                  fontSize: '0.78rem',
                  padding: '4px 10px',
                  borderRadius: '16px',
                }}
                onClick={() => handleSectionChange(sec.key)}
              >
                {sec.label}
              </button>
            ))}
          </div>
        </div>

        {/* Cümle Listesi */}
        <div style={{ padding: '16px 20px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {loading && (
            <div style={{ textAlign: 'center', padding: '30px', color: '#64748b' }}>
              İfadeler yükleniyor...
            </div>
          )}

          {!loading && phrases.length === 0 && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: '#94a3b8' }}>
              Arama kriterlerinize uygun standart ifade bulunamadı.
            </div>
          )}

          {!loading &&
            phrases.map((phrase) => {
              const isSelected = copiedId === phrase.id;
              return (
                <div
                  key={phrase.id}
                  style={{
                    border: isSelected ? '1.5px solid #10b981' : '1px solid #e2e8f0',
                    borderRadius: '8px',
                    padding: '12px 14px',
                    background: isSelected ? '#ecfdf5' : '#ffffff',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span
                        style={{
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          background: '#e0f2fe',
                          color: '#0369a1',
                          padding: '2px 6px',
                          borderRadius: '4px',
                        }}
                      >
                        {phrase.id}
                      </span>
                      <strong style={{ fontSize: '0.9rem', color: '#0f172a' }}>
                        {phrase.title_tr}
                      </strong>
                    </div>

                    <button
                      type="button"
                      className={`btn btn-sm ${isSelected ? 'btn-success' : 'btn-primary'}`}
                      style={{ padding: '4px 12px', fontSize: '0.8rem', shrink: 0 }}
                      onClick={() => handleSelectPhrase(phrase)}
                    >
                      {isSelected ? (
                        <>
                          <Check size={13} /> Eklendi
                        </>
                      ) : (
                        '+ Bu İfadeyi Seç'
                      )}
                    </button>
                  </div>

                  {/* Türkçe Metin */}
                  <p style={{ margin: '0 0 6px 0', fontSize: '0.86rem', color: '#334155', lineHeight: 1.45 }}>
                    {phrase.text_tr}
                  </p>

                  {/* İngilizce Karşılık */}
                  {phrase.text_en && (
                    <div
                      style={{
                        fontSize: '0.78rem',
                        color: '#64748b',
                        background: '#f8fafc',
                        padding: '6px 8px',
                        borderRadius: '4px',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '6px',
                      }}
                    >
                      <Globe size={13} style={{ marginTop: '2px', color: '#0284c7', flexShrink: 0 }} />
                      <span style={{ fontStyle: 'italic' }}>{phrase.text_en}</span>
                    </div>
                  )}
                </div>
              );
            })}
        </div>

        {/* Alt Bilgi */}
        <div
          className="modal-footer"
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#f8fafc' }}
        >
          <span style={{ fontSize: '0.76rem', color: '#64748b' }}>
            EuPhraC uyumlu resmi kimyasal standart ifadeler kütüphanesi
          </span>
          <button type="button" className="btn btn-secondary btn-sm" onClick={onClose}>
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
}
