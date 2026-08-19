import React, { useState } from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';
import HazardCalculationModal from '../HazardCalculationModal';
import { Plus, Trash2, Layers, Atom, Calculator } from 'lucide-react';

export default function Step3_Bilesim() {
  const { sdsData, updateSdsField } = useApp();
  const [isHazardModalOpen, setIsHazardModalOpen] = useState(false);

  const b3 = sdsData?.b3_bilesim || {};
  const tip = b3.tip || 'karisim';
  const madde = b3.madde || {};
  const karisim = b3.karisim || {};
  const bilesenler = karisim.bilesenler || [];

  // Toggle Type (Madde vs Karışım)
  const handleTypeChange = (newTip) => {
    updateSdsField(['b3_bilesim', 'tip'], newTip);
  };

  // Add Component Row
  const addComponentRow = () => {
    const updated = [
      ...bilesenler,
      {
        ad: '',
        cas_no: '',
        ec_no: '',
        kayit_no: '',
        konsantrasyon: '',
        siniflandirma: '',
      },
    ];
    updateSdsField(['b3_bilesim', 'karisim', 'bilesenler'], updated);
  };

  // Remove Component Row
  const removeComponentRow = (index) => {
    const updated = bilesenler.filter((_, i) => i !== index);
    updateSdsField(['b3_bilesim', 'karisim', 'bilesenler'], updated);
  };

  // Update Component Field
  const updateComponentField = (index, field, value) => {
    const updated = [...bilesenler];
    updated[index] = { ...updated[index], [field]: value };
    updateSdsField(['b3_bilesim', 'karisim', 'bilesenler'], updated);
  };

  return (
    <div>
      {/* 3.1 XOR 3.2 Seçici */}
      <div className="section-group-title">
        <span>3. Bölüm Yapısı (Madde / Karışım Seçimi)</span>
      </div>

      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <div
          onClick={() => handleTypeChange('karisim')}
          style={{
            flex: 1,
            padding: '16px 20px',
            borderRadius: '12px',
            border: '2px solid',
            borderColor: tip === 'karisim' ? '#2563eb' : '#e2e8f0',
            background: tip === 'karisim' ? '#eff6ff' : '#ffffff',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            transition: 'all 0.15s ease',
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '8px',
              background: tip === 'karisim' ? '#2563eb' : '#f1f5f9',
              color: tip === 'karisim' ? 'white' : '#64748b',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Layers size={20} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: tip === 'karisim' ? '#1e40af' : '#1e293b' }}>
              3.2. Karışım
            </div>
            <div style={{ fontSize: '0.78rem', color: '#64748b' }}>
              Birden fazla kimyasal maddeden oluşan formülasyonlar (Önerilen)
            </div>
          </div>
        </div>

        <div
          onClick={() => handleTypeChange('madde')}
          style={{
            flex: 1,
            padding: '16px 20px',
            borderRadius: '12px',
            border: '2px solid',
            borderColor: tip === 'madde' ? '#2563eb' : '#e2e8f0',
            background: tip === 'madde' ? '#eff6ff' : '#ffffff',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            transition: 'all 0.15s ease',
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '8px',
              background: tip === 'madde' ? '#2563eb' : '#f1f5f9',
              color: tip === 'madde' ? 'white' : '#64748b',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Atom size={20} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: tip === 'madde' ? '#1e40af' : '#1e293b' }}>
              3.1. Madde
            </div>
            <div style={{ fontSize: '0.78rem', color: '#64748b' }}>
              Saf veya teknik saflıkta tek bir kimyasal bileşik
            </div>
          </div>
        </div>
      </div>

      <FieldHelper
        legalRef="KKDİK Ek-2 md. 0.3.1, 3. Bölüm"
        tooltip="Mevzuat gereği 3.1 veya 3.2'den yalnızca biri seçilebilir (XOR kuralı)."
      />

      {/* 3.1 Madde Formu */}
      {tip === 'madde' && (
        <div style={{ marginTop: '24px' }}>
          <div className="section-group-title">
            <span>3.1. Maddenin Kimyasal Tanımı</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">
                <span>Kimyasal Adı / IUPAC Adı <span className="req-star">*</span></span>
              </label>
              <input
                type="text"
                className="form-control"
                placeholder="ör. Toluen / Metilbenzen"
                value={madde.kimyasal_kimlik || ''}
                onChange={(e) => updateSdsField(['b3_bilesim', 'madde', 'kimyasal_kimlik'], e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <span>CAS Numarası</span>
              </label>
              <input
                type="text"
                className="form-control"
                placeholder="ör. 108-88-3"
                value={madde.cas_no || ''}
                onChange={(e) => updateSdsField(['b3_bilesim', 'madde', 'cas_no'], e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <span>EC / EINECS Numarası</span>
              </label>
              <input
                type="text"
                className="form-control"
                placeholder="ör. 203-625-9"
                value={madde.ec_no || ''}
                onChange={(e) => updateSdsField(['b3_bilesim', 'madde', 'ec_no'], e.target.value)}
              />
            </div>
          </div>

          <div className="form-group" style={{ marginTop: '16px' }}>
            <label className="form-label">
              <span>Safsızlıklar / Katkı Maddeleri (Her satıra bir tane)</span>
            </label>
            <textarea
              className="form-control"
              placeholder="ör. Sınıflandırmaya etki eden safsızlık bulunmamaktadır."
              value={(madde.safsizliklar || []).join('\n')}
              onChange={(e) =>
                updateSdsField(
                  ['b3_bilesim', 'madde', 'safsizliklar'],
                  e.target.value.split('\n').filter((x) => x.trim())
                )
              }
            />
            <FieldHelper
              legalRef="md. 3.1"
              onInsertText={(val) => updateSdsField(['b3_bilesim', 'madde', 'safsizliklar'], [val])}
              templates={['Sınıflandırmaya etki eden safsızlık veya katkı maddesi içermez.']}
            />
          </div>
        </div>
      )}

      {/* 3.2 Karışım Formu */}
      {tip === 'karisim' && (
        <div style={{ marginTop: '24px' }}>
          <div className="section-group-title" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>3.2. Karışımı Oluşturan Tehlikeli Bileşenler</span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={() => setIsHazardModalOpen(true)}
                style={{
                  background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
                title="Bu bileşen konsantrasyonlarıyla Bölüm 2 Zararlılıklarını SEA Ek-1 toplanabilirlik kurallarına göre hesapla"
              >
                <Calculator size={14} />
                ⚡ Bu Karışımla Bölüm 2'yi Hesapla
              </button>

              <button type="button" className="btn btn-outline btn-sm" onClick={addComponentRow}>
                <Plus size={14} />
                Bileşen Satırı Ekle
              </button>
            </div>
          </div>

          <div style={{ overflowX: 'auto', marginBottom: '16px' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th style={{ width: '22%' }}>Bileşen Adı</th>
                  <th style={{ width: '13%' }}>CAS No</th>
                  <th style={{ width: '13%' }}>EC No</th>
                  <th style={{ width: '16%' }}>Kayıt No</th>
                  <th style={{ width: '12%' }}>Konsantrasyon</th>
                  <th style={{ width: '20%' }}>SEA Sınıflandırması & H-İfadeleri</th>
                  <th style={{ width: '4%', textAlign: 'center' }}>Sil</th>
                </tr>
              </thead>
              <tbody>
                {bilesenler.map((row, idx) => (
                  <tr key={idx}>
                    <td>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="ör. Ksilen"
                        value={row.ad || ''}
                        onChange={(e) => updateComponentField(idx, 'ad', e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="1330-20-7"
                        value={row.cas_no || ''}
                        onChange={(e) => updateComponentField(idx, 'cas_no', e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="215-535-7"
                        value={row.ec_no || ''}
                        onChange={(e) => updateComponentField(idx, 'ec_no', e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="01-2119488216-32"
                        value={row.kayit_no || ''}
                        onChange={(e) => updateComponentField(idx, 'kayit_no', e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="ör. %10 - 25"
                        value={row.konsantrasyon || ''}
                        onChange={(e) => updateComponentField(idx, 'konsantrasyon', e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Flam. Liq. 3 H226, Skin Irrit. 2 H315"
                        value={row.siniflandirma || ''}
                        onChange={(e) => updateComponentField(idx, 'siniflandirma', e.target.value)}
                      />
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => removeComponentRow(idx)}
                      >
                        <Trash2 size={13} />
                      </button>
                    </td>
                  </tr>
                ))}
                {bilesenler.length === 0 && (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', color: '#94a3b8', padding: '24px' }}>
                      Henüz bileşen eklenmedi. Yukarıdaki "Bileşen Satırı Ekle" butonuna tıklayınız.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <FieldHelper
            legalRef="KKDİK Ek-2 md. 3.2"
            tooltip="Zararlılık eşiğini aşan veya mesleki maruziyet sınır değeri bulunan tüm bileşenler listelenmelidir."
          />

          {/* SEA Karışım Hesaplama Modalı */}
          <HazardCalculationModal
            isOpen={isHazardModalOpen}
            onClose={() => setIsHazardModalOpen(false)}
          />
        </div>
      )}
    </div>
  );
}
