import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory is always the backend folder
BACKEND_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BACKEND_DIR / "sds_hazirlayici.db"

class Settings(BaseSettings):
    APP_NAME: str = "KKDİK SDS Hazırlayıcı API"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE.as_posix()}")
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
