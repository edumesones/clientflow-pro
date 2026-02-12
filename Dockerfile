FROM python:3.11-slim

WORKDIR /app

# Force rebuild: 2026-02-12 cache bust

# Copiar solo requirements primero (cache layer)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/ .

# Exponer puerto
EXPOSE $PORT

# Comando de inicio
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
