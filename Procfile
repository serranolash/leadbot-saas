web: uvicorn app.main:app --host 0.0.0.0 --port 8000
worker: celery -A app.worker.celery worker --loglevel=INFO
beat: celery -A app.worker.celery beat --loglevel=INFO --schedule /tmp/celerybeat-schedule
