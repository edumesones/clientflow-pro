# Railway Procfile
# Este archivo define cómo se ejecutan los procesos en Railway

# Proceso principal: FastAPI app
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Proceso de Celery Worker
worker: cd backend && celery -A app.celery_config.celery_app worker --loglevel=info --concurrency=2

# Proceso de Celery Beat (scheduler)
scheduler: cd backend && celery -A app.celery_config.celery_app beat --loglevel=info
