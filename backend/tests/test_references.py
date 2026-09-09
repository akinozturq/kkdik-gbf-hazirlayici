"""
Mevzuat Referans Kütüphanesi Birim ve API Testleri
"""

import pytest


def test_get_h_statements_api(client):
    """H-kodları listeleme ve filtreleme testi"""
    # Tüm H-kodları
    res = client.get("/api/references/h-statements")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 30

    # Kategori filtresi (Fiziksel)
    res_fiz = client.get("/api/references/h-statements?category=Fiziksel")
    assert res_fiz.status_code == 200
    for item in res_fiz.json():
        assert item["category"] == "Fiziksel"

    # Kod detayı
    res_code = client.get("/api/references/h-statements/H225")
    assert res_code.status_code == 200
    data = res_code.json()
    assert data["code"] == "H225"
    assert "Kolay alevlenir" in data["text"]


def test_get_p_statements_api(client):
    """P-kodları listeleme ve arama testi"""
    res = client.get("/api/references/p-statements")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 20

    # Tip filtresi (Önlem)
    res_onlem = client.get("/api/references/p-statements?type=Önlem")
    assert res_onlem.status_code == 200
    for item in res_onlem.json():
        assert item["type"] == "Önlem"

    # Kod detayı
    res_code = client.get("/api/references/p-statements/P210")
    assert res_code.status_code == 200
    assert "Isıdan" in res_code.json()["text"]


def test_get_pictograms_api(client):
    """GHS piktogram listesi ve detay testi"""
    res = client.get("/api/references/pictograms")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 9  # GHS01 - GHS09

    codes = [p["code"] for p in items]
    assert "GHS01" in codes
    assert "GHS02" in codes
    assert "GHS07" in codes
    assert "GHS09" in codes


def test_get_raw_materials_api(client):
    """Hammadde Kütüphanesi listeleme, arama ve detay testi"""
    res = client.get("/api/references/raw-materials")
    assert res.status_code == 200
    materials = res.json()
    assert len(materials) >= 12  # Aseton, Toluen, Ksilen, Butil Asetat vb.

    # Arama testi
    res_search = client.get("/api/references/raw-materials?search=Ksilen")
    assert res_search.status_code == 200
    assert len(res_search.json()) >= 1
    assert res_search.json()[0]["cas_no"] == "1330-20-7"

    # Detay testi
    res_detail = client.get("/api/references/raw-materials/raw-aseton")
    assert res_detail.status_code == 200
    assert res_detail.json()["ad"] == "Aseton"
    assert "H225" in res_detail.json()["h_kodlari"]


    # Tek piktogram detayı
    res_pic = client.get("/api/references/pictograms/GHS02")
    assert res_pic.status_code == 200
    assert res_pic.json()["name"] == "Alevlenir"


def test_raw_material_crud_api(client):
    """Hammadde Kütüphanesi Ekleme, Güncelleme ve Silme (CRUD) API testi"""
    test_payload = {
        "ad": "Test Reaktif Maddesi",
        "ticari_ad": "TRM-100",
        "cas_no": "99999-99-9",
        "ec_no": "999-999-9",
        "kategori": "Katkılar",
        "siniflandirma_str": "Flam. Liq. 2 H225, Eye Irrit. 2 H319, STOT SE 3 H336",
        "uyari_kelimesi": "Tehlike"
    }

    # 1. CREATE (POST)
    res_create = client.post("/api/references/raw-materials", json=test_payload)
    assert res_create.status_code == 201
    created_data = res_create.json()
    assert created_data["ad"] == "Test Reaktif Maddesi"
    assert "raw-test-reaktif-maddesi" in created_data["id"]
    assert "H225" in created_data["h_kodlari"]
    assert "H319" in created_data["h_kodlari"]
    assert "H336" in created_data["h_kodlari"]
    assert "GHS02" in created_data["piktogramlar"]
    assert "GHS07" in created_data["piktogramlar"]
    mat_id = created_data["id"]

    # 2. UPDATE (PUT)
    update_payload = dict(test_payload)
    update_payload["ticari_ad"] = "TRM-100 Guncel"
    update_payload["akut_toksisite_oral"] = 2500
    res_update = client.put(f"/api/references/raw-materials/{mat_id}", json=update_payload)
    assert res_update.status_code == 200
    updated_data = res_update.json()
    assert updated_data["ticari_ad"] == "TRM-100 Guncel"
    assert updated_data["akut_toksisite_oral"] == 2500

    # 3. GET by ID to confirm
    res_get = client.get(f"/api/references/raw-materials/{mat_id}")
    assert res_get.status_code == 200
    assert res_get.json()["ticari_ad"] == "TRM-100 Guncel"

    # 4. DELETE (DELETE)
    res_del = client.delete(f"/api/references/raw-materials/{mat_id}")
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True

    # 5. Confirm DELETED
    res_after_del = client.get(f"/api/references/raw-materials/{mat_id}")
    assert res_after_del.status_code == 404

