/**
 * KKDİK SDS Hazırlayıcı Backend API İstemcisi
 */

const API_BASE = '/api';

export async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  let response;
  try {
    response = await fetch(url, config);
  } catch (netErr) {
    throw new Error('Sunucuya bağlanılamadı. Backend API çalışıyor mu? (' + netErr.message + ')');
  }

  if (response.status === 204) {
    return null;
  }

  if (!response.ok) {
    let errorDetail = 'Bir hata oluştu.';
    const text = await response.text();
    try {
      const errJson = JSON.parse(text);
      if (typeof errJson.detail === 'string') {
        errorDetail = errJson.detail;
      } else if (Array.isArray(errJson.detail)) {
        errorDetail = errJson.detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
      } else {
        errorDetail = JSON.stringify(errJson);
      }
    } catch {
      errorDetail = text || `HTTP ${response.status} Hatası`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

// ==========================================
// ÜRÜN & SDS İŞLEMLERİ
// ==========================================
export const api = {
  // Ürünleri Listele
  getProducts: (params = {}) => {
    const query = new URLSearchParams();
    if (params.query) query.set('query', params.query);
    if (params.kategori) query.set('kategori', params.kategori);
    if (params.page) query.set('page', params.page);
    if (params.page_size) query.set('page_size', params.page_size);
    if (params.sort_by) query.set('sort_by', params.sort_by);
    if (params.sort_order) query.set('sort_order', params.sort_order);
    return request(`/products?${query.toString()}`);
  },

  // Ürün Detayı & 16 Bölüm SDS
  getProduct: (id) => request(`/products/${id}`),

  // Yeni Ürün Oluştur
  createProduct: (data) =>
    request('/products', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Ürün & SDS Güncelle (Autosave Uyumlu)
  updateProduct: (id, data) =>
    request(`/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Ürün Sil
  deleteProduct: (id) =>
    request(`/products/${id}`, {
      method: 'DELETE',
    }),

  // Ürün Kopyala -> Yeni Ürün
  duplicateProduct: (id, data = {}) =>
    request(`/products/${id}/duplicate`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Ürünün SDS'ini KKDİK Ek-2 Kurallarına Göre Doğrula
  validateProduct: (id) => request(`/products/${id}/validate`),

  // H-Kodlarını Otomatik Topla ve Bölüm 16'ya Yaz
  autoFillHCodes: (id, saveToSds = false) =>
    request(`/products/${id}/auto-fill-h-codes?save_to_sds=${saveToSds}`, {
      method: 'POST',
    }),

  // Ham SDS JSON Doğrula
  validateRawSds: (sdsData) =>
    request('/products/validate-raw', {
      method: 'POST',
      body: JSON.stringify(sdsData),
    }),

  // ==========================================
  // FAZ 3: DIŞA AKTARMA (EXPORT) BAĞLANTILARI
  // ==========================================
  getDocxExportUrl: (id) => `${API_BASE}/products/${id}/export/docx`,
  getPdfExportUrl: (id) => `${API_BASE}/products/${id}/export/pdf`,
  getPreviewHtmlUrl: (id) => `${API_BASE}/products/${id}/export/preview-html`,

  downloadDocx: async (id, filename) => {
    const res = await fetch(`${API_BASE}/products/${id}/export/docx`);
    if (!res.ok) {
      const text = await res.text();
      let errText = text;
      try {
        const errJson = JSON.parse(text);
        errText = errJson.detail || JSON.stringify(errJson);
      } catch {}
      throw new Error(errText || 'Word dosyası indirilemedi.');
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || `GBF_${id}.docx`;
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    }, 200);
  },

  downloadPdf: async (id, filename) => {
    const res = await fetch(`${API_BASE}/products/${id}/export/pdf`);
    if (!res.ok) {
      const text = await res.text();
      let errText = text;
      try {
        const errJson = JSON.parse(text);
        errText = errJson.detail || JSON.stringify(errJson);
      } catch {}
      throw new Error(errText || 'PDF dosyası indirilemedi.');
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || `GBF_${id}.pdf`;
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    }, 200);
  },

  // ==========================================
  // MEVZUAT REFERANS KÜTÜPHANESİ
  // ==========================================
  getHStatements: (category = null, search = null) => {
    const query = new URLSearchParams();
    if (category) query.set('category', category);
    if (search) query.set('search', search);
    return request(`/references/h-statements?${query.toString()}`);
  },

  getPStatements: (type = null, search = null) => {
    const query = new URLSearchParams();
    if (type) query.set('type', type);
    if (search) query.set('search', search);
    return request(`/references/p-statements?${query.toString()}`);
  },

  getPictograms: () => request('/references/pictograms'),

  getExposureLimits: (search = null) => {
    const query = new URLSearchParams();
    if (search) query.set('search', search);
    return request(`/references/exposure-limits?${query.toString()}`);
  },

  // ==========================================
  // SEA KARIŞIM HESAPLAMA & H -> P HARİTALAMA
  // ==========================================
  calculateProductHazards: (id) =>
    request(`/products/${id}/calculate-hazards`, {
      method: 'POST',
    }),

  applyCalculatedHazards: (id) =>
    request(`/products/${id}/apply-calculated-hazards`, {
      method: 'POST',
    }),

  derivePFromH: (hCodes) =>
    request('/products/hazards/h-to-p', {
      method: 'POST',
      body: JSON.stringify({ h_codes: hCodes }),
    }),

  calculatePreview: (data) =>
    request('/products/hazards/calculate-preview', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // ==========================================
  // BÖLÜM 8.1 MARUZİYET SINIR DEĞERLERİ OTOMASYONU
  // ==========================================
  autoFillExposureLimits: (id, saveToSds = false) =>
    request(`/products/${id}/auto-fill-exposure-limits?save_to_sds=${saveToSds}`, {
      method: 'POST',
    }),
};


