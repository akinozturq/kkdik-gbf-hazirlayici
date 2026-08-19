import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    urun_adi = Column(String(255), nullable=False, index=True)
    ticari_kod = Column(String(100), nullable=False, index=True)
    kategori = Column(String(100), nullable=True, index=True)
    olusturma_tarihi = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    son_guncelleme = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )
    sds_data = Column(JSON, nullable=False, default=dict)

    def __repr__(self):
        return f"<Product(id={self.id}, urun_adi='{self.urun_adi}', ticari_kod='{self.ticari_kod}')>"
