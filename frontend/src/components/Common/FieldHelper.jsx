import React, { useState } from 'react';
import { FileText, BookOpen } from 'lucide-react';
import PhrasePickerModal from './PhrasePickerModal';

export default function FieldHelper({
  legalRef,
  tooltip,
  onInsertText,
  templates = ['Uygulanabilir değildir.', 'Mevcut veri bulunmamaktadır.'],
  section = '',
  fieldLabel = '',
}) {
  const [isPhraseModalOpen, setIsPhraseModalOpen] = useState(false);

  return (
    <div style={{ marginTop: '4px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {legalRef && (
            <span className="form-help" style={{ color: '#0284c7' }}>
              <FileText size={12} />
              {legalRef}
            </span>
          )}

          {/* EuPhraC Standart Cümle Seçici Butonu */}
          {onInsertText && (
            <button
              type="button"
              className="quick-tag-btn"
              style={{
                background: '#f0f9ff',
                borderColor: '#bae6fd',
                color: '#0284c7',
                fontWeight: 600,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
              }}
              onClick={() => setIsPhraseModalOpen(true)}
              title="EuPhraC uyumlu resmi standart kimya ifadeleri kütüphanesinden seç"
            >
              <BookOpen size={12} />
              Standart İfade Seç
            </button>
          )}
        </div>

        {onInsertText && templates.length > 0 && (
          <div className="helper-quick-tags">
            {templates.map((tpl, idx) => (
              <button
                key={idx}
                type="button"
                className="quick-tag-btn"
                onClick={() => onInsertText(tpl)}
                title="Bu metni alana hızlıca yerleştir"
              >
                + {tpl}
              </button>
            ))}
          </div>
        )}
      </div>

      {tooltip && (
        <div style={{ fontSize: '0.76rem', color: '#64748b', marginTop: '2px' }}>
          {tooltip}
        </div>
      )}

      {/* Standart İfade Seçim Modal */}
      {isPhraseModalOpen && (
        <PhrasePickerModal
          isOpen={isPhraseModalOpen}
          onClose={() => setIsPhraseModalOpen(false)}
          onSelect={(selectedText) => onInsertText(selectedText)}
          initialSection={section}
          fieldLabel={fieldLabel}
        />
      )}
    </div>
  );
}

