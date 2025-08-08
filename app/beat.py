import json
from celery.schedules import crontab
from .worker import celery, run_job, ping
from .settings import settings
from .utils.crypto import encrypt_obj

# Siempre tener al menos un heartbeat para verificar que Beat corre
celery.conf.beat_schedule = {
    "heartbeat-every-5-min": {
        "task": "app.worker.ping",
        "schedule": 300.0,  # cada 5 minutos
    }
}

# Job demo opcional vía env (para probar cron sin UI/DB)
# Define DEMO_QUERY y DEMO_CREDS_JSON con las credenciales (ojo seguridad).
if settings.DEMO_QUERY and settings.DEMO_CREDS_JSON:
    try:
        creds_map = json.loads(settings.DEMO_CREDS_JSON)
        token = encrypt_obj(creds_map)
        celery.conf.beat_schedule["demo-query-daily-9am"] = {
            "task": "app.worker.run_job",
            "schedule": crontab(hour=9, minute=0),
            "args": [
                token,
                settings.DEMO_QUERY,
                settings.DEMO_TARGET,
                settings.DEMO_MIN_SCORE,
                settings.DEMO_MIN_GROUPS,
                settings.DEMO_MIN_YEARS,
            ],
        }
    except Exception as e:
        print("[beat] DEMO_CREDS_JSON inválido:", e)
