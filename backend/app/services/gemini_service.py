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

# Desteklenen ve fallback modeller
SUPPORTED_MODELS = [
    {"id": "gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash Lite (Hızlı & Ekonomik)", "recommended": True},
    {"id": "gemini-3.5-flash-lite", "name": "Gemini 3.5 Flash Lite", "recommended": False},
    {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "recommended": False},
    {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash (Klasik)", "recommended": False},
    {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro (Gelişmiş)", "recommended": False},
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
        return self._model or settings.GEMINI_MODEL or "gemini-2.5-flash-lite"

    def set_credentials(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if api_key is not None:
            self._api_key = api_key.strip()
            settings.GEMINI_API_KEY = self._api_key
        if model is not None:
            self._model = model.strip()
            settings.GEMINI_MODEL = self._model

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

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
                        {"text": "Translate the following phrase into English in 5 words or fewer: 'Kolay alevlenir sıvı ve buhar.'"}
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
                            "message": f"Bağlantı başarılı! Model yanıtı: '{text_part}'",
                            "model": model_to_use,
                            "response_sample": text_part
                        }
                    return {
                        "success": True,
                        "message": "Bağlantı başarılı ancak yanıt gövdesi boş.",
                        "model": model_to_use
                    }
                else:
                    error_detail = response.text
                    try:
                        err_json = response.json()
                        error_detail = err_json.get("error", {}).get("message", response.text)
                    except Exception:
                        pass
                    
                    # If model not found, try fallback to gemini-2.5-flash or gemini-1.5-flash
                    if "not found" in error_detail.lower() and model_to_use != "gemini-2.5-flash-lite":
                        logger.warning(f"Model {model_to_use} bulunamadı, gemini-2.5-flash-lite deneniyor...")
                        return self.test_connection(key_to_use, "gemini-2.5-flash-lite")

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
                "temperature": 0.1
            }
        }

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.post(url, json=payload, headers={"Content-Type": "application/json"})
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
                        return result
                else:
                    logger.warning(f"Gemini çeviri başarısız ({response.status_code}): {response.text}")
        except Exception as e:
            logger.error(f"Gemini çeviri sırasında istisna: {e}")

        # Başarısız olursa orijinal metinleri geri dön (Kural bazlı çeviriye geri düş)
        return items


gemini_service = GeminiService()
