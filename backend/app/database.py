import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

import logging

logger = logging.getLogger(__name__)

# SQLite requires check_same_thread=False for multithreaded FastAPI apps
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_auto_migrations():
    """
    Var olan SQLite veritabanı şemasını dinamik olarak modellerle senkronize eder.
    create_all() sadece yeni tabloları açtığından, mevcut tablolara eklenen yeni
    kolonları (tamamlanma_yuzdesi, dogrulama_durumu vb.) otomatik olarak ekler.
    """
    Base.metadata.create_all(bind=engine)

    # Sadece SQLite için dinamik kolon kontrolü
    if settings.DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            try:
                # products tablosu var mı kontrol et
                res = conn.execute(text("PRAGMA table_info(products)")).fetchall()
                if res:
                    existing_cols = {row[1] for row in res}
                    
                    if "tamamlanma_yuzdesi" not in existing_cols:
                        conn.execute(text("ALTER TABLE products ADD COLUMN tamamlanma_yuzdesi FLOAT DEFAULT 0.0"))
                        conn.commit()
                        
                    if "dogrulama_durumu" not in existing_cols:
                        conn.execute(text("ALTER TABLE products ADD COLUMN dogrulama_durumu VARCHAR(50) DEFAULT 'Eksik / Hatalı'"))
                        conn.commit()

                    if "kategori" not in existing_cols:
                        conn.execute(text("ALTER TABLE products ADD COLUMN kategori VARCHAR(100)"))
                        conn.commit()

                # 0.0 olan veya güncellenmemiş eski kayıtların tamamlanma yüzdelerini senkronize et
                products = conn.execute(text("SELECT id, sds_data FROM products WHERE tamamlanma_yuzdesi = 0.0")).fetchall()
                if products:
                    import json
                    from app.services.validator_service import validator_service
                    for p_id, sds_raw in products:
                        try:
                            sds_dict = json.loads(sds_raw) if isinstance(sds_raw, str) else (sds_raw or {})
                            val_res = validator_service.validate_sds(sds_dict)
                            stat = "Eksik / Hatalı" if val_res.total_errors > 0 else ("Uyarılı" if val_res.total_warnings > 0 else "Eksiksiz")
                            conn.execute(
                                text("UPDATE products SET tamamlanma_yuzdesi = :pct, dogrulama_durumu = :stat WHERE id = :id"),
                                {"pct": val_res.overall_completion_percentage, "stat": stat, "id": p_id}
                            )
                        except Exception as row_err:
                            logger.debug(f"[AutoMigration] Ürün {p_id} tamamlanma yüzdesi hesaplanamadı: {row_err}")
                    conn.commit()
            except Exception as e:
                logger.warning(f"[AutoMigration Warning] {e}")
