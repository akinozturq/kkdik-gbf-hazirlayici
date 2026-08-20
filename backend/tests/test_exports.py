import pytest
from fastapi.testclient import TestClient

def test_export_docx_endpoint(client: TestClient):
    # 1. Create a test product
    create_res = client.post("/api/products", json={
        "urun_adi": "Polyester Reçine PRS-100",
        "ticari_kod": "AYP-PRS-100",
        "kategori": "Reçineler",
        "sds_data": {
            "meta": {"hazirlama_tarihi": "18.08.2026", "revizyon_no": "01"},
            "b1_kimlik": {
                "b1_1": {"madde_karisim_adi": "Polyester Reçine PRS-100"},
                "b1_3": {"tedarikci_adi": "Aypol Kimya"},
                "b1_4": {"acil_telefon": "114"}
            },
            "b2_zarar_tanimi": {
                "b2_1": {"siniflandirmalar": [{"zararlilik_sinifi": "Alevlenir Sıvı", "h_kodu": "H226"}]},
                "b2_2": {"piktogramlar": ["GHS02"], "uyari_kelimesi": "Dikkat", "h_ifadeleri": ["H226"]}
            }
        }
    })
    assert create_res.status_code == 201
    prod_id = create_res.json()["id"]

    # 2. Test DOCX export
    docx_res = client.get(f"/api/products/{prod_id}/export/docx")
    assert docx_res.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in docx_res.headers["content-type"]
    assert len(docx_res.content) > 1000

def test_export_pdf_endpoint(client: TestClient):
    # 1. Create a test product
    create_res = client.post("/api/products", json={
        "urun_adi": "Selülozik Tiner Extra",
        "ticari_kod": "G.TN.20.00",
        "kategori": "Solventler & Tinerler",
        "sds_data": {
            "meta": {"hazirlama_tarihi": "18.08.2026"},
            "b1_kimlik": {
                "b1_1": {"madde_karisim_adi": "Selülozik Tiner Extra"},
                "b1_3": {"tedarikci_adi": "Aypol Kimya"},
                "b1_4": {"acil_telefon": "114"}
            }
        }
    })
    assert create_res.status_code == 201
    prod_id = create_res.json()["id"]

    # 2. Test PDF export
    pdf_res = client.get(f"/api/products/{prod_id}/export/pdf")
    assert pdf_res.status_code == 200
    assert "application/pdf" in pdf_res.headers["content-type"]
    assert pdf_res.content.startswith(b"%PDF")
    assert len(pdf_res.content) > 1000

def test_preview_html_endpoint(client: TestClient):
    create_res = client.post("/api/products", json={
        "urun_adi": "Epoksi Astar",
        "ticari_kod": "AYP-EPX-01",
        "kategori": "Epoksi Sistemler",
        "sds_data": {}
    })
    prod_id = create_res.json()["id"]

    html_res = client.get(f"/api/products/{prod_id}/export/preview-html")
    assert html_res.status_code == 200
    assert "text/html" in html_res.headers["content-type"]
    assert "GÜVENLİK BİLGİ FORMU" in html_res.text
    assert "Epoksi Astar" in html_res.text

    # Test English HTML Preview (REACH Annex II)
    html_en_res = client.get(f"/api/products/{prod_id}/export/preview-html?lang=en")
    assert html_en_res.status_code == 200
    assert "SAFETY DATA SHEET" in html_en_res.text
    assert "Identification of the substance/mixture" in html_en_res.text
    assert "Hazards identification" in html_en_res.text


def test_export_english_docx_and_pdf(client: TestClient):
    create_res = client.post("/api/products", json={
        "urun_adi": "Industrial Solvent Blend",
        "ticari_kod": "SOL-200",
        "kategori": "Solvents",
        "sds_data": {
            "meta": {"hazirlama_tarihi": "20.08.2026", "revizyon_no": "02"},
            "b1_kimlik": {
                "b1_1": {"madde_karisim_adi": "Industrial Solvent Blend"},
                "b1_3": {"tedarikci_adi": "Aypol Chemicals"},
                "b1_4": {"acil_telefon": "112"}
            }
        }
    })
    prod_id = create_res.json()["id"]

    # English DOCX
    docx_en_res = client.get(f"/api/products/{prod_id}/export/docx?lang=en")
    assert docx_en_res.status_code == 200
    assert len(docx_en_res.content) > 1000

    # English PDF
    pdf_en_res = client.get(f"/api/products/{prod_id}/export/pdf?lang=en")
    assert pdf_en_res.status_code == 200
    assert pdf_en_res.content.startswith(b"%PDF")
    assert len(pdf_en_res.content) > 1000


def test_export_404_for_missing_product(client: TestClient):
    res = client.get("/api/products/99999/export/docx")
    assert res.status_code == 404
