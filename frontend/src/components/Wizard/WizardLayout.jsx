import React from 'react';
import { useApp } from '../../context/AppContext';
import ValidationDrawer from '../Common/ValidationDrawer';
import PresetModal from './PresetModal';

// Import all 16 step components
import Step1_Kimlik from './Steps/Step1_Kimlik';
import Step2_ZararTanimi from './Steps/Step2_ZararTanimi';
import Step3_Bilesim from './Steps/Step3_Bilesim';
import Step4_IlkYardim from './Steps/Step4_IlkYardim';
import Step5_YanginMucadele from './Steps/Step5_YanginMucadele';
import Step6_KazaYayilma from './Steps/Step6_KazaYayilma';
import Step7_EllecmeDepolama from './Steps/Step7_EllecmeDepolama';
import Step8_MaruzKalma from './Steps/Step8_MaruzKalma';
import Step9_FizikselKimyasal from './Steps/Step9_FizikselKimyasal';
import Step10_KararlilikTepkime from './Steps/Step10_KararlilikTepkime';
import Step11_Toksikolojik from './Steps/Step11_Toksikolojik';
import Step12_Ekolojik from './Steps/Step12_Ekolojik';
import Step13_Bertaraf from './Steps/Step13_Bertaraf';
import Step14_Tasimacilik from './Steps/Step14_Tasimacilik';
import Step15_Mevzuat from './Steps/Step15_Mevzuat';
import Step16_DigerBilgiler from './Steps/Step16_DigerBilgiler';

import {
  ChevronLeft,
  ChevronRight,
  Save,
  CheckCircle2,
  AlertOctagon,
  FileCheck2,
  FileText,
  Sparkles,
} from 'lucide-react';

const SECTIONS = [
  { num: 1, title: 'Madde / Karışım ve Şirket Kimliği', code: 'B1', legal: 'KKDİK Ek-2 md. 1' },
  { num: 2, title: 'Zararlılık Tanımı', code: 'B2', legal: 'KKDİK Ek-2 md. 2' },
  { num: 3, title: 'Bileşimi / İçindekiler Hakkında Bilgi', code: 'B3', legal: 'KKDİK Ek-2 md. 3' },
  { num: 4, title: 'İlk Yardım Önlemleri', code: 'B4', legal: 'KKDİK Ek-2 md. 4' },
  { num: 5, title: 'Yangınla Mücadele Önlemleri', code: 'B5', legal: 'KKDİK Ek-2 md. 5' },
  { num: 6, title: 'Kaza Sonucu Yayılmaya Karşı Önlemler', code: 'B6', legal: 'KKDİK Ek-2 md. 6' },
  { num: 7, title: 'Elleçleme ve Depolama', code: 'B7', legal: 'KKDİK Ek-2 md. 7' },
  { num: 8, title: 'Maruz Kalma Kontrolleri / Kişisel Korunma', code: 'B8', legal: 'KKDİK Ek-2 md. 8' },
  { num: 9, title: 'Fiziksel ve Kimyasal Özellikler', code: 'B9', legal: 'KKDİK Ek-2 md. 9' },
  { num: 10, title: 'Kararlılık ve Tepkime', code: 'B10', legal: 'KKDİK Ek-2 md. 10' },
  { num: 11, title: 'Toksikolojik Bilgiler', code: 'B11', legal: 'KKDİK Ek-2 md. 11' },
  { num: 12, title: 'Ekolojik Bilgiler', code: 'B12', legal: 'KKDİK Ek-2 md. 12' },
  { num: 13, title: 'Bertaraf Etme Bilgileri', code: 'B13', legal: 'KKDİK Ek-2 md. 13' },
  { num: 14, title: 'Taşımacılık Bilgisi', code: 'B14', legal: 'KKDİK Ek-2 md. 14' },
  { num: 15, title: 'Mevzuat Bilgisi', code: 'B15', legal: 'KKDİK Ek-2 md. 15' },
  { num: 16, title: 'Diğer Bilgiler', code: 'B16', legal: 'KKDİK Ek-2 md. 16' },
];

export default function WizardLayout() {
  const {
    activeStep,
    setActiveStep,
    product,
    validationReport,
    setIsValidationOpen,
    isPresetModalOpen,
    setIsPresetModalOpen,
    saveNow,
    autosaveStatus,
  } = useApp();

  const currentSection = SECTIONS.find((s) => s.num === activeStep) || SECTIONS[0];
  const sectionProgressMap = {};
  (validationReport?.section_progress || []).forEach((sp) => {
    sectionProgressMap[sp.section_number] = sp;
  });

  const overallPct = validationReport?.overall_completion_percentage || 0;

  const renderStepContent = () => {
    switch (activeStep) {
      case 1:
        return <Step1_Kimlik />;
      case 2:
        return <Step2_ZararTanimi />;
      case 3:
        return <Step3_Bilesim />;
      case 4:
        return <Step4_IlkYardim />;
      case 5:
        return <Step5_YanginMucadele />;
      case 6:
        return <Step6_KazaYayilma />;
      case 7:
        return <Step7_EllecmeDepolama />;
      case 8:
        return <Step8_MaruzKalma />;
      case 9:
        return <Step9_FizikselKimyasal />;
      case 10:
        return <Step10_KararlilikTepkime />;
      case 11:
        return <Step11_Toksikolojik />;
      case 12:
        return <Step12_Ekolojik />;
      case 13:
        return <Step13_Bertaraf />;
      case 14:
        return <Step14_Tasimacilik />;
      case 15:
        return <Step15_Mevzuat />;
      case 16:
        return <Step16_DigerBilgiler />;
      default:
        return <Step1_Kimlik />;
    }
  };

  return (
    <div className="wizard-layout">
      {/* 16 Steps Navigation Sidebar */}
      <aside className="wizard-sidebar">
        <div className="wizard-sidebar-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#475569' }}>
              SDS TAMAMLANMA ORANI
            </span>
            <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#1e40af' }}>
              %{overallPct}
            </span>
          </div>
          <div style={{ width: '100%', height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
            <div
              style={{
                width: `${overallPct}%`,
                height: '100%',
                background: overallPct === 100 ? '#10b981' : '#3b82f6',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
        </div>

        <div className="wizard-sidebar-steps">
          {SECTIONS.map((sec) => {
            const isActive = activeStep === sec.num;
            const progress = sectionProgressMap[sec.num];
            const hasError = progress?.has_errors;
            const isFull = progress?.completion_percentage === 100;

            return (
              <div
                key={sec.num}
                className={`step-nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setActiveStep(sec.num)}
              >
                <div className="step-nav-left">
                  <div className="step-num-bubble">{sec.num}</div>
                  <div className="step-nav-title" title={sec.title}>
                    {sec.title}
                  </div>
                </div>

                <div className="step-nav-right">
                  {hasError ? (
                    <AlertOctagon size={14} color="#dc2626" title="Bu bölümde eksik zorunlu alan var" />
                  ) : isFull ? (
                    <CheckCircle2 size={14} color="#059669" title="Bölüm eksiksiz" />
                  ) : (
                    <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                      %{progress?.completion_percentage || 0}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </aside>

      {/* Main Step Form Area */}
      <main className="wizard-main">
        <div className="wizard-step-card">
          <div className="step-header">
            <div className="step-badge-row" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="badge badge-neutral" style={{ fontSize: '0.78rem' }}>
                BÖLÜM {currentSection.num} / 16
              </span>

              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button
                  type="button"
                  className="btn btn-outline btn-sm"
                  style={{
                    borderColor: '#93c5fd',
                    color: '#1d4ed8',
                    background: '#eff6ff',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                  }}
                  onClick={() => setIsPresetModalOpen(true)}
                  title="Boya, Tiner ve Sertleştiriciler için hazır KKDİK metinlerini uygula"
                >
                  <Sparkles size={14} color="#2563eb" />
                  ⚡ Sektörel Şablon Doldur
                </button>

                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => setIsValidationOpen(true)}
                >
                  <FileCheck2 size={14} />
                  Doğrulama Çekmecesi
                </button>
              </div>
            </div>

            <h2 className="step-title">
              {currentSection.num}. {currentSection.title}
            </h2>

            <div className="step-legal-ref">
              <FileText size={14} />
              <span>{currentSection.legal} — Resmi Gazete No: 30105</span>
            </div>
          </div>

          {/* Render Step Form Body */}
          <div className="step-body" style={{ minHeight: '400px' }}>
            {renderStepContent()}
          </div>

          {/* Bottom Step Actions */}
          <div
            style={{
              marginTop: '36px',
              paddingTop: '20px',
              borderTop: '1px solid var(--border-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <button
              type="button"
              className="btn btn-secondary"
              disabled={activeStep === 1}
              onClick={() => setActiveStep((prev) => Math.max(1, prev - 1))}
            >
              <ChevronLeft size={16} />
              Önceki Bölüm
            </button>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => saveNow()}
                disabled={autosaveStatus === 'saving'}
              >
                <Save size={15} />
                {autosaveStatus === 'saving' ? 'Kaydediliyor...' : 'Şimdi Kaydet'}
              </button>

              {activeStep < 16 ? (
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => setActiveStep((prev) => Math.min(16, prev + 1))}
                >
                  Sonraki Bölüm
                  <ChevronRight size={16} />
                </button>
              ) : (
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => setIsValidationOpen(true)}
                  style={{ background: '#059669', borderColor: '#047857' }}
                >
                  <CheckCircle2 size={16} />
                  Formu Tamamla ve Doğrula
                </button>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Sektörel Şablon Doldurma Modalı */}
      <PresetModal isOpen={isPresetModalOpen} onClose={() => setIsPresetModalOpen(false)} />

      {/* Slide-over Validation Drawer */}
      <ValidationDrawer />
    </div>
  );
}
