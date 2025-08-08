from celery import Celery
from .settings import settings
from .utils.crypto import decrypt_obj, encrypt_obj
from .services.pipeline import run_pipeline

celery = Celery(__name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

@celery.task
def run_job(tenant_creds_map_token: str, query: str, target: int, min_score: int, min_groups: int, min_years: int):
    tenant_creds_map = decrypt_obj(tenant_creds_map_token)
    return run_pipeline(tenant_creds_map, query, target, min_score, min_groups, min_years)

@celery.task
def ping():
    return {"status": "ok"}
