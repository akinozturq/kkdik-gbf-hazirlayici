import React from 'react';
import { useApp } from '../../context/AppContext';
import {
  X,
  AlertOctagon,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  Percent,
} from 'lucide-react';

export default function ValidationDrawer() {
  const {
    isValidationOpen,
    setIsValidationOpen,
    validationReport,
    setActiveStep,
  } = useApp();

  if (!isValidationOpen) return null;

  const errors = validationReport?.errors || [];
  const warnings = validationReport?.warnings || [];
  const progressList = validationReport?.section_progress || [];
  const isValid = validationReport?.is_valid_for_export;
  const overallPct = validationReport?.overall_completion_percentage || 0;

  // Extract step number from section code (e.g., 'B1.1' -> 1)
  const jumpToSection = (sectionCode) => {
    if (!sectionCode) return;
    const match = sectionCode.match(/B(\d+)/i);
    if (match) {
      const stepNum = parseInt(match[1], 10);
      if (stepNum >= 1 && stepNum <= 16) {
        setActiveStep(stepNum);
      }
    }
  };

  return (
    <div className={`validation-drawer ${isValidationOpen ? 'open' : ''}`}>
      <div className="drawer-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {isValid ? (
            <ShieldCheck size={20} color="#059669" />
          ) : (
            <AlertOctagon size={20} color="#dc2626" />
          )}
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>KKDİK Doğrulama</h3>
            <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
              Toplam İlerleme: %{overallPct}
            </span>
          </div>
        </div>
        <button
          className="btn btn-secondary btn-icon"
          onClick={() => setIsValidationOpen(false)}
          title="Kapat"
        >
          <X size={16} />
        </button>
      </div>

      <div className="drawer-body">
        {/* Export Readiness Card */}
        <div
          className="card"
          style={{
            padding: '12px 14px',
            marginBottom: '16px',
            background: isValid ? '#ecfdf5' : '#fef2f2',
            borderColor: isValid ? '#a7f3d0' : '#fecaca',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, fontSize: '0.88rem' }}>
            {isValid ? (
              <CheckCircle2 size={16} color="#059669" />
            ) : (
              <AlertOctagon size={16} color="#dc2626" />
            )}
            <span style={{ color: isValid ? '#065f46' : '#991b1b' }}>
              {isValid
                ? 'Dışa Aktarıma Hazır (PDF/DOCX)'
                : `${errors.length} Engelliyici Hata Bulundu`}
            </span>
          </div>
          <p style={{ fontSize: '0.78rem', color: '#475569', marginTop: '4px' }}>
            {isValid
              ? 'Tüm zorunlu KKDİK Ek-2 alt bölümleri ve kuralları karşılanmıştır.'
              : 'Resmi mevzuat gereği eksik alanlar doldurulmadan dışa aktarım tavsiye edilmez.'}
          </p>
        </div>

        {/* Errors Section */}
        {errors.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#991b1b', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertOctagon size={14} />
              Zorunlu Alan Hataları ({errors.length})
            </h4>
            {errors.map((err, idx) => (
              <div
                key={idx}
                className="val-item-card error"
                onClick={() => jumpToSection(err.section)}
                style={{ cursor: 'pointer' }}
                title="İlgili bölüme gitmek için tıklayın"
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span className="badge badge-danger">{err.section}</span>
                  <span style={{ fontSize: '0.72rem', color: '#b91c1c' }}>
                    {err.regulation_ref}
                  </span>
                </div>
                <div style={{ fontSize: '0.82rem', fontWeight: 500 }}>
                  {err.message}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: '#dc2626', marginTop: '6px', fontWeight: 600 }}>
                  <span>Bölüme Git</span>
                  <ArrowRight size={12} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Warnings Section */}
        {warnings.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#92400e', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertTriangle size={14} />
              Mevzuat Uyarıları ({warnings.length})
            </h4>
            {warnings.map((warn, idx) => (
              <div
                key={idx}
                className="val-item-card warning"
                onClick={() => jumpToSection(warn.section)}
                style={{ cursor: 'pointer' }}
                title="İlgili bölüme gitmek için tıklayın"
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span className="badge badge-warning">{warn.section}</span>
                  <span style={{ fontSize: '0.72rem', color: '#b45309' }}>
                    {warn.regulation_ref}
                  </span>
                </div>
                <div style={{ fontSize: '0.82rem', fontWeight: 500 }}>
                  {warn.message}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: '#d97706', marginTop: '6px', fontWeight: 600 }}>
                  <span>Düzenle</span>
                  <ArrowRight size={12} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 16 Section Progress List */}
        <div>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#1e293b', marginBottom: '10px' }}>
            Bölüm Doluluk Oranları
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {progressList.map((sp) => (
              <div
                key={sp.section_number}
                onClick={() => setActiveStep(sp.section_number)}
                style={{
                  padding: '8px 10px',
                  borderRadius: '6px',
                  background: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 600, color: '#334155' }}>
                    Bölüm {sp.section_number}: {sp.section_code}
                  </span>
                  <span style={{ fontWeight: 700, color: sp.completion_percentage === 100 ? '#059669' : '#475569' }}>
                    %{sp.completion_percentage}
                  </span>
                </div>
                <div style={{ width: '100%', height: '4px', background: '#e2e8f0', borderRadius: '2px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${sp.completion_percentage}%`,
                      height: '100%',
                      background: sp.has_errors ? '#ef4444' : sp.completion_percentage === 100 ? '#10b981' : '#3b82f6',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
