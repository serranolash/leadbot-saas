#!/usr/bin/env bash
set -euo pipefail

# --- Debug: muestra las URLs (sin el token) ---
echo "REDIS_URL=${REDIS_URL%%@*}@***"
echo "CELERY_BROKER_URL=${CELERY_BROKER_URL%%@*}@***"
echo "CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND%%@*}@***"

# Falla si vienen placeholders
if echo "$REDIS_URL$CELERY_BROKER_URL$CELERY_RESULT_BACKEND" | grep -qE '<PORT>|<HOST>|<PASS>'; then
  echo "❌ Variables Redis inválidas (contienen placeholders). Abortando." >&2
  exit 1
fi

# --- Procesos ---
# worker
celery -A app.worker.celery worker --loglevel=INFO &

# beat
celery -A app.worker.celery beat --loglevel=INFO --schedule /tmp/celerybeat-schedule &

# api
uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
