import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { useApp } from '../../context/AppContext';
import {
  X,
  FileText,
  FileDown,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  ShieldCheck,
  Download,
  Eye,
  Globe,
} from 'lucide-react';

export default function ExportModal({ isOpen, onClose }) {
  const { product, validationReport, uiLang, setLanguage } = useApp();
  const [selectedLang, setSelectedLang] = useState(uiLang || 'tr');
  const [downloadingDocx, setDownloadingDocx] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  // Sync selectedLang with uiLang when modal opens or uiLang changes
  useEffect(() => {
    if (isOpen && uiLang) {
      setSelectedLang(uiLang);
    }
  }, [isOpen, uiLang]);

  if (!isOpen || !product) return null;

  const isValid = validationReport?.is_valid_for_export;
  const errors = validationReport?.errors || [];
  const warnings = validationReport?.warnings || [];
  const completionPct = validationReport?.overall_completion_percentage || 0;

  const handleSelectLang = (lang) => {
    setSelectedLang(lang);
    if (setLanguage) {
      setLanguage(lang);
    }
  };

  const handleDocxDownload = async () => {
    setDownloadingDocx(true);
    setErrorMessage(null);
    try {
      const suffix = selectedLang === 'en' ? 'Safety_Data_Sheet' : 'Guvenlik_Bilgi_Formu';
      const filename = `${product.ticari_kod || 'GBF'}_${suffix}.docx`;
      await api.downloadDocx(product.id, filename, selectedLang);
    } catch (err) {
      console.error('Word indirme hatası:', err);
      setErrorMessage('Word belgesi indirilirken bir hata oluştu: ' + err.message);
    } finally {
      setDownloadingDocx(false);
    }
  };

  const handlePdfDownload = async () => {
    setDownloadingPdf(true);
    setErrorMessage(null);
    try {
      const suffix = selectedLang === 'en' ? 'Safety_Data_Sheet' : 'Guvenlik_Bilgi_Formu';
      const filename = `${product.ticari_kod || 'GBF'}_${suffix}.pdf`;
      await api.downloadPdf(product.id, filename, selectedLang);
    } catch (err) {
      console.error('PDF indirme hatası:', err);
      setErrorMessage('PDF belgesi indirilirken bir hata oluştu: ' + err.message);
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleOpenPreview = () => {
    const previewUrl = api.getPreviewHtmlUrl(product.id, selectedLang);
    window.open(previewUrl, '_blank');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: '640px' }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileDown size={20} color="#2563eb" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>
              {selectedLang === 'en' ? 'Export Safety Data Sheet (SDS)' : 'Güvenlik Bilgi Formu (GBF) Dışa Aktar'}
            </h3>
          </div>
          <button type="button" className="btn btn-secondary btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {errorMessage && (
            <div
              style={{
                padding: '12px 14px',
                background: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: '8px',
                color: '#991b1b',
                fontSize: '0.85rem',
                marginBottom: '16px',
              }}
            >
              {errorMessage}
            </div>
          )}

          {/* Product Summary Box */}
          <div
            style={{
              padding: '14px 16px',
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '10px',
              marginBottom: '18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ fontWeight: 700, fontSize: '1rem', color: '#1e40af' }}>
                {product.urun_adi}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#64748b', fontFamily: 'var(--font-mono)' }}>
                {product.ticari_kod} {product.kategori ? `• ${product.kategori}` : ''}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span
                style={{
                  fontSize: '0.95rem',
                  fontWeight: 800,
                  color: completionPct === 100 ? '#059669' : '#1e40af',
                }}
              >
                %{completionPct}
              </span>
              <div style={{ fontSize: '0.72rem', color: '#64748b' }}>
                {selectedLang === 'en' ? 'Completed' : 'Tamamlanma'}
              </div>
            </div>
          </div>

          {/* Validation Pre-Export Notice */}
          <div
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              marginBottom: '20px',
              background: isValid ? '#ecfdf5' : '#fffbeb',
              border: '1px solid',
              borderColor: isValid ? '#a7f3d0' : '#fde68a',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, fontSize: '0.88rem' }}>
              {isValid ? (
                <ShieldCheck size={18} color="#059669" />
              ) : (
                <AlertTriangle size={18} color="#d97706" />
              )}
              <span style={{ color: isValid ? '#065f46' : '#92400e' }}>
                {isValid
                  ? (selectedLang === 'en' ? 'Fully Compliant — Ready for Export' : 'Mevzuata Tam Uyumlu — Dışa Aktarıma Hazır')
                  : (selectedLang === 'en' ? `Validation Warnings (${errors.length} Missing Mandatory Fields)` : `Mevzuat Uyarıları (${errors.length} Eksik Zorunlu Alan)`)}
              </span>
            </div>
            <p style={{ fontSize: '0.78rem', color: '#475569', marginTop: '4px' }}>
              {isValid
                ? (selectedLang === 'en' ? 'All mandatory subheadings and REACH Annex II rules are satisfied.' : 'Tüm KKDİK Ek-2 zorunlu alt bölümleri ve kuralları eksiksiz karşılanmıştır.')
                : (selectedLang === 'en' ? 'Some fields are missing, but you can still download a draft copy in Word or PDF.' : 'Formda bazı zorunlu alanlar doldurulmamış olsa da taslak doküman olarak Word veya PDF formatında indirebilirsiniz.')}
            </p>
          </div>

          {/* Language Selector */}
          <div style={{ marginBottom: '18px' }}>
            <label style={{ fontSize: '0.82rem', fontWeight: 700, color: '#334155', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <Globe size={15} color="#2563eb" />
              GBF / SDS Dili & Mevzuat Şablonu:
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <button
                type="button"
                onClick={() => handleSelectLang('tr')}
                style={{
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: selectedLang === 'tr' ? '2px solid #2563eb' : '1px solid #cbd5e1',
                  background: selectedLang === 'tr' ? '#eff6ff' : '#ffffff',
                  textAlign: 'left',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  boxShadow: selectedLang === 'tr' ? '0 0 0 1px #2563eb' : 'none',
                }}
              >
                <span style={{ fontSize: '1.4rem' }}>🇹🇷</span>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.88rem', color: selectedLang === 'tr' ? '#1e40af' : '#1e293b' }}>
                    Türkçe (KKDİK)
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#64748b' }}>
                    KKDİK Yönetmeliği Ek-2
                  </div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => handleSelectLang('en')}
                style={{
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: selectedLang === 'en' ? '2px solid #2563eb' : '1px solid #cbd5e1',
                  background: selectedLang === 'en' ? '#eff6ff' : '#ffffff',
                  textAlign: 'left',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  boxShadow: selectedLang === 'en' ? '0 0 0 1px #2563eb' : 'none',
                }}
              >
                <span style={{ fontSize: '1.4rem' }}>🇬🇧</span>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.88rem', color: selectedLang === 'en' ? '#1e40af' : '#1e293b' }}>
                    English (SDS)
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#64748b' }}>
                    REACH Annex II & CLP
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Export Action Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
            {/* Word DOCX Card */}
            <div
              style={{
                border: '1px solid #cbd5e1',
                borderRadius: '10px',
                padding: '16px',
                background: '#ffffff',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, fontSize: '0.95rem', color: '#1e3a8a' }}>
                  <FileText size={18} color="#2563eb" />
                  <span>{selectedLang === 'en' ? 'Word Document (.docx)' : 'Word Belgesi (.docx)'}</span>
                </div>
                <p style={{ fontSize: '0.76rem', color: '#64748b', marginTop: '6px', lineHeight: 1.35 }}>
                  {selectedLang === 'en'
                    ? 'REACH Annex II structure, corporate header template (GBF ANTET.docx), logos and editable tables.'
                    : 'Resmi antet şablonu (GBF ANTET.docx), şirket logoları, tablolar ve düzenlenebilir Word formatı.'}
                </p>
              </div>

              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={handleDocxDownload}
                disabled={downloadingDocx}
                style={{ marginTop: '14px', width: '100%' }}
              >
                <Download size={14} />
                {downloadingDocx
                  ? 'İndiriliyor...'
                  : selectedLang === 'en'
                  ? 'Download Word (.docx)'
                  : 'Word İndir (.docx)'}
              </button>
            </div>

            {/* PDF Card */}
            <div
              style={{
                border: '1px solid #cbd5e1',
                borderRadius: '10px',
                padding: '16px',
                background: '#ffffff',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, fontSize: '0.95rem', color: '#991b1b' }}>
                  <FileText size={18} color="#dc2626" />
                  <span>{selectedLang === 'en' ? 'PDF Document (.pdf)' : 'PDF Belgesi (.pdf)'}</span>
                </div>
                <p style={{ fontSize: '0.76rem', color: '#64748b', marginTop: '6px', lineHeight: 1.35 }}>
                  {selectedLang === 'en'
                    ? 'Print-ready corporate layout, official REACH Annex II headings, page numbering and 16 section tables.'
                    : 'Baskıya hazır kurumsal mizanpaj, sayfa numaralandırması (Sayfa X / Y) ve 16 bölüm tabloları.'}
                </p>
              </div>

              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={handlePdfDownload}
                disabled={downloadingPdf}
                style={{ marginTop: '14px', width: '100%', backgroundColor: '#b91c1c', borderColor: '#991b1b' }}
              >
                <Download size={14} />
                {downloadingPdf
                  ? 'İndiriliyor...'
                  : selectedLang === 'en'
                  ? 'Download PDF (.pdf)'
                  : 'PDF İndir (.pdf)'}
              </button>
            </div>
          </div>

          {/* HTML Preview Button */}
          <div style={{ textAlign: 'center' }}>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={handleOpenPreview}
              style={{ color: '#475569', borderColor: '#cbd5e1' }}
            >
              <Eye size={14} />
              {selectedLang === 'en'
                ? 'Live HTML Preview in New Tab (English SDS)'
                : 'Yeni Sekmede Canlı HTML Önizleme (Türkçe GBF)'}
              <ExternalLink size={12} />
            </button>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            {selectedLang === 'en' ? 'Close' : 'Kapat'}
          </button>
        </div>
      </div>
    </div>
  );
}
