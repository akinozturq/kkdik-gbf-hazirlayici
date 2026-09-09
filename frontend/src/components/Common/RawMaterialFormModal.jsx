import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { X, Save, Sparkles, AlertTriangle, Package, Check, Shield } from 'lucide-react';

const ALL_PICTOGRAMS = [
  { code: 'GHS01', name: 'Patlayıcı' },
  { code: 'GHS02', name: 'Alevlenir' },
  { code: 'GHS03', name: 'Oksitleyici' },
  { code: 'GHS04', name: 'Gaz Tüpü' },
  { code: 'GHS05', name: 'Aşındırıcı (Korozif)' },
  { code: 'GHS06', name: 'Toksik (Zehirli)' },
  { code: 'GHS07', name: 'Zararlı / Tahriş Edici' },
  { code: 'GHS08', name: 'Sağlık Zararı (Kanserojen/Aspirasyon)' },
  { code: 'GHS09', name: 'Çevre İçin Zararlı' },
];

const CATEGORIES = [
  'Solventler / Aromatik Hidrokarbonlar',
  'Solventler / Esterler',
  'Solventler / Ketonlar',
  'Solventler / Alkoller',
  'Solventler / Alifatik Hidrokarbonlar',
  'Solventler / Glikol Eterler',
  'Sertleştiriciler / Alifatik İzosiyanatlar',
  'Sertleştiriciler / Aromatik İzosiyanatlar',
  'Reçineler / Akrilik',
  'Reçineler / Alkid',
  'Reçineler / Epoksi',
  'Reçineler / Poliüretan',
  'Pigmentler & Dolgular',
  'Katkılar & Kurutucular',
  'Genel Kimyasallar',
];

export default function RawMaterialFormModal({ isOpen, onClose, initialData, onSaved }) {
  const isEditing = Boolean(initialData?.id);
  const [activeTab, setActiveTab] = useState('genel');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    ad: '',
    ticari_ad: '',
    iupac_adi: '',
    cas_no: '',
    ec_no: '',
    kayit_no: '',
    molekul_formulu: '',
    molekul_agirligi: '',
    kategori: 'Solventler / Aromatik Hidrokarbonlar',
    fiziksel_hal: 'Sıvı',
    siniflandirma_str: '',
    h_kodlari: [],
    piktogramlar: [],
    uyari_kelimesi: 'Tehlike',
    is_isocyanate: false,
    akut_toksisite_oral: '',
    akut_toksisite_dermal: '',
    akut_toksisite_soluma: '',
    akut_toksisite_soluma_formu: 'buhar',
    m_faktoru_akut: '',
    m_faktoru_kronik: '',
    maruziyet_limitleri: {
      twa_ppm: '',
      twa_mg_m3: '',
      stel_ppm: '',
      stel_mg_m3: '',
      notes: '',
    },
    fiziksel_ozellikler: {
      parlama_noktasi: '',
      kaynama_noktasi: '',
      erime_noktasi: '',
      yogunluk: '',
      buhar_basinci: '',
      patlama_alt_ust_limit: '',
      kendiliginden_tutusma: '',
      cozunurluk: '',
    },
    toksikolojik_bilgiler: {
      akut_oral_ld50: '',
      akut_dermal_ld50: '',
      akut_soluma_lc50: '',
      cilt_goz_etkisi: '',
      stot_se: '',
      ilave_etiket: '',
    },
    ekolojik_bilgiler: {
      balik_toksisitesi: '',
      su_piresi_toksisitesi: '',
      biyobirikim: '',
      kalicilik: '',
    },
    tasimacilik_bilgileri: {
      un_no: '',
      uygun_tasima_adi: '',
      sinif: '',
      ambalaj_grubu: '',
    },
  });

  useEffect(() => {
    if (isOpen) {
      setError(null);
      setActiveTab('genel');
      if (initialData) {
        setFormData({
          ad: initialData.ad || '',
          ticari_ad: initialData.ticari_ad || '',
          iupac_adi: initialData.iupac_adi || '',
          cas_no: initialData.cas_no || '',
          ec_no: initialData.ec_no || '',
          kayit_no: initialData.kayit_no || '',
          molekul_formulu: initialData.molekul_formulu || '',
          molekul_agirligi: initialData.molekul_agirligi || '',
          kategori: initialData.kategori || 'Genel Kimyasallar',
          fiziksel_hal: initialData.fiziksel_hal || 'Sıvı',
          siniflandirma_str: initialData.siniflandirma_str || '',
          h_kodlari: initialData.h_kodlari || [],
          piktogramlar: initialData.piktogramlar || [],
          uyari_kelimesi: initialData.uyari_kelimesi || 'Tehlike',
          is_isocyanate: Boolean(initialData.is_isocyanate),
          akut_toksisite_oral: initialData.akut_toksisite_oral ?? '',
          akut_toksisite_dermal: initialData.akut_toksisite_dermal ?? '',
          akut_toksisite_soluma: initialData.akut_toksisite_soluma ?? '',
          akut_toksisite_soluma_formu: initialData.akut_toksisite_soluma_formu || 'buhar',
          m_faktoru_akut: initialData.m_faktoru_akut ?? '',
          m_faktoru_kronik: initialData.m_faktoru_kronik ?? '',
          maruziyet_limitleri: {
            twa_ppm: initialData.maruziyet_limitleri?.twa_ppm || '',
            twa_mg_m3: initialData.maruziyet_limitleri?.twa_mg_m3 || '',
            stel_ppm: initialData.maruziyet_limitleri?.stel_ppm || '',
            stel_mg_m3: initialData.maruziyet_limitleri?.stel_mg_m3 || '',
            notes: initialData.maruziyet_limitleri?.notes || '',
          },
          fiziksel_ozellikler: {
            parlama_noktasi: initialData.fiziksel_ozellikler?.parlama_noktasi || '',
            kaynama_noktasi: initialData.fiziksel_ozellikler?.kaynama_noktasi || '',
            erime_noktasi: initialData.fiziksel_ozellikler?.erime_noktasi || '',
            yogunluk: initialData.fiziksel_ozellikler?.yogunluk || '',
            buhar_basinci: initialData.fiziksel_ozellikler?.buhar_basinci || '',
            patlama_alt_ust_limit: initialData.fiziksel_ozellikler?.patlama_alt_ust_limit || '',
            kendiliginden_tutusma: initialData.fiziksel_ozellikler?.kendiliginden_tutusma || '',
            cozunurluk: initialData.fiziksel_ozellikler?.cozunurluk || '',
          },
          toksikolojik_bilgiler: {
            akut_oral_ld50: initialData.toksikolojik_bilgiler?.akut_oral_ld50 || '',
            akut_dermal_ld50: initialData.toksikolojik_bilgiler?.akut_dermal_ld50 || '',
            akut_soluma_lc50: initialData.toksikolojik_bilgiler?.akut_soluma_lc50 || '',
            cilt_goz_etkisi: initialData.toksikolojik_bilgiler?.cilt_goz_etkisi || '',
            stot_se: initialData.toksikolojik_bilgiler?.stot_se || '',
            ilave_etiket: initialData.toksikolojik_bilgiler?.ilave_etiket || '',
          },
          ekolojik_bilgiler: {
            balik_toksisitesi: initialData.ekolojik_bilgiler?.balik_toksisitesi || '',
            su_piresi_toksisitesi: initialData.ekolojik_bilgiler?.su_piresi_toksisitesi || '',
            biyobirikim: initialData.ekolojik_bilgiler?.biyobirikim || '',
            kalicilik: initialData.ekolojik_bilgiler?.kalicilik || '',
          },
          tasimacilik_bilgileri: {
            un_no: initialData.tasimacilik_bilgileri?.un_no || '',
            uygun_tasima_adi: initialData.tasimacilik_bilgileri?.uygun_tasima_adi || '',
            sinif: initialData.tasimacilik_bilgileri?.sinif || '',
            ambalaj_grubu: initialData.tasimacilik_bilgileri?.ambalaj_grubu || '',
          },
        });
      } else {
        setFormData({
          ad: '',
          ticari_ad: '',
          iupac_adi: '',
          cas_no: '',
          ec_no: '',
          kayit_no: '',
          molekul_formulu: '',
          molekul_agirligi: '',
          kategori: 'Solventler / Aromatik Hidrokarbonlar',
          fiziksel_hal: 'Sıvı',
          siniflandirma_str: '',
          h_kodlari: [],
          piktogramlar: [],
          uyari_kelimesi: 'Tehlike',
          is_isocyanate: false,
          akut_toksisite_oral: '',
          akut_toksisite_dermal: '',
          akut_toksisite_soluma: '',
          akut_toksisite_soluma_formu: 'buhar',
          m_faktoru_akut: '',
          m_faktoru_kronik: '',
          maruziyet_limitleri: {
            twa_ppm: '',
            twa_mg_m3: '',
            stel_ppm: '',
            stel_mg_m3: '',
            notes: '',
          },
          fiziksel_ozellikler: {
            parlama_noktasi: '',
            kaynama_noktasi: '',
            erime_noktasi: '',
            yogunluk: '',
            buhar_basinci: '',
            patlama_alt_ust_limit: '',
            kendiliginden_tutusma: '',
            cozunurluk: '',
          },
          toksikolojik_bilgiler: {
            akut_oral_ld50: '',
            akut_dermal_ld50: '',
            akut_soluma_lc50: '',
            cilt_goz_etkisi: '',
            stot_se: '',
            ilave_etiket: '',
          },
          ekolojik_bilgiler: {
            balik_toksisitesi: '',
            su_piresi_toksisitesi: '',
            biyobirikim: '',
            kalicilik: '',
          },
          tasimacilik_bilgileri: {
            un_no: '',
            uygun_tasima_adi: '',
            sinif: '',
            ambalaj_grubu: '',
          },
        });
      }
    }
  }, [isOpen, initialData]);

  if (!isOpen) return null;

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleNestedChange = (parent, field, value) => {
    setFormData((prev) => ({
      ...prev,
      [parent]: {
        ...prev[parent],
        [field]: value,
      },
    }));
  };

  const togglePictogram = (code) => {
    setFormData((prev) => {
      const exists = prev.piktogramlar.includes(code);
      const updated = exists
        ? prev.piktogramlar.filter((p) => p !== code)
        : [...prev.piktogramlar, code];
      return { ...prev, piktogramlar: updated };
    });
  };

  const autoParseClassification = () => {
    const text = formData.siniflandirma_str || '';
    const hRegex = /\b(H\d{3}[a-zA-Z]*|EUH\d{3})\b/gi;
    const matches = text.match(hRegex);
    if (matches) {
      const uniqueH = Array.from(new Set(matches.map((m) => m.toUpperCase())));
      
      // Auto-infer pictograms
      const pics = new Set(formData.piktogramlar);
      uniqueH.forEach((code) => {
        if (['H220', 'H221', 'H222', 'H223', 'H224', 'H225', 'H226', 'H228'].includes(code)) pics.add('GHS02');
        if (['H270', 'H271', 'H272'].includes(code)) pics.add('GHS03');
        if (['H314', 'H318', 'H290'].includes(code)) pics.add('GHS05');
        if (['H300', 'H301', 'H310', 'H311', 'H330', 'H331'].includes(code)) pics.add('GHS06');
        if (['H302', 'H312', 'H332', 'H315', 'H319', 'H317', 'H335', 'H336'].includes(code)) pics.add('GHS07');
        if (['H304', 'H334', 'H340', 'H341', 'H350', 'H351', 'H360', 'H361', 'H370', 'H371', 'H372', 'H373'].includes(code)) pics.add('GHS08');
        if (['H400', 'H410', 'H411'].includes(code)) pics.add('GHS09');
      });

      setFormData((prev) => ({
        ...prev,
        h_kodlari: uniqueH,
        piktogramlar: Array.from(pics),
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.ad.trim()) {
      setError('Hammadde adı zorunludur.');
      setActiveTab('genel');
      return;
    }

    setLoading(true);
    setError(null);

    const payload = {
      ...formData,
      akut_toksisite_oral: formData.akut_toksisite_oral !== '' ? Number(formData.akut_toksisite_oral) : null,
      akut_toksisite_dermal: formData.akut_toksisite_dermal !== '' ? Number(formData.akut_toksisite_dermal) : null,
      akut_toksisite_soluma: formData.akut_toksisite_soluma !== '' ? Number(formData.akut_toksisite_soluma) : null,
      m_faktoru_akut: formData.m_faktoru_akut !== '' ? Number(formData.m_faktoru_akut) : null,
      m_faktoru_kronik: formData.m_faktoru_kronik !== '' ? Number(formData.m_faktoru_kronik) : null,
    };

    try {
      let saved;
      if (isEditing) {
        saved = await api.updateRawMaterial(initialData.id, payload);
      } else {
        saved = await api.createRawMaterial(payload);
      }
      if (onSaved) onSaved(saved);
      onClose();
    } catch (err) {
      console.error('Hammadde kaydedilemedi:', err);
      setError(err.message || 'Hammadde kaydedilirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 10000 }}>
      <div
        className="modal-content"
        style={{ maxWidth: '840px', width: '95%', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="modal-header" style={{ padding: '16px 24px', background: '#f8fafc' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '10px',
                background: isEditing
                  ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                  : 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 10px rgba(0,0,0,0.15)',
              }}
            >
              <Package size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#0f172a' }}>
                {isEditing ? `Hammaddeyi Düzenle: ${initialData.ad}` : 'Yeni Kimyasal Hammadde Ekle'}
              </h3>
              <p style={{ margin: '2px 0 0', fontSize: '0.8rem', color: '#64748b' }}>
                Formülasyon ve GBF hesaplama motorunda kullanılacak kimyasal & mevzuat parametreleri
              </p>
            </div>
          </div>
          <button className="btn btn-secondary btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Tab Navigation */}
        <div style={{ display: 'flex', background: '#ffffff', borderBottom: '1px solid #e2e8f0', padding: '0 24px', gap: '8px' }}>
          {[
            { key: 'genel', label: '1. Kimlik & Genel' },
            { key: 'zararlilik', label: '2. Sınıflandırma (SEA)' },
            { key: 'fiziksel', label: '3. Fiziksel Özellikler' },
            { key: 'toksikoloji', label: '4. Toksisite & Limitler' },
            { key: 'tasimacilik', label: '5. Taşımacılık (ADR)' },
          ].map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key)}
              style={{
                padding: '12px 14px',
                fontSize: '0.84rem',
                fontWeight: activeTab === tab.key ? 700 : 500,
                color: activeTab === tab.key ? '#0284c7' : '#64748b',
                border: 'none',
                background: 'transparent',
                borderBottom: activeTab === tab.key ? '2px solid #0284c7' : '2px solid transparent',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Error Alert */}
        {error && (
          <div style={{ margin: '16px 24px 0', padding: '10px 16px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#b91c1c', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Modal Form Body */}
        <form onSubmit={handleSubmit} style={{ flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column' }}>
          {/* TAB 1: Genel & Kimlik */}
          {activeTab === 'genel' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
                <div>
                  <label className="form-label" style={{ fontWeight: 700 }}>
                    Kimyasal / Hammadde Adı <span style={{ color: '#ef4444' }}>*</span>
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. Aseton, Toluen, Heksametilen Diizosiyanat Oligomeri"
                    value={formData.ad}
                    onChange={(e) => handleChange('ad', e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="form-label" style={{ fontWeight: 700 }}>
                    Kategori
                  </label>
                  <input
                    type="text"
                    list="category-suggestions"
                    className="form-control"
                    value={formData.kategori}
                    onChange={(e) => handleChange('kategori', e.target.value)}
                    placeholder="Kategori seçin veya yazın..."
                  />
                  <datalist id="category-suggestions">
                    {CATEGORIES.map((c) => (
                      <option key={c} value={c} />
                    ))}
                  </datalist>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label className="form-label">Ticari Ad / Formülasyon Kodu</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. MEK, Desmodur N 3300, Shellsol A"
                    value={formData.ticari_ad}
                    onChange={(e) => handleChange('ticari_ad', e.target.value)}
                  />
                </div>
                <div>
                  <label className="form-label">IUPAC / Sistematik Adı</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. Propan-2-on, Metilbenzen"
                    value={formData.iupac_adi}
                    onChange={(e) => handleChange('iupac_adi', e.target.value)}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                <div>
                  <label className="form-label" style={{ fontWeight: 700 }}>CAS Numarası</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. 67-64-1, 108-88-3"
                    value={formData.cas_no}
                    onChange={(e) => handleChange('cas_no', e.target.value)}
                  />
                </div>
                <div>
                  <label className="form-label" style={{ fontWeight: 700 }}>EC / EINECS No</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. 200-662-2"
                    value={formData.ec_no}
                    onChange={(e) => handleChange('ec_no', e.target.value)}
                  />
                </div>
                <div>
                  <label className="form-label">KKDİK / REACH Kayıt No</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="01-2119471330-49-XXXX"
                    value={formData.kayit_no}
                    onChange={(e) => handleChange('kayit_no', e.target.value)}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                <div>
                  <label className="form-label">Molekül Formülü</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="C3H6O, C7H8"
                    value={formData.molekul_formulu}
                    onChange={(e) => handleChange('molekul_formulu', e.target.value)}
                  />
                </div>
                <div>
                  <label className="form-label">Molekül Ağırlığı</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="58.08 g/mol"
                    value={formData.molekul_agirligi}
                    onChange={(e) => handleChange('molekul_agirligi', e.target.value)}
                  />
                </div>
                <div>
                  <label className="form-label">Fiziksel Hal & Görünüm</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Sıvı (Renksiz, karakteristik)"
                    value={formData.fiziksel_hal}
                    onChange={(e) => handleChange('fiziksel_hal', e.target.value)}
                  />
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Zararlılık & Sınıflandırma */}
          {activeTab === 'zararlilik' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <label className="form-label" style={{ fontWeight: 700, margin: 0 }}>
                    SEA / CLP Sınıflandırma Metni
                  </label>
                  <button
                    type="button"
                    className="btn btn-sm btn-secondary"
                    onClick={autoParseClassification}
                    title="Metindeki H-kodlarını ve GHS piktogramlarını otomatik ayrıştırır"
                    style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px', padding: '3px 8px' }}
                  >
                    <Sparkles size={13} color="#0284c7" />
                    Kodları ve Piktogramları Otomatik Çıkar
                  </button>
                </div>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Ör. Flam. Liq. 2 H225, Eye Irrit. 2 H319, STOT SE 3 H336, EUH066"
                  value={formData.siniflandirma_str}
                  onChange={(e) => handleChange('siniflandirma_str', e.target.value)}
                  onBlur={autoParseClassification}
                />
                <span style={{ fontSize: '0.74rem', color: '#64748b', marginTop: '4px', display: 'block' }}>
                  Sınıflandırma dizesini girdiğinizde sistem otomatik olarak H-kodlarını ve ilgili GHS piktogramlarını eşler.
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label className="form-label" style={{ fontWeight: 700 }}>
                    Uyarı Kelimesi
                  </label>
                  <select
                    className="form-control"
                    value={formData.uyari_kelimesi}
                    onChange={(e) => handleChange('uyari_kelimesi', e.target.value)}
                  >
                    <option value="Tehlike">Tehlike (Danger)</option>
                    <option value="Uyarı">Uyarı (Warning)</option>
                    <option value="Yok">Zararsız / Yok</option>
                  </select>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', marginTop: '24px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.88rem', fontWeight: 600, color: '#0f172a' }}>
                    <input
                      type="checkbox"
                      checked={formData.is_isocyanate}
                      onChange={(e) => handleChange('is_isocyanate', e.target.checked)}
                      style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                    />
                    İzosiyanat İçerir (EUH204 Zorunlu Etiketi Tetikler)
                  </label>
                </div>
              </div>

              {/* Pictogram Picker */}
              <div>
                <label className="form-label" style={{ fontWeight: 700, marginBottom: '8px' }}>
                  GHS Tehlike Piktogramları
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                  {ALL_PICTOGRAMS.map((pic) => {
                    const isSelected = formData.piktogramlar.includes(pic.code);
                    return (
                      <div
                        key={pic.code}
                        onClick={() => togglePictogram(pic.code)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          padding: '8px 12px',
                          border: isSelected ? '2px solid #0284c7' : '1px solid #e2e8f0',
                          borderRadius: '8px',
                          background: isSelected ? '#f0f9ff' : '#ffffff',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        <img
                          src={`/pictograms/${pic.code.toLowerCase()}.svg`}
                          alt={pic.code}
                          style={{ width: '28px', height: '28px', objectFit: 'contain' }}
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = `/pictograms/${pic.code.toLowerCase()}.png`;
                          }}
                        />
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#0f172a' }}>{pic.code}</div>
                          <div style={{ fontSize: '0.72rem', color: '#64748b' }}>{pic.name}</div>
                        </div>
                        {isSelected && <Check size={16} color="#0284c7" />}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Fiziksel Özellikler */}
          {activeTab === 'fiziksel' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label className="form-label">Parlama Noktası</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. -20 °C, 25 °C, > 100 °C"
                    value={formData.fiziksel_ozellikler.parlama_noktasi}
                    onChange={(e) => handleNestedChange('fiziksel_ozellikler', 'parlama_noktasi', e.target.value)}
                  />
                </div>
                <div>
                  <label className="form-label">Kaynama Noktası</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. 56 °C, 110.6 °C"
                    value={formData.fiziksel_ozellikler.kaynama_noktasi}
                    onChange={(e) => handleNestedChange('fiziksel_ozellikler', 'kaynama_noktasi', e.target.value)}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label className="form-label">Yoğunluk (20 °C)</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. 0.791 g/cm³, 1.16 g/cm³"
                    value={formData.fiziksel_ozellikler.yogunluk}
                    onChange={(e) => handleNestedChange('fiziksel_ozellikler', 'yogunluk', e.target.value)}
                  />
                </div>
                <div>
                  <label className="form-label">Buhar Basıncı (20 °C)</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. 24.5 kPa, 29 hPa"
                    value={formData.fiziksel_ozellikler.buhar_basinci}
                    onChange={(e) => handleNestedChange('fiziksel_ozellikler', 'buhar_basinci', e.target.value)}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label className="form-label">Patlama Alt / Üst Sınırları (% Hacim)</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. %1.1 - %7.1"
                    value={formData.fiziksel_ozellikler.patlama_alt_ust_limit}
                    onChange={(e) => handleNestedChange('fiziksel_ozellikler', 'patlama_alt_ust_limit', e.target.value)}
                  />
                </div>
                <div>
                  <label className="form-label">Kendiliğinden Tutuşma Sıcaklığı</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. 465 °C, 480 °C"
                    value={formData.fiziksel_ozellikler.kendiliginden_tutusma}
                    onChange={(e) => handleNestedChange('fiziksel_ozellikler', 'kendiliginden_tutusma', e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="form-label">Çözünürlük (Su ve Çözücülerde)</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Ör. Suda pratik olarak çözünmez, organik solventlerde tamamen karışır"
                  value={formData.fiziksel_ozellikler.cozunurluk}
                  onChange={(e) => handleNestedChange('fiziksel_ozellikler', 'cozunurluk', e.target.value)}
                />
              </div>
            </div>
          )}

          {/* TAB 4: Toksisite & Limitler */}
          {activeTab === 'toksikoloji' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h4 style={{ margin: '0 0 10px', fontSize: '0.9rem', fontWeight: 800, color: '#0f172a' }}>
                  Akut Toksisite Tahmini (ATE) Sayısal Değerleri (GBF Karışım Motoru İçin)
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '12px' }}>
                  <div>
                    <label className="form-label">Oral LD50 (mg/kg)</label>
                    <input
                      type="number"
                      step="any"
                      className="form-control"
                      placeholder="Ör. 5800"
                      value={formData.akut_toksisite_oral}
                      onChange={(e) => handleChange('akut_toksisite_oral', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="form-label">Dermal LD50 (mg/kg)</label>
                    <input
                      type="number"
                      step="any"
                      className="form-control"
                      placeholder="Ör. 12126"
                      value={formData.akut_toksisite_dermal}
                      onChange={(e) => handleChange('akut_toksisite_dermal', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="form-label">Soluma LC50 (mg/L)</label>
                    <input
                      type="number"
                      step="any"
                      className="form-control"
                      placeholder="Ör. 20.0 veya 1.5"
                      value={formData.akut_toksisite_soluma}
                      onChange={(e) => handleChange('akut_toksisite_soluma', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="form-label">Soluma Formu</label>
                    <select
                      className="form-control"
                      value={formData.akut_toksisite_soluma_formu}
                      onChange={(e) => handleChange('akut_toksisite_soluma_formu', e.target.value)}
                    >
                      <option value="buhar">Buhar (mg/L)</option>
                      <option value="toz_sis">Toz / Sis (Aerosol mg/L)</option>
                      <option value="gaz">Gaz (ppm)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Mesleki Maruziyet Limitleri */}
              <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <h4 style={{ margin: '0 0 10px', fontSize: '0.9rem', fontWeight: 800, color: '#0f172a' }}>
                  Mesleki Maruziyet Sınır Değerleri (OEL / Bölüm 8.1)
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '12px' }}>
                  <div>
                    <label className="form-label">TWA (ppm)</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Ör. 50"
                      value={formData.maruziyet_limitleri.twa_ppm}
                      onChange={(e) => handleNestedChange('maruziyet_limitleri', 'twa_ppm', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="form-label">TWA (mg/m³)</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Ör. 192"
                      value={formData.maruziyet_limitleri.twa_mg_m3}
                      onChange={(e) => handleNestedChange('maruziyet_limitleri', 'twa_mg_m3', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="form-label">STEL (ppm)</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Ör. 100"
                      value={formData.maruziyet_limitleri.stel_ppm}
                      onChange={(e) => handleNestedChange('maruziyet_limitleri', 'stel_ppm', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="form-label">STEL (mg/m³)</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Ör. 384"
                      value={formData.maruziyet_limitleri.stel_mg_m3}
                      onChange={(e) => handleNestedChange('maruziyet_limitleri', 'stel_mg_m3', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: Taşımacılık (ADR) */}
          {activeTab === 'tasimacilik' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '16px' }}>
                <div>
                  <label className="form-label" style={{ fontWeight: 700 }}>UN Numarası</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. UN 1263, UN 1090"
                    value={formData.tasimacilik_bilgileri.un_no}
                    onChange={(e) => handleNestedChange('tasimacilik_bilgileri', 'un_no', e.target.value)}
                  />
                </div>
                <div>
                  <label className="form-label" style={{ fontWeight: 700 }}>Uygun Sevkiyat Adı (Proper Shipping Name)</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. BOYA İLE İLGİLİ MALZEME veya ASETON"
                    value={formData.tasimacilik_bilgileri.uygun_tasima_adi}
                    onChange={(e) => handleNestedChange('tasimacilik_bilgileri', 'uygun_tasima_adi', e.target.value)}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label className="form-label">Taşımacılık Sınıfı</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Ör. 3 (Alevlenir Sıvılar)"
                    value={formData.tasimacilik_bilgileri.sinif}
                    onChange={(e) => handleNestedChange('tasimacilik_bilgileri', 'sinif', e.target.value)}
                  />
                </div>
                <div>
                  <label className="form-label">Paketleme / Ambalaj Grubu</label>
                  <select
                    className="form-control"
                    value={formData.tasimacilik_bilgileri.ambalaj_grubu}
                    onChange={(e) => handleNestedChange('tasimacilik_bilgileri', 'ambalaj_grubu', e.target.value)}
                  >
                    <option value="">Seçiniz...</option>
                    <option value="PG I">PG I (Yüksek Tehlike)</option>
                    <option value="PG II">PG II (Orta Tehlike)</option>
                    <option value="PG III">PG III (Düşük Tehlike)</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Form Actions / Footer */}
          <div style={{ marginTop: 'auto', paddingTop: '20px', display: 'flex', justifyContent: 'flex-end', gap: '10px', borderTop: '1px solid #e2e8f0' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              İptal
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{
                background: isEditing
                  ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                  : 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontWeight: 700,
                minWidth: '120px',
                justifyContent: 'center',
              }}
            >
              <Save size={16} />
              <span>{loading ? 'Kaydediliyor...' : isEditing ? 'Değişiklikleri Kaydet' : 'Kütüphaneye Ekle'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
