"""
KKDİK Uyumlu Güvenlik Bilgi Formu (SDS) Hazırlayıcısı — FastAPI Backend Uygulaması
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, run_auto_migrations
from app.routers import products_router, references_router, ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama başlangıcında veritabanı tablolarını ve kolon migrasyonlarını çalıştır
    run_auto_migrations()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "KKDİK Ek-2 ve SEA yönetmeliklerine tam uyumlu, 16 bölümlük Güvenlik Bilgi Formu (SDS/GBF) "
        "hazırlama, doğrulama ve ürün yönetim API'si."
    ),
    lifespan=lifespan
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları kaydet
app.include_router(products_router)
app.include_router(references_router)
app.include_router(ai_router)


@app.get("/", tags=["Sistem"])
def root_info():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "active",
        "docs_url": "/docs",
        "endpoints": {
            "products": "/api/products",
            "h_statements": "/api/references/h-statements",
            "p_statements": "/api/references/p-statements",
            "pictograms": "/api/references/pictograms",
        }
    }


@app.get("/api/health", tags=["Sistem"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
