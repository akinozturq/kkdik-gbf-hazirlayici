"""
Google Gemini AI API Router'ı
Yapılandırma, bağlantı testi ve ürün çeviri API uçları
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Product
from app.config import settings, save_env_setting
from app.services.gemini_service import gemini_service, SUPPORTED_MODELS
from app.services.translation_service import translation_service

router = APIRouter(prefix="/api/ai", tags=["Gemini AI Çeviri"])


class AIConfigRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = "gemini-2.5-flash-lite"


class AITestRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None


@router.get("/config", summary="Mevcut AI yapılandırmasını ve model listesini getir")
def get_ai_config():
    key = gemini_service.api_key
    masked_key = ""
    if key:
        if len(key) > 8:
            masked_key = key[:6] + "..." + key[-4:]
        else:
            masked_key = "***"

    return {
        "is_configured": gemini_service.is_configured(),
        "api_key_masked": masked_key,
        "active_model": gemini_service.model,
        "supported_models": SUPPORTED_MODELS
    }


@router.post("/config", summary="Gemini API anahtarını ve aktif modeli kaydet")
def save_ai_config(req: AIConfigRequest):
    if req.api_key is not None:
        save_env_setting("GEMINI_API_KEY", req.api_key.strip())
    if req.model is not None:
        save_env_setting("GEMINI_MODEL", req.model.strip())

    gemini_service.set_credentials(
        api_key=req.api_key if req.api_key is not None else None,
        model=req.model if req.model is not None else None
    )

    return {
        "success": True,
        "message": "Gemini AI ayarları başarıyla kaydedildi.",
        "is_configured": gemini_service.is_configured(),
        "active_model": gemini_service.model
    }


@router.post("/test", summary="Gemini API bağlantısını ve model yanıtını test et")
def test_ai_connection(req: AITestRequest):
    result = gemini_service.test_connection(api_key=req.api_key, model=req.model)
    return result


@router.post("/translate-product/{product_id}", summary="Ürün SDS verilerini Gemini AI ile İngilizceye çevir")
def translate_product_sds(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{product_id} ID'li ürün bulunamadı."
        )

    sds_data = product.sds_data or {}
    translated_sds = translation_service.translate_sds_dict(sds_data, lang="en")
    
    return {
        "success": True,
        "product_id": product_id,
        "urun_adi": product.urun_adi,
        "translated_sds": translated_sds
    }
