from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "LeadBot Sheet SaaS"
    APP_ENV: str = "dev"
    SECRET_KEY: str = "change_me"
    CRYPTO_FERNET_KEY: str = "QniwY3P8Lu1TipE5x5lEyeGL55Pg4QT9gpwyll807Is="

    DATABASE_URL: str = "sqlite:///./leadbot.db"

    # No defaults aquí: deben venir por ENV (Render)
    REDIS_URL: str
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    EXPORT_DIR: str = "./exports"

    ENABLE_LINKEDIN: bool = False
    ENABLE_COMPUTRABAJO: bool = True

    # Demo
    DEMO_QUERY: Optional[str] = None
    DEMO_TARGET: int = 10
    DEMO_MIN_SCORE: int = 6
    DEMO_MIN_GROUPS: int = 2
    DEMO_MIN_YEARS: int = 0
    DEMO_CREDS_JSON: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",               # para dev; en Render las ENV del sistema tienen prioridad
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("REDIS_URL", mode="after")
    @classmethod
    def _validate_redis_url(cls, v: str) -> str:
        assert v, "REDIS_URL vacía"
        assert "<PORT>" not in v and "<HOST>" not in v, "REDIS_URL contiene placeholders"
        return v

settings = Settings()

# Normalizamos: si no vienen, usamos REDIS_URL
BROKER_URL = settings.CELERY_BROKER_URL or settings.REDIS_URL
BACKEND_URL = settings.CELERY_RESULT_BACKEND or settings.REDIS_URL



settings = Settings()

