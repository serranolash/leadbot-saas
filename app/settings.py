from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "LeadBot Sheet SaaS"
    APP_ENV: str = "dev"
    SECRET_KEY: str = "change_me"
    CRYPTO_FERNET_KEY: str = "REPLACE_WITH_FERNET_KEY"

    DATABASE_URL: str = "sqlite:///./leadbot.db"

    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    EXPORT_DIR: str = "./exports"

    ENABLE_LINKEDIN: bool = False
    ENABLE_COMPUTRABAJO: bool = True

    # Celery Beat simple demo
    DEMO_QUERY: Optional[str] = None             # e.g. "java backend 5 años ecommerce"
    DEMO_TARGET: int = 10
    DEMO_MIN_SCORE: int = 6
    DEMO_MIN_GROUPS: int = 2
    DEMO_MIN_YEARS: int = 0
    # JSON plano con credenciales mínimas para demo (se aceptan solo para demo/local):
    # {"linkedin": {"user":"...", "pass":"...", "chrome_profile": "...", "chrome_binary": "..."},
    #  "computrabajo": {}}
    DEMO_CREDS_JSON: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
