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

    # Tek piktogram detayı
    res_pic = client.get("/api/references/pictograms/GHS02")
    assert res_pic.status_code == 200
    assert res_pic.json()["name"] == "Alevlenir"
