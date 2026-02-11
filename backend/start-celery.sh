#!/bin/bash
# Script para iniciar Celery Worker y Beat
# Uso: ./start-celery.sh

echo "🚀 Iniciando Celery para ClientFlow Pro..."

# Verificar REDIS_URL
if [ -z "$REDIS_URL" ]; then
    echo "⚠️  REDIS_URL no configurado, usando localhost"
    export REDIS_URL="redis://localhost:6379/0"
fi

echo "📡 Usando Redis: $REDIS_URL"

# Iniciar Celery Worker en background
echo "👷 Iniciando Celery Worker..."
celery -A app.celery_config.celery_app worker --loglevel=info --concurrency=2 &
WORKER_PID=$!

# Iniciar Celery Beat en background
echo "⏰ Iniciando Celery Beat (scheduler)..."
celery -A app.celery_config.celery_app beat --loglevel=info &
BEAT_PID=$!

echo "✅ Celery iniciado!"
echo "   Worker PID: $WORKER_PID"
echo "   Beat PID: $BEAT_PID"
echo ""
echo "📋 Los agentes se ejecutarán automáticamente:"
echo "   - Remindy: Cada hora"
echo "   - Followup: Cada 2 horas"
echo "   - Brief: Cada 30 minutos"
echo ""
echo "🛑 Para detener: kill $WORKER_PID $BEAT_PID"

# Esperar a que terminen
wait $WORKER_PID
wait $BEAT_PID
