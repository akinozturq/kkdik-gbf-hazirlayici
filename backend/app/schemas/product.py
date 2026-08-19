"""
Ürün CRUD Pydantic Şemaları
"""

import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.sds_sections import SDSModel


class ProductBase(BaseModel):
    urun_adi: str = Field(..., min_length=1, max_length=255, description="Ürün ticari veya kimyasal adı")
    ticari_kod: str = Field(..., min_length=1, max_length=100, description="Ürün stok / ticari kodu")
    kategori: Optional[str] = Field(None, max_length=100, description="Ürün ailesi veya kategorisi")


class ProductCreate(ProductBase):
    kategori: str = Field(..., min_length=1, max_length=100, description="Ürün ailesi / kategorisi (Zorunlu)")
    sds_data: Optional[SDSModel] = Field(default_factory=SDSModel, description="Ürüne ait 16 bölümlük SDS verisi")


class ProductUpdate(BaseModel):
    urun_adi: Optional[str] = Field(None, min_length=1, max_length=255)
    ticari_kod: Optional[str] = Field(None, min_length=1, max_length=100)
    kategori: Optional[str] = Field(None, max_length=100)
    sds_data: Optional[Dict[str, Any]] = Field(None, description="Güncellenecek SDS verisi (tam veya kısmi)")


class ProductDuplicateRequest(BaseModel):
    yeni_urun_adi: Optional[str] = Field(None, description="Kopyalanacak yeni ürün adı (varsayılan: [Orijinal Ad] - Kopya)")
    yeni_ticari_kod: Optional[str] = Field(None, description="Kopyalanacak yeni ticari kod (varsayılan: [Orijinal Kod]-COPY)")


class ProductListItem(BaseModel):
    id: int
    urun_adi: str
    ticari_kod: str
    kategori: Optional[str] = None
    olusturma_tarihi: datetime.datetime
    son_guncelleme: datetime.datetime
    tamamlanma_yuzdesi: Optional[float] = Field(None, description="SDS tamamlanma oranı (0-100)")
    dogrulama_durumu: Optional[str] = Field(None, description="Gecerli, Uyarili veya Hatali")

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductBase):
    id: int
    olusturma_tarihi: datetime.datetime
    son_guncelleme: datetime.datetime
    sds_data: SDSModel

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ProductListItem]
