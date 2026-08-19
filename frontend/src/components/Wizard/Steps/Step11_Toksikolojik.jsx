import React from 'react';
import { useApp } from '../../../context/AppContext';
import FieldHelper from '../../Common/FieldHelper';

export default function Step11_Toksikolojik() {
  const { sdsData, updateSdsField } = useApp();

  const b11 = sdsData?.b11_toksikolojik || {};
  const b11_1 = b11.b11_1 || {};

  const toxFields = [
    {
      key: 'akut_toksisite',
      label: 'Akut Toksisite (Oral / Dermal / Soluma)',
      required: true,
      ph: 'ör. LD50 Oral (sıçan): > 2000 mg/kg; ATE Karışım: Hesaplanmış sınıflandırma eşiğinin üzerindedir.',
      tpl: 'Mevcut verilere göre sınıflandırma kriterlerini karşılamamaktadır.',
    },
    {
      key: 'cilt_asinmasi_tahrisi',
      label: 'Cilt Aşınması / Tahrişi',
      required: false,
      ph: 'ör. Ciltte tahrişe yol açar (Kategori 2).',
      tpl: 'Mevcut bilgilere göre sınıflandırma kriterlerini karşılamaz.',
    },
    {
      key: 'goz_hasari',
      label: 'Ciddi Göz Hasarları / Tahrişi',
      required: false,
      ph: 'ör. Ciddi göz tahrişine yol açar (Kategori 2).',
      tpl: 'Ciddi göz tahrişine yol açar.',
    },
    {
      key: 'solunum_cilt_hassasiyeti',
      label: 'Solunum Yolları veya Cilt Hassaslaşması',
      required: false,
      ph: 'ör. Alerjik cilt reaksiyonlarına yol açabilir veya Hassaslaştırıcı etki bildirilmemiştir.',
      tpl: 'Hassaslaştırıcı etkisi bilinmemektedir / Kriterleri karşılamaz.',
    },
    {
      key: 'mutajenite',
      label: 'Eşey Hücre Mutajenitesi',
      required: false,
      ph: 'ör. Genetik hasara yol açma şüphesi yoktur.',
      tpl: 'Mevcut verilere göre mutajenik olarak sınıflandırılmaz.',
    },
    {
      key: 'kanserojenite',
      label: 'Kanserojenite',
      required: false,
      ph: 'ör. Kanserojen olarak sınıflandırılmamıştır.',
      tpl: 'Kanserojenik madde içermez / Kriterleri karşılamamaktadır.',
    },
    {
      key: 'ureme_toksisitesi',
      label: 'Üreme Toksisitesi',
      required: false,
      ph: 'ör. Üreme yeteneğine veya doğmamış çocuğa zararlı etkisi bilinmemektedir.',
      tpl: 'Üreme için toksik olarak sınıflandırılmamıştır.',
    },
    {
      key: 'bhot_tek_maruz',
      label: 'Belirli Hedef Organ Toksisitesi (BHOT) - Tek Maruz Kalma',
      required: false,
      ph: 'ör. Solunum yolu tahrişine yol açabilir (Kategori 3) veya Rehavete neden olabilir.',
      tpl: 'Mevcut verilere göre sınıflandırma kriterlerini karşılamaz.',
    },
    {
      key: 'bhot_tekrarli',
      label: 'Belirli Hedef Organ Toksisitesi (BHOT) - Tekrarlı Maruz Kalma',
      required: false,
      ph: 'ör. Uzun süreli veya tekrarlı maruz kalmada organ hasarı riski yoktur.',
      tpl: 'Tekrarlanan maruz kalmalarda organ hasarı beklenmez.',
    },
    {
      key: 'aspirasyon_zarari',
      label: 'Aspirasyon Zararı',
      required: false,
      ph: 'ör. Aspirasyon tehlikesi oluşturmaz.',
      tpl: 'Aspirasyon zararı oluşturmaz.',
    },
    {
      key: 'maruz_kalma_yollari',
      label: 'Olası Maruz Kalma Yolları',
      required: false,
      ph: 'ör. Soluma, cilt teması, göz teması ve yutma.',
      tpl: 'Solunum, cilt ve göz teması, yutma.',
    },
    {
      key: 'belirtiler',
      label: 'Fiziksel, Kimyasal ve Toksikolojik Belirtiler',
      required: false,
      ph: 'ör. Gözde batma, kızarıklık, baş dönmesi, cilt kuruluğu.',
      tpl: 'Gözlerde sulanma ve kızarıklık, ciltte hafif tahriş.',
    },
    {
      key: 'kronik_etkiler',
      label: 'Kısa ve Uzun Süreli Maruz Kalmadan Doğan Kronik Etkiler',
      required: false,
      ph: 'ör. Tekrarlanan maruziyetlerde ciltte çatlak ve kuruluğa neden olabilir.',
      tpl: 'Sürekli veya tekrarlanan maruziyet ciltte kuruluk ve çatlaklara yol açabilir.',
    },
  ];

  return (
    <div>
      <div className="section-group-title">
        <span>11.1. Toksikolojik Etkiler Hakkında Bilgi</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
        {toxFields.map((f) => (
          <div key={f.key} className="form-group">
            <label className="form-label">
              <span>
                {f.label} {f.required && <span className="req-star">*</span>}
              </span>
            </label>
            <textarea
              className="form-control"
              placeholder={f.ph}
              value={b11_1[f.key] || ''}
              onChange={(e) => updateSdsField(['b11_toksikolojik', 'b11_1', f.key], e.target.value)}
              style={{ minHeight: '60px' }}
            />
            <FieldHelper
              legalRef="KKDİK Ek-2 md. 11.1"
              onInsertText={(val) => updateSdsField(['b11_toksikolojik', 'b11_1', f.key], val)}
              templates={[f.tpl, 'Veri bulunmamaktadır.']}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
