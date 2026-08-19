import React from 'react';
import { HelpCircle, FileText } from 'lucide-react';

export default function FieldHelper({
  legalRef,
  tooltip,
  onInsertText,
  templates = ['Uygulanabilir değildir.', 'Mevcut veri bulunmamaktadır.'],
}) {
  return (
    <div style={{ marginTop: '4px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
        {legalRef && (
          <span className="form-help" style={{ color: '#0284c7' }}>
            <FileText size={12} />
            {legalRef}
          </span>
        )}

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
    </div>
  );
}
