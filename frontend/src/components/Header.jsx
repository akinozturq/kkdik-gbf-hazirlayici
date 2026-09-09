import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import ExportModal from './Wizard/ExportModal';
import AiSettingsModal from './AiSettingsModal';
import RawMaterialPickerModal from './Common/RawMaterialPickerModal';
import {
  FlaskConical,
  Save,
  CheckCircle2,
  XCircle,
  ArrowLeft,
  ShieldAlert,
  FileDown,
  Sparkles,
  Package,
} from 'lucide-react';

export default function Header() {
  const {
    currentView,
    product,
    autosaveStatus,
    lastSavedTime,
    validationReport,
    isValidationOpen,
    setIsValidationOpen,
    setIsPresetModalOpen,
    goToList,
    uiLang,
    setLanguage,
  } = useApp();

  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [isRawMaterialsOpen, setIsRawMaterialsOpen] = useState(false);

  const totalErrors = validationReport?.total_errors || 0;
  const totalWarnings = validationReport?.total_warnings || 0;
  const completionPct = validationReport?.overall_completion_percentage || 0;

  return (
    <>
      <header className="app-header">
        <div className="app-header-left">
          <div className="brand-badge">
            <div className="brand-logo-icon">
              <FlaskConical size={20} />
            </div>
            <span>KKDİK SDS Hazırlayıcı</span>
          </div>

          {currentView === 'wizard' && product && (
            <div className="product-breadcrumb">
              <button
                className="btn btn-secondary btn-sm"
                onClick={goToList}
                title="Ürün Listesine Dön"
                style={{ background: 'rgba(255,255,255,0.1)', color: 'white', borderColor: 'rgba(255,255,255,0.2)' }}
              >
                <ArrowLeft size={14} />
                Ürün Listesi
              </button>
              <span style={{ color: '#94a3b8' }}>/</span>
              <span style={{ fontWeight: 600, color: '#f8fafc' }}>
                {product.urun_adi}
              </span>
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                ({product.ticari_kod})
              </span>
            </div>
          )}
        </div>

        <div className="app-header-right">
          {currentView === 'wizard' && (
            <>
              {/* Autosave Status Pill */}
              <div className={`autosave-pill ${autosaveStatus}`}>
                {autosaveStatus === 'saving' && (
                  <>
                    <Save size={14} className="animate-spin" />
                    <span>Kaydediliyor...</span>
                  </>
                )}
                {autosaveStatus === 'saved' && (
                  <>
                    <CheckCircle2 size={14} />
                    <span>Kaydedildi {lastSavedTime ? `(${lastSavedTime})` : ''}</span>
                  </>
                )}
                {autosaveStatus === 'idle' && (
                  <>
                    <Save size={14} />
                    <span>Otomatik Kayıt Aktif</span>
                  </>
                )}
                {autosaveStatus === 'error' && (
                  <>
                    <XCircle size={14} style={{ color: '#ef4444' }} />
                    <span style={{ color: '#ef4444' }}>Kayıt Hatası</span>
                  </>
                )}
              </div>

              {/* Sektörel Şablon Uygula Button */}
              <button
                type="button"
                className="btn btn-sm"
                onClick={() => setIsPresetModalOpen(true)}
                title="Boya, tiner ve sertleştiriciler için hazır sektörel şablon uygula"
                style={{
                  background: 'rgba(59, 130, 246, 0.15)',
                  color: '#93c5fd',
                  borderColor: 'rgba(59, 130, 246, 0.35)',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <Sparkles size={14} color="#60a5fa" />
                <span>Sektörel Şablon</span>
              </button>

              {/* Validation Trigger Button */}
              <button
                className={`btn btn-sm ${
                  totalErrors > 0 ? 'btn-danger' : totalWarnings > 0 ? 'btn-secondary' : 'btn-secondary'
                }`}
                onClick={() => setIsValidationOpen(!isValidationOpen)}
                style={
                  totalErrors === 0 && totalWarnings === 0
                    ? { backgroundColor: '#065f46', color: '#a7f3d0', borderColor: '#047857' }
                    : totalErrors === 0 && totalWarnings > 0
                    ? { backgroundColor: '#78350f', color: '#fde68a', borderColor: '#92400e' }
                    : {}
                }
              >
                <ShieldAlert size={15} />
                <span>
                  {totalErrors > 0
                    ? `${totalErrors} Hata`
                    : totalWarnings > 0
                    ? `${totalWarnings} Uyarı`
                    : 'Mevzuata Uygun'}
                </span>
                <span style={{ fontSize: '0.75rem', opacity: 0.85 }}>({completionPct}%)</span>
              </button>

              {/* Dışa Aktar (Export) Button */}
              <button
                className="btn btn-primary btn-sm"
                onClick={() => setIsExportModalOpen(true)}
                style={{
                  background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                  boxShadow: '0 2px 4px rgba(37, 99, 235, 0.3)',
                }}
              >
                <FileDown size={15} />
                {uiLang === 'en' ? 'Export (SDS)' : 'Dışa Aktar (GBF)'}
              </button>
            </>
          )}

          {/* Hammadde Kütüphanesi Button */}
          <button
            type="button"
            className="btn btn-sm"
            onClick={() => setIsRawMaterialsOpen(true)}
            title="Hammadde Kütüphanesini Görüntüle ve Yönet"
            style={{
              background: 'rgba(2, 132, 199, 0.2)',
              color: '#7dd3fc',
              borderColor: 'rgba(2, 132, 199, 0.4)',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Package size={14} color="#38bdf8" />
            <span>Hammaddeler</span>
          </button>

          {/* Gemini AI Settings Button */}
          <button
            type="button"
            className="btn btn-sm"
            onClick={() => setIsAiModalOpen(true)}
            title="Google Gemini AI Çeviri ve Model Ayarları"
            style={{
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(147, 51, 234, 0.2) 100%)',
              color: '#ddd6fe',
              borderColor: 'rgba(168, 85, 247, 0.4)',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Sparkles size={14} color="#c084fc" />
            <span>Gemini AI</span>
          </button>

          {/* Language Switcher Toggle */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '20px',
              padding: '2px',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              marginLeft: '4px',
            }}
          >
            <button
              type="button"
              onClick={() => setLanguage('tr')}
              title="Türkçe (KKDİK)"
              style={{
                border: 'none',
                background: uiLang === 'tr' ? '#2563eb' : 'transparent',
                color: uiLang === 'tr' ? '#ffffff' : '#cbd5e1',
                padding: '3px 8px',
                borderRadius: '16px',
                fontSize: '0.74rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              🇹🇷 TR
            </button>
            <button
              type="button"
              onClick={() => setLanguage('en')}
              title="English (REACH Annex II)"
              style={{
                border: 'none',
                background: uiLang === 'en' ? '#2563eb' : 'transparent',
                color: uiLang === 'en' ? '#ffffff' : '#cbd5e1',
                padding: '3px 8px',
                borderRadius: '16px',
                fontSize: '0.74rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              🇬🇧 EN
            </button>
          </div>
        </div>
      </header>

      {/* Export Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
      />

      {/* Gemini AI Settings Modal */}
      <AiSettingsModal
        isOpen={isAiModalOpen}
        onClose={() => setIsAiModalOpen(false)}
      />

      {/* Raw Materials Library Modal */}
      <RawMaterialPickerModal
        isOpen={isRawMaterialsOpen}
        onClose={() => setIsRawMaterialsOpen(false)}
      />
    </>
  );
}
