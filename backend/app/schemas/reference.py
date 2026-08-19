"""
Referans Veri Şemaları (H-İfadeleri, P-İfadeleri, GHS Piktogramları)
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class HStatementItem(BaseModel):
    code: str = Field(..., description="H-kodu (ör. 'H225')")
    category: str = Field(..., description="Zararlılık grubu (Fiziksel, Sağlık, Çevre, İlave)")
    text: str = Field(..., description="Türkçe standart zararlılık ifadesi metni")


class PStatementItem(BaseModel):
    code: str = Field(..., description="P-kodu (ör. 'P210', 'P301+P310')")
    type: str = Field(..., description="Önlem türü (Genel, Önlem, Müdahale, Depolama, Bertaraf)")
    text: str = Field(..., description="Türkçe standart önlem ifadesi metni")


class PictogramItem(BaseModel):
    code: str = Field(..., description="Piktogram kodu (ör. 'GHS02')")
    name: str = Field(..., description="Piktogram Türkçe adı")
    symbol: str = Field(..., description="Sembol açıklaması")
    description: str = Field(..., description="Kapsadığı zararlılık sınıfları")


class AutoFillHResponse(BaseModel):
    product_id: int
    found_h_codes: List[str] = Field(default_factory=list, description="SDS içerisinden tespit edilen H-kodları")
    h_statements: List[HStatementItem] = Field(default_factory=list, description="Kodlara karşılık gelen tam Türkçe metinler")
    formatted_texts: List[str] = Field(default_factory=list, description="Bölüm 16'ya yazılmaya hazır biçimlendirilmiş metinler ('H225: Kolay alevlenir sıvı...')")
    updated_section16: bool = Field(False, description="Ürün Bölüm 16'sına otomatik kaydedildi mi")
