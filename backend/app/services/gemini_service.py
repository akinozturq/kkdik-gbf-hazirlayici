"""
Google Gemini AI Hibrit Çeviri Servisi
REACH Annex II ve CLP uyumlu kimyasal güvenlik bilgi formu serbest metin çevirisi
"""

import json
import logging
import re
from typing import Dict, Any, Optional, List
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Desteklenen ve bilinen kararlı modeller
SUPPORTED_MODELS = [
    {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash (En Kararlı & Ücretsiz Kotaya Uygun)", "recommended": True},
    {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash (Yeni Nesil Hızlı)", "recommended": False},
    {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "recommended": False},
    {"id": "gemini-3.5-flash-lite", "name": "Gemini 3.5 Flash Lite", "recommended": False},
    {"id": "gemini-1.5-flash-8b", "name": "Gemini 1.5 Flash 8B (Ultra Hafif)", "recommended": False},
    {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro (Gelişmiş Zekâ)", "recommended": False},
]


class GeminiService:
    def __init__(self):
        self._api_key: Optional[str] = None
        self._model: Optional[str] = None

    @property
    def api_key(self) -> str:
        return self._api_key or settings.GEMINI_API_KEY or ""

    @property
    def model(self) -> str:
        return self._model or settings.GEMINI_MODEL or "gemini-1.5-flash"

    def set_credentials(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if api_key is not None:
            self._api_key = api_key.strip()
            settings.GEMINI_API_KEY = self._api_key
        if model is not None:
            self._model = model.strip()
            settings.GEMINI_MODEL = self._model

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def get_available_models(self, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """API anahtarı için Google'da tanımlı güncel model listesini çeker."""
        key_to_use = (api_key or self.api_key).strip()
        if not key_to_use:
            return SUPPORTED_MODELS

        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.get(f"{GEMINI_API_URL}?key={key_to_use}")
                if res.status_code == 200:
                    data = res.json()
                    models = []
                    for m in data.get("models", []):
                        m_name = m.get("name", "").replace("models/", "")
                        methods = m.get("supportedGenerationMethods", [])
                        if "generateContent" in methods and "gemini" in m_name:
                            disp = m.get("displayName", m_name)
                            models.append({
                                "id": m_name,
                                "name": f"{disp} ({m_name})",
                                "recommended": "1.5-flash" in m_name or "flash" in m_name
                            })
                    if models:
                        return models
        except Exception as e:
            logger.warning(f"Google modelleri listelenemedi: {e}")

        return SUPPORTED_MODELS

    def test_connection(self, api_key: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """Gemini API bağlantısını test eder ve yanıt süresini döner."""
        key_to_use = (api_key or self.api_key).strip()
        model_to_use = (model or self.model).strip()

        if not key_to_use:
            return {
                "success": False,
                "message": "Gemini API Anahtarı girilmedi.",
                "model": model_to_use
            }

        url = f"{GEMINI_API_URL}/{model_to_use}:generateContent?key={key_to_use}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Translate into English in 5 words or fewer: 'Kolay alevlenir sıvı ve buhar.'"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 60
            }
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload, headers={"Content-Type": "application/json"})
                
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_part = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        return {
                            "success": True,
                            "message": f"Bağlantı başarılı! Model: {model_to_use}",
                            "model": model_to_use,
                            "response_sample": text_part
                        }
                    return {
                        "success": True,
                        "message": "Bağlantı başarılı.",
                        "model": model_to_use
                    }
                else:
                    error_detail = response.text
                    try:
                        err_json = response.json()
                        error_detail = err_json.get("error", {}).get("message", response.text)
                    except Exception:
                        pass

                    # 429 Prepayment Hatası Açıklaması
                    if response.status_code == 429 and "prepayment" in error_detail.lower():
                        msg = (
                            "Google AI Studio 429 Hatası: Seçili proje ücretli (prepayment) plana bağlanmış ve kredi bakiyesi $0 görünüyor. "
                            "Çözüm: Google AI Studio (aistudio.google.com/app/apikey) ekranında 'Create API key in new project' "
                            "(yeni projede anahtar oluştur) seçeneğiyle tamamen ücretsiz bir API anahtarı alabilirsiniz."
                        )
                        return {
                            "success": False,
                            "message": msg,
                            "model": model_to_use,
                            "error_code": 429
                        }

                    # 404 Model Bulunamadı Hatası
                    if response.status_code == 404 or "not found" in error_detail.lower():
                        msg = (
                            f"Model '{model_to_use}' bu API anahtarı için bulunamadı veya kullanımdan kaldırılmış. "
                            "Lütfen 'gemini-1.5-flash' veya 'gemini-2.0-flash' modelini seçiniz."
                        )
                        return {
                            "success": False,
                            "message": msg,
                            "model": model_to_use,
                            "error_code": 404
                        }

                    return {
                        "success": False,
                        "message": f"Gemini API Hatası ({response.status_code}): {error_detail}",
                        "model": model_to_use
                    }
        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "Bağlantı zaman aşımına uğradı (10 sn). Lütfen internet bağlantınızı kontrol ediniz.",
                "model": model_to_use
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Bağlantı hatası: {str(e)}",
                "model": model_to_use
            }

    def translate_texts_batch(self, items: Dict[str, str], target_lang: str = "en") -> Dict[str, str]:
        """
        Birden fazla metin alanını tek bir istekte JSON formatında çevirir.
        Hibrit model: Sadece serbest metinler buraya gelir.
        """
        if not self.is_configured() or not items:
            return items

        # Boş olmayan metinleri filtrele
        to_translate = {k: v for k, v in items.items() if v and isinstance(v, str) and len(v.strip()) > 1}
        if not to_translate:
            return items

        prompt = (
            "You are a professional chemical safety expert and translator specializing in "
            "EU REACH Annex II (Regulation (EU) 2020/878) and CLP Regulation (EC) No 1272/2008 SDS authoring.\n"
            "Translate the following Turkish chemical safety data sheet phrases, descriptions, and user notes into "
            "precise, professional, formal English for an SDS document.\n\n"
            "Input JSON:\n"
            f"{json.dumps(to_translate, ensure_ascii=False, indent=2)}\n\n"
            "Instructions:\n"
            "- Return a JSON object with the exact same keys.\n"
            "- Values must be the accurate English translations.\n"
            "- Preserve chemical terminology, standard phrases, and safety nuances.\n"
            "- Return ONLY valid JSON, no markdown codeblocks or surrounding explanations."
        )

        url = f"{GEMINI_API_URL}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1,
                "maxOutputTokens": 4096
            }
        }

        try:
            with httpx.Client(timeout=25.0) as client:
                response = client.post(url, json=payload, headers={"Content-Type": "application/json"})
                
                # If model not found or deprecated, try gemini-1.5-flash
                if response.status_code == 404 and self.model != "gemini-1.5-flash":
                    logger.warning(f"Model {self.model} 404 döndürdü, gemini-1.5-flash deneniyor...")
                    fallback_url = f"{GEMINI_API_URL}/gemini-1.5-flash:generateContent?key={self.api_key}"
                    response = client.post(fallback_url, json=payload, headers={"Content-Type": "application/json"})

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        
                        # JSON temizliği
                        clean_json = text_content
                        if clean_json.startswith("```json"):
                            clean_json = clean_json[7:]
                        if clean_json.startswith("```"):
                            clean_json = clean_json[3:]
                        if clean_json.endswith("```"):
                            clean_json = clean_json[:-3]
                        clean_json = clean_json.strip()

                        translated_dict = json.loads(clean_json)
                        
                        result = dict(items)
                        for k, trans_v in translated_dict.items():
                            if k in result and trans_v:
                                result[k] = str(trans_v).strip()
                        logger.info(f"Gemini AI {len(result)} alanı başarıyla İngilizceye çevirdi.")
                        return result
                else:
                    logger.warning(f"Gemini çeviri başarısız ({response.status_code}): {response.text}")
        except Exception as e:
            logger.error(f"Gemini çeviri sırasında istisna: {e}")

        # Başarısız olursa orijinal metinleri geri dön (Kural bazlı çeviriye geri düş)
        return items


gemini_service = GeminiService()
