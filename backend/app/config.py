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
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

def save_env_setting(key: str, value: str):
    """Saves a setting to the .env file and updates runtime settings."""
    env_file = BACKEND_DIR / ".env"
    lines = []
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

    found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}\n")

    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    os.environ[key] = value
    if hasattr(settings, key):
        setattr(settings, key, value)

settings = Settings()
