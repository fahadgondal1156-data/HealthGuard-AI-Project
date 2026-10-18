from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "HealthGuard-AI"
    app_env: str = "development"
    database_url: str = "sqlite:///./healthguard.db"
    jwt_secret: str = "development-only-change-me-32-bytes-minimum-key"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    model_dir: str = "models/24h"
    alert_threshold_override: float | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_ignore_empty=True)

settings = Settings()
ROOT = Path(__file__).resolve().parents[2]
