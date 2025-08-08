#!/usr/bin/env bash
set -e

# Inicia el worker en segundo plano
celery -A app.worker.celery worker --loglevel=INFO &

# Inicia el beat en segundo plano
celery -A app.worker.celery beat --loglevel=INFO --schedule /tmp/celerybeat-schedule &

# Inicia la API en primer plano (cambia app.main:app si tu punto de entrada es otro)
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
