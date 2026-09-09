import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from app.database import Base

def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    urun_adi = Column(String(255), nullable=False, index=True)
    ticari_kod = Column(String(100), nullable=False, index=True)
    kategori = Column(String(100), nullable=True, index=True)
    olusturma_tarihi = Column(DateTime, default=get_utc_now, nullable=False)
    son_guncelleme = Column(
        DateTime,
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False
    )
    sds_data = Column(JSON, nullable=False, default=dict)
    tamamlanma_yuzdesi = Column(Float, nullable=False, default=0.0)
    dogrulama_durumu = Column(String(50), nullable=False, default="Eksik / Hatalı")

    def __repr__(self):
        return f"<Product(id={self.id}, urun_adi='{self.urun_adi}', ticari_kod='{self.ticari_kod}')>"

