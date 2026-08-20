import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import {
  X,
  Sparkles,
  Key,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  ShieldCheck,
  Zap,
  Eye,
  EyeOff,
} from 'lucide-react';

export default function AiSettingsModal({ isOpen, onClose }) {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gemini-3.5-flash-lite');
  const [isConfigured, setIsConfigured] = useState(false);
  const [maskedKey, setMaskedKey] = useState('');
  const [supportedModels, setSupportedModels] = useState([]);
  const [showKey, setShowKey] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadConfig();
      setTestResult(null);
      setSaveSuccess(false);
    }
  }, [isOpen]);

  const loadConfig = async () => {
    try {
      const data = await api.getAiConfig();
      setIsConfigured(data.is_configured);
      setMaskedKey(data.api_key_masked || '');
      setModel(data.active_model || 'gemini-3.5-flash-lite');
      setSupportedModels(data.supported_models || []);
    } catch (err) {
      console.error('AI Ayarları yükleme hatası:', err);
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await api.testAiConnection({
        api_key: apiKey.trim() || undefined,
        model: model,
      });
      setTestResult(res);
    } catch (err) {
      setTestResult({
        success: false,
        message: 'Bağlantı hatası: ' + err.message,
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    try {
      await api.saveAiConfig({
        api_key: apiKey.trim() || undefined,
        model: model,
      });
      setSaveSuccess(true);
      await loadConfig();
      setApiKey('');
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    } catch (err) {
      alert('Ayarlar kaydedilemedi: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: '580px' }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
              }}
            >
              <Sparkles size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0 }}>
                Google Gemini AI Ayarları
              </h3>
              <p style={{ fontSize: '0.76rem', color: '#64748b', margin: 0 }}>
                Hibrit Çeviri & Kimyasal Mevzuat Motoru
              </p>
            </div>
          </div>
          <button type="button" className="btn btn-secondary btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSave}>
          <div className="modal-body">
            {/* Status Banner */}
            <div
              style={{
                padding: '12px 14px',
                borderRadius: '8px',
                marginBottom: '16px',
                background: isConfigured ? '#ecfdf5' : '#eff6ff',
                border: '1px solid',
                borderColor: isConfigured ? '#a7f3d0' : '#bfdbfe',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {isConfigured ? (
                  <ShieldCheck size={18} color="#059669" />
                ) : (
                  <Zap size={18} color="#2563eb" />
                )}
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.84rem', color: isConfigured ? '#065f46' : '#1e40af' }}>
                    {isConfigured ? 'Gemini AI Yapılandırıldı (Aktif)' : 'Gemini AI Yapılandırılmadı'}
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#64748b' }}>
                    {isConfigured
                      ? `API Anahtarı: ${maskedKey} • Model: ${model}`
                      : 'Kural tabanlı REACH Annex II sözlüğü ile çalışıyor.'}
                  </div>
                </div>
              </div>
            </div>

            {/* Model Selection */}
            <div className="form-group" style={{ marginBottom: '16px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '0.84rem' }}>
                <Cpu size={15} color="#2563eb" />
                Kullanılacak Gemini Modeli:
              </label>
              <select
                className="form-control"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                style={{ fontWeight: 600 }}
              >
                {supportedModels && supportedModels.length > 0 ? (
                  supportedModels.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))
                ) : (
                  <>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash (En Kararlı & Ücretsiz Kotaya Uygun)</option>
                    <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                    <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                    <option value="gemini-3.5-flash-lite">Gemini 3.5 Flash Lite</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                  </>
                )}
              </select>
              <p style={{ fontSize: '0.73rem', color: '#64748b', marginTop: '4px' }}>
                💡 <b>İpucu:</b> <code>gemini-1.5-flash</code> modeli Google AI Studio ücretsiz planında en kararlı çalışan ve günlük 1.500 istek kotası veren modeldir.
              </p>
            </div>

            {/* API Key Input */}
            <div className="form-group" style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '0.84rem', margin: 0 }}>
                  <Key size={15} color="#2563eb" />
                  Google Gemini API Anahtarı:
                </label>
                <a
                  href="https://aistudio.google.com/app/apikey"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    fontSize: '0.74rem',
                    color: '#2563eb',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    textDecoration: 'none',
                    fontWeight: 600,
                  }}
                >
                  Ücretsiz API Key Al
                  <ExternalLink size={12} />
                </a>
              </div>

              <div style={{ position: 'relative' }}>
                <input
                  type={showKey ? 'text' : 'password'}
                  className="form-control"
                  placeholder={isConfigured ? `Mevcut Key (${maskedKey}) — Değiştirmek için yazın` : 'AIzaSy...'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  style={{ paddingRight: '40px', fontFamily: 'monospace' }}
                />
                <button
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  style={{
                    position: 'absolute',
                    right: '10px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'transparent',
                    border: 'none',
                    color: '#94a3b8',
                    cursor: 'pointer',
                    display: 'flex',
                  }}
                >
                  {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Test Connection Button & Result */}
            <div style={{ marginBottom: '16px' }}>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={handleTestConnection}
                disabled={testing || (!apiKey && !isConfigured)}
                style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
              >
                <Zap size={14} color="#f59e0b" />
                {testing ? 'Bağlantı Test Ediliyor...' : 'API Bağlantısını Test Et'}
              </button>

              {testResult && (
                <div
                  style={{
                    marginTop: '10px',
                    padding: '10px 12px',
                    borderRadius: '6px',
                    background: testResult.success ? '#ecfdf5' : '#fef2f2',
                    border: '1px solid',
                    borderColor: testResult.success ? '#a7f3d0' : '#fecaca',
                    color: testResult.success ? '#065f46' : '#991b1b',
                    fontSize: '0.8rem',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '8px',
                  }}
                >
                  {testResult.success ? (
                    <CheckCircle2 size={16} color="#059669" style={{ flexShrink: 0, marginTop: '2px' }} />
                  ) : (
                    <AlertTriangle size={16} color="#dc2626" style={{ flexShrink: 0, marginTop: '2px' }} />
                  )}
                  <div>
                    <div>{testResult.message}</div>
                    {testResult.response_sample && (
                      <div style={{ fontSize: '0.72rem', color: '#047857', marginTop: '2px' }}>
                        Örnek Çeviri: <i>"{testResult.response_sample}"</i>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Free Tier Info Box */}
            <div
              style={{
                padding: '12px',
                borderRadius: '8px',
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                fontSize: '0.74rem',
                color: '#475569',
                lineHeight: 1.45,
              }}
            >
              <div style={{ fontWeight: 700, color: '#1e293b', marginBottom: '4px' }}>
                ℹ️ Google AI Studio Ücretsiz Kotası:
              </div>
              <ul style={{ margin: 0, paddingLeft: '18px' }}>
                <li>Günde <b>1.500 istek</b> tamamen ücretsizdir.</li>
                <li>Hibrit mimari sayesinde 16 ana başlık ve CLP kodları API kotasını tüketmez.</li>
                <li>Günde 10 doküman çevirisi aylık <b>0,00 TL</b> tutacaktır.</li>
              </ul>
            </div>

            {saveSuccess && (
              <div
                style={{
                  marginTop: '12px',
                  padding: '10px',
                  borderRadius: '6px',
                  background: '#ecfdf5',
                  color: '#065f46',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  textAlign: 'center',
                }}
              >
                ✓ Ayarlar başarıyla kaydedildi ve uygulandı.
              </div>
            )}
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Kapat
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={saving}
            >
              {saving ? 'Kaydediliyor...' : 'Kaydet ve Uygula'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
