import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';
import { Plus, Trash2 } from 'lucide-react';

export default function Step8_MaruzKalma() {
  const { sdsData, updateSdsField } = useApp();

  const b8 = sdsData?.b8_maruz_kalma_kontrolu || {};
  const b8_1 = b8.b8_1_kontrol_parametreleri || [];
  const b8_2 = b8.b8_2 || {};
  const kkd = b8_2.kkd || {};

  // Add Exposure Param Row
  const addExposureRow = () => {
    const updated = [
      ...b8_1,
      { madde: '', sinir_degeri: '', birim: 'mg/m³', yasal_dayanak: '' },
    ];
    updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_1_kontrol_parametreleri'], updated);
  };

  const removeExposureRow = (index) => {
    const updated = b8_1.filter((_, i) => i !== index);
    updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_1_kontrol_parametreleri'], updated);
  };

  const updateExposureRow = (index, field, value) => {
    const updated = [...b8_1];
    updated[index] = { ...updated[index], [field]: value };
    updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_1_kontrol_parametreleri'], updated);
  };

  return (
    <div>
      {/* 8.1 Kontrol Parametreleri */}
      <div className="section-group-title">
        <span>8.1. Kontrol Parametreleri (Mesleki Maruziyet Sınır Değerleri)</span>
        <button type="button" className="btn btn-outline btn-sm" onClick={addExposureRow}>
          <Plus size={14} />
          Sınır Değer Satırı Ekle
        </button>
      </div>

      <div style={{ overflowX: 'auto', marginBottom: '16px' }}>
        <table className="custom-table">
          <thead>
            <tr>
              <th style={{ width: '30%' }}>Madde / Bileşen</th>
              <th style={{ width: '30%' }}>Sınır Değeri (TWA / STEL)</th>
              <th style={{ width: '15%' }}>Birim</th>
              <th style={{ width: '20%' }}>Yasal Dayanak / Standart</th>
              <th style={{ width: '5%', textAlign: 'center' }}>Sil</th>
            </tr>
          </thead>
          <tbody>
            {b8_1.map((row, idx) => (
              <tr key={idx}>
                <td>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="ör. Ksilen (CAS: 1330-20-7)"
                    value={row.madde || ''}
                    onChange={(e) => updateExposureRow(idx, 'madde', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="ör. TWA: 50 ppm, STEL: 100 ppm"
                    value={row.sinir_degeri || ''}
                    onChange={(e) => updateExposureRow(idx, 'sinir_degeri', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="mg/m³ veya ppm"
                    value={row.birim || ''}
                    onChange={(e) => updateExposureRow(idx, 'birim', e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Kimyasal Maddelerle Çalışmalarda İSG Yönetmeliği"
                    value={row.yasal_dayanak || ''}
                    onChange={(e) => updateExposureRow(idx, 'yasal_dayanak', e.target.value)}
                  />
                </td>
                <td style={{ textAlign: 'center' }}>
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    onClick={() => removeExposureRow(idx)}
                  >
                    <Trash2 size={13} />
                  </button>
                </td>
              </tr>
            ))}
            {b8_1.length === 0 && (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', color: '#94a3b8', padding: '20px' }}>
                  Tanımlı mesleki maruziyet sınır değeri girilmedi.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <FieldHelper
        legalRef="KKDİK Ek-2 md. 8.1"
        tooltip="Ulusal veya uluslararası OEL / TWA / STEL değerleri bulunuyorsa listelenmelidir."
      />

      {/* 8.2 Maruz Kalma Kontrolleri */}
      <div className="section-group-title">
        <span>8.2. Maruz Kalma Kontrolleri</span>
      </div>

      <div className="form-group">
        <label className="form-label">
          <span>Uygun Mühendislik Kontrolleri <span className="req-star">*</span></span>
        </label>
        <textarea
          className="form-control"
          placeholder="ör. Yeterli genel ve lokal egzoz havalandırması sağlayınız. Göz yıkama çeşmeleri ve acil duş üniteleri bulundurunuz."
          value={b8_2.muhendislik_kontrolleri || ''}
          onChange={(e) => updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'muhendislik_kontrolleri'], e.target.value)}
        />
        <FieldHelper
          legalRef="KKDİK Ek-2 md. 8.2"
          onInsertText={(val) =>
            updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'muhendislik_kontrolleri'], val)
          }
          templates={['Lokal egzoz havalandırması ve çalışma alanında yeterli hava sirkülasyonu sağlayınız.']}
        />
      </div>

      {/* Kişisel Koruyucu Donanım */}
      <div style={{ marginTop: '16px' }}>
        <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#334155', marginBottom: '10px' }}>
          Kişisel Koruyucu Donanım (KKD)
        </h4>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div className="form-group">
            <label className="form-label">
              <span>Göz / Yüz Koruması</span>
            </label>
            <input
              type="text"
              className="form-control"
              placeholder="ör. EN 166 standardına uygun koruyucu gözlük veya yüz siperi."
              value={kkd.goz_yuz || ''}
              onChange={(e) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'goz_yuz'], e.target.value)
              }
            />
            <FieldHelper
              onInsertText={(val) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'goz_yuz'], val)
              }
              templates={['EN 166 uyumlu yan siperlikli koruyucu gözlük.']}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span>Ellerin Korunması (Eldiven)</span>
            </label>
            <input
              type="text"
              className="form-control"
              placeholder="ör. EN 374 standardına uygun nitril veya bütil kauçuk eldiven."
              value={kkd.cilt_el || ''}
              onChange={(e) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'cilt_el'], e.target.value)
              }
            />
            <FieldHelper
              onInsertText={(val) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'cilt_el'], val)
              }
              templates={['EN 374 uyumlu nitril/bütil kimyasala dayanıklı eldiven.']}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span>Cildin Diğer Kısımlarının Korunması</span>
            </label>
            <input
              type="text"
              className="form-control"
              placeholder="ör. Antistatik kimyasala dayanıklı koruyucu iş önlüğü/tulum ve güvenlik ayakkabısı."
              value={kkd.cilt_diger || ''}
              onChange={(e) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'cilt_diger'], e.target.value)
              }
            />
            <FieldHelper
              onInsertText={(val) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'cilt_diger'], val)
              }
              templates={['Antistatik koruyucu iş kıyafeti ve iş ayakkabısı.']}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span>Solunum Sisteminin Korunması</span>
            </label>
            <input
              type="text"
              className="form-control"
              placeholder="ör. Yetersiz havalandırmada EN 14387 uyumlu A tipi organik buhar filtreli yarım yüz maskesi."
              value={kkd.solunum || ''}
              onChange={(e) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'solunum'], e.target.value)
              }
            />
            <FieldHelper
              onInsertText={(val) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'solunum'], val)
              }
              templates={['EN 14387 standardına uygun A tipi filtreli solunum maskesi.', 'Normal havalandırma koşullarında gerekli değildir.']}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span>Isıl Zararlara Karşı Koruma</span>
            </label>
            <input
              type="text"
              className="form-control"
              placeholder="ör. Gerekli değildir."
              value={kkd.isil || ''}
              onChange={(e) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'isil'], e.target.value)
              }
            />
            <FieldHelper
              onInsertText={(val) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'kkd', 'isil'], val)
              }
              templates={['Gerekli değildir.']}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <span>Çevresel Maruziyet Kontrolleri</span>
            </label>
            <input
              type="text"
              className="form-control"
              placeholder="ör. Havalandırma bacalarından emisyon mevzuat sınırlarına uyulmalıdır."
              value={b8_2.cevresel_kontroller || ''}
              onChange={(e) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'cevresel_kontroller'], e.target.value)
              }
            />
            <FieldHelper
              onInsertText={(val) =>
                updateSdsField(['b8_maruz_kalma_kontrolu', 'b8_2', 'cevresel_kontroller'], val)
              }
              templates={['Çevre koruma mevzuatına ve emisyon limitlerine uyulmalıdır.']}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
