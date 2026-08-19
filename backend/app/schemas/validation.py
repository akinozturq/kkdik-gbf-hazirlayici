"""
KKDİK SDS Doğrulama Şemaları
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


ValidationSeverity = Literal["ERROR", "WARNING", "INFO"]


class ValidationItem(BaseModel):
    section: str = Field(..., description="İlgili bölüm / alt bölüm kodu (ör. 'B1.1', 'B2.1', 'B3', 'B0.2.4')")
    field_path: str = Field(..., description="Veri modeli alan yolu (ör. 'b1_kimlik.b1_1.madde_karisim_adi')")
    message: str = Field(..., description="Kullanıcıya yönelik açıklayıcı doğrulama mesajı")
    regulation_ref: str = Field(..., description="KKDİK Ek-2 mevzuat referansı (ör. 'KKDİK Ek-2 md. 0.4')")
    severity: ValidationSeverity = Field("ERROR", description="Zorunluluk düzeyi: ERROR (engeller), WARNING (uyarı), INFO (bilgi)")


class SectionProgress(BaseModel):
    section_number: int = Field(..., description="Bölüm numarası (1 - 16)")
    section_code: str = Field(..., description="Bölüm kısa adı (ör. 'B1', 'B2')")
    section_title: str = Field(..., description="Bölüm resmi başlığı")
    total_subsections: int = Field(..., description="Toplam alt bölüm sayısı")
    filled_subsections: int = Field(..., description="Doldurulmuş alt bölüm sayısı")
    completion_percentage: float = Field(..., description="Bölüm doluluk yüzdesi (0.0 - 100.0)")
    has_errors: bool = Field(False, description="Bölümde hata var mı")
    has_warnings: bool = Field(False, description="Bölümde uyarı var mı")


class ValidationResult(BaseModel):
    is_valid_for_export: bool = Field(..., description="Resmi PDF/DOCX dışa aktarımına uygun mu (Hata yoksa True)")
    total_errors: int = Field(0, description="Toplam engelliyici hata sayısı")
    total_warnings: int = Field(0, description="Toplam uyarı sayısı")
    overall_completion_percentage: float = Field(0.0, description="Genel SDS tamamlanma yüzdesi")
    errors: List[ValidationItem] = Field(default_factory=list, description="Hata listesi")
    warnings: List[ValidationItem] = Field(default_factory=list, description="Uyarı listesi")
    section_progress: List[SectionProgress] = Field(default_factory=list, description="16 bölümün her birinin ilerleme durumu")
