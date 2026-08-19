"""
Ürün CRUD ve API Uç Noktaları Entegrasyon Testleri
"""

import pytest


def test_create_product(client, sample_valid_sds_dict):
    """Yeni ürün ve SDS oluşturma uç noktası testi (POST /api/products)"""
    payload = {
        "urun_adi": "Aypol Akrilik Binder 50",
        "ticari_kod": "AYP-AB-50",
        "kategori": "Akrilik Reçineler",
        "sds_data": sample_valid_sds_dict
    }

    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["urun_adi"] == "Aypol Akrilik Binder 50"
    assert data["ticari_kod"] == "AYP-AB-50"
    assert data["kategori"] == "Akrilik Reçineler"
    assert data["sds_data"]["b1_kimlik"]["b1_1"]["madde_karisim_adi"] == "Polyester Reçine Solüsyonu"


def test_create_product_missing_kategori_fails(client, sample_valid_sds_dict):
    """Kategori/Ürün ailesi olmadan ürün oluşturulamamalıdır (422 Unprocessable Entity)"""
    payload = {
        "urun_adi": "Kategorisiz Ürün",
        "ticari_kod": "KAT-001",
        "sds_data": sample_valid_sds_dict
    }
    response = client.post("/api/products", json=payload)
    assert response.status_code == 422


def test_get_product_categories(client, sample_valid_sds_dict):
    """Ürün aileleri ve kategorileri listesi testi (GET /api/products/categories)"""
    client.post("/api/products", json={
        "urun_adi": "Epoksi Astar Gri",
        "ticari_kod": "EP-GR-01",
        "kategori": "Özel Epoksiler",
        "sds_data": sample_valid_sds_dict
    })
    res = client.get("/api/products/categories")
    assert res.status_code == 200
    cats = res.json()
    assert "Özel Epoksiler" in cats
    assert "Solventler & Tinerler" in cats


def test_list_products_and_search(client, sample_valid_sds_dict):
    """Ürün listeleme, arama ve filtreleme testi (GET /api/products)"""
    # 2 ürün oluşturalım
    client.post("/api/products", json={
        "urun_adi": "Epoksi Astar",
        "ticari_kod": "EP-101",
        "kategori": "Epoksi",
        "sds_data": sample_valid_sds_dict
    })
    client.post("/api/products", json={
        "urun_adi": "Poliüretan Vernik",
        "ticari_kod": "PU-202",
        "kategori": "Poliüretan",
        "sds_data": sample_valid_sds_dict
    })

    # Genel listeleme
    res1 = client.get("/api/products")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["total"] == 2
    assert len(data1["items"]) == 2

    # Arama (query=Epoksi)
    res2 = client.get("/api/products?query=Epoksi")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["total"] == 1
    assert data2["items"][0]["urun_adi"] == "Epoksi Astar"

    # Kategori filtreleme
    res3 = client.get("/api/products?kategori=Poliüretan")
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["total"] == 1
    assert data3["items"][0]["ticari_kod"] == "PU-202"


def test_get_product_detail(client, sample_valid_sds_dict):
    """Ürün detayı getirme testi (GET /api/products/{id})"""
    create_res = client.post("/api/products", json={
        "urun_adi": "İzotopik Çözücü",
        "ticari_kod": "SLV-001",
        "kategori": "Solventler",
        "sds_data": sample_valid_sds_dict
    })
    product_id = create_res.json()["id"]

    get_res = client.get(f"/api/products/{product_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == product_id
    assert data["urun_adi"] == "İzotopik Çözücü"
    assert data["sds_data"]["b14_tasimacilik"]["b14_1_un_numarasi"] == "UN 1866"


def test_update_product(client, sample_valid_sds_dict):
    """Ürün ve SDS form güncelleme testi (PUT /api/products/{id})"""
    create_res = client.post("/api/products", json={
        "urun_adi": "Eski Ürün Adı",
        "ticari_kod": "OLD-001",
        "kategori": "Genel Reçineler",
        "sds_data": sample_valid_sds_dict
    })
    product_id = create_res.json()["id"]

    # Kısmi güncelleme
    update_payload = {
        "urun_adi": "Yeni Güncellenmiş Ürün Adı",
        "sds_data": {
            "b1_kimlik": {
                "b1_1": {
                    "madde_karisim_adi": "Yeni Güncellenmiş Ürün Adı"
                }
            }
        }
    }
    update_res = client.put(f"/api/products/{product_id}", json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["urun_adi"] == "Yeni Güncellenmiş Ürün Adı"
    assert updated_data["sds_data"]["b1_kimlik"]["b1_1"]["madde_karisim_adi"] == "Yeni Güncellenmiş Ürün Adı"
    # Diğer bölümler korunmalı
    assert updated_data["sds_data"]["b14_tasimacilik"]["b14_1_un_numarasi"] == "UN 1866"


def test_delete_product(client):
    """Ürün silme testi (DELETE /api/products/{id})"""
    create_res = client.post("/api/products", json={
        "urun_adi": "Silinecek Ürün",
        "ticari_kod": "DEL-001",
        "kategori": "Silinecekler"
    })
    product_id = create_res.json()["id"]

    del_res = client.delete(f"/api/products/{product_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/products/{product_id}")
    assert get_res.status_code == 404


def test_duplicate_product(client, sample_valid_sds_dict):
    """Var olan bir üründen kopyalama testi (POST /api/products/{id}/duplicate)"""
    create_res = client.post("/api/products", json={
        "urun_adi": "Aypol Orijinal Formülasyon",
        "ticari_kod": "AYP-ORIG-01",
        "kategori": "Reçineler",
        "sds_data": sample_valid_sds_dict
    })
    original_id = create_res.json()["id"]

    dup_res = client.post(f"/api/products/{original_id}/duplicate", json={
        "yeni_urun_adi": "Aypol Yeni Formülasyon v2",
        "yeni_ticari_kod": "AYP-V2-01"
    })
    assert dup_res.status_code == 201
    dup_data = dup_res.json()
    assert dup_data["id"] != original_id
    assert dup_data["urun_adi"] == "Aypol Yeni Formülasyon v2"
    assert dup_data["ticari_kod"] == "AYP-V2-01"
    assert dup_data["sds_data"]["b1_kimlik"]["b1_1"]["madde_karisim_adi"] == "Aypol Yeni Formülasyon v2"
    assert dup_data["sds_data"]["b14_tasimacilik"]["b14_1_un_numarasi"] == "UN 1866"


def test_validate_product_api(client, sample_valid_sds_dict):
    """Ürün SDS doğrulama uç noktası testi (GET /api/products/{id}/validate)"""
    create_res = client.post("/api/products", json={
        "urun_adi": "Test Ürünü",
        "ticari_kod": "TST-01",
        "kategori": "Test Ailesi",
        "sds_data": sample_valid_sds_dict
    })
    product_id = create_res.json()["id"]

    val_res = client.get(f"/api/products/{product_id}/validate")
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["is_valid_for_export"] is True
    assert val_data["total_errors"] == 0
    assert len(val_data["section_progress"]) == 16


def test_auto_fill_h_codes_api(client, sample_valid_sds_dict):
    """H-kodlarını otomatik toplama ve Bölüm 16'ya yazma testi (POST /api/products/{id}/auto-fill-h-codes)"""
    create_res = client.post("/api/products", json={
        "urun_adi": "H-Kod Test Ürünü",
        "ticari_kod": "HK-01",
        "kategori": "Solventler",
        "sds_data": sample_valid_sds_dict
    })
    product_id = create_res.json()["id"]

    fill_res = client.post(f"/api/products/{product_id}/auto-fill-h-codes?save_to_sds=true")
    assert fill_res.status_code == 200
    fill_data = fill_res.json()
    assert fill_data["product_id"] == product_id
    assert "H226" in fill_data["found_h_codes"]
    assert "H315" in fill_data["found_h_codes"]
    assert "H319" in fill_data["found_h_codes"]
    assert fill_data["updated_section16"] is True

    # Ürünü tekrar getirip Bölüm 16'yı kontrol edelim
    product_res = client.get(f"/api/products/{product_id}")
    b16 = product_res.json()["sds_data"]["b16_diger_bilgiler"]
    assert any("H226" in txt for txt in b16["tam_h_ifadeleri"])


def test_validate_raw_sds_endpoint(client, sample_valid_sds_dict):
    """Kaydetmeden doğrudan ham SDS JSON doğrulama testi (POST /api/products/validate-raw)"""
    res = client.post("/api/products/validate-raw", json=sample_valid_sds_dict)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid_for_export"] is True
    assert data["total_errors"] == 0


def test_calculate_and_apply_hazards_api(client, sample_valid_sds_dict):
    """Zararlılık hesaplama ve Bölüm 2'ye aktarma API testi"""
    create_res = client.post("/api/products", json={
        "urun_adi": "Karışım Hesaplama Test Ürünü",
        "ticari_kod": "CALC-01",
        "kategori": "Test Karışımlar",
        "sds_data": sample_valid_sds_dict
    })
    product_id = create_res.json()["id"]

    # 1. Calculate endpoint
    calc_res = client.post(f"/api/products/{product_id}/calculate-hazards")
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert "h_ifadeleri" in calc_data
    assert "p_ifadeleri" in calc_data
    assert "uyari_kelimesi" in calc_data

    # 2. Apply endpoint
    apply_res = client.post(f"/api/products/{product_id}/apply-calculated-hazards")
    assert apply_res.status_code == 200
    apply_data = apply_res.json()
    assert apply_data["status"] == "success"
    assert "product" in apply_data
    assert apply_data["product"]["id"] == product_id

    # Verify SDS was updated in database
    product_res = client.get(f"/api/products/{product_id}")
    b2 = product_res.json()["sds_data"]["b2_zarar_tanimi"]
    assert b2["b2_2"]["uyari_kelimesi"] == calc_data["uyari_kelimesi"]
    assert len(b2["b2_2"]["h_ifadeleri"]) > 0

