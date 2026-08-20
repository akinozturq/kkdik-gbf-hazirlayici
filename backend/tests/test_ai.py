"""
Gemini AI Router & Service Testleri
"""

from starlette.testclient import TestClient
from app.services.gemini_service import gemini_service


def test_ai_config_endpoints(client: TestClient):
    # 1. Get initial config
    res = client.get("/api/ai/config")
    assert res.status_code == 200
    data = res.json()
    assert "is_configured" in data
    assert "active_model" in data
    assert "supported_models" in data

    # 2. Save config with Gemini 3.5 Flash Lite
    save_res = client.post("/api/ai/config", json={
        "api_key": "AIzaSyDummyKeyForTesting12345678",
        "model": "gemini-3.5-flash-lite"
    })
    assert save_res.status_code == 200
    save_data = save_res.json()
    assert save_data["success"] is True
    assert save_data["active_model"] == "gemini-3.5-flash-lite"
    assert gemini_service.is_configured() is True

    # 3. Check masked key in GET
    res2 = client.get("/api/ai/config")
    data2 = res2.json()
    assert data2["is_configured"] is True
    assert "AIzaSy" in data2["api_key_masked"]

    # 4. Clean up test credentials
    client.post("/api/ai/config", json={"api_key": "", "model": "gemini-1.5-flash"})


def test_ai_test_endpoint_without_valid_key(client: TestClient):
    # Test connection with empty key
    res = client.post("/api/ai/test", json={"api_key": ""})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
