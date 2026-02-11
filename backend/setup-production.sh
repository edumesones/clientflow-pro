#!/bin/bash
# Setup completo para producción de ClientFlow Pro
# Uso: ./setup-production.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🚀 ClientFlow Pro - Setup de Producción${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# 1. Verificar variables requeridas
echo -e "${YELLOW}📋 Verificando variables de entorno...${NC}"

required_vars=(
    "DATABASE_URL"
    "SECRET_KEY"
    "SMTP_HOST"
    "SMTP_USER"
    "SMTP_PASSWORD"
    "OPENAI_API_KEY"
)

optional_vars=(
    "REDIS_URL"
    "WHATSAPP_API_KEY"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=($var)
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "${RED}❌ Variables requeridas faltantes:${NC}"
    printf '%s\n' "${missing_vars[@]}"
    echo ""
    echo -e "${YELLOW}Por favor configura estas variables en Railway:${NC}"
    echo "https://railway.app/dashboard"
    exit 1
fi

echo -e "${GREEN}✅ Variables requeridas configuradas${NC}"

# 2. Verificar directorio
if [ ! -f "app/main.py" ]; then
    echo -e "${RED}❌ Error: No estás en el directorio backend/${NC}"
    echo "Por favor corre: cd backend && ./setup-production.sh"
    exit 1
fi

# 3. Instalar dependencias
echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencias instaladas${NC}"

# 4. Crear tablas
echo -e "${YELLOW}📊 Creando tablas de base de datos...${NC}"
python -c "
from app.core.database import engine
from app.models.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Tablas creadas')
"

# 5. Crear usuario demo
echo -e "${YELLOW}👤 Creando usuario demo...${NC}"
python << 'PYTHON_SCRIPT'
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.models import User, UserRole, Professional
from sqlalchemy import select

db = SessionLocal()
try:
    # Verificar si existe
    result = db.execute(select(User).where(User.email == 'demo@clientflow.pro'))
    existing = result.scalar_one_or_none()
    
    if not existing:
        # Crear usuario
        user = User(
            email='demo@clientflow.pro',
            hashed_password=get_password_hash('demo123'),
            full_name='Dr. Ana García',
            phone='+5215512345678',
            role=UserRole.PROFESSIONAL,
            is_active=True
        )
        db.add(user)
        db.flush()  # Para obtener user.id
        
        # Crear perfil profesional
        professional = Professional(
            user_id=user.id,
            slug='dr-ana-garcia',
            bio='Especialista en atención personalizada con más de 10 años de experiencia.',
            specialty='Consultoría Profesional',
            timezone='America/Mexico_City',
            appointment_duration=60,
            buffer_time=15,
            advance_booking_days=30,
            is_accepting_appointments=True
        )
        db.add(professional)
        db.commit()
        print('✅ Usuario demo y perfil profesional creados')
    else:
        print('✅ Usuario demo ya existe')
finally:
    db.close()
PYTHON_SCRIPT

# 6. Verificar Email
echo -e "${YELLOW}📧 Verificando configuración de email...${NC}"
python << 'PYTHON_SCRIPT'
import smtplib
from app.core.config import settings

try:
    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    server.starttls()
    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    server.quit()
    print('✅ Email configurado correctamente')
except Exception as e:
    print(f'⚠️  Error conectando a SMTP: {e}')
    print('   El email puede no funcionar correctamente')
PYTHON_SCRIPT

# 7. Verificar OpenAI
echo -e "${YELLOW}🧠 Verificando OpenAI...${NC}"
python << 'PYTHON_SCRIPT'
import openai
from app.core.config import settings

if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY
    try:
        response = openai.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': 'Hola'}],
            max_tokens=5
        )
        print('✅ OpenAI configurado correctamente')
    except Exception as e:
        print(f'⚠️  Error conectando a OpenAI: {e}')
        print('   Los agentes de IA no funcionarán')
else:
    print('⚠️  OPENAI_API_KEY no configurado')
PYTHON_SCRIPT

# 8. Verificar Redis (opcional)
if [ -n "$REDIS_URL" ]; then
    echo -e "${YELLOW}📨 Verificando Redis...${NC}"
    python << 'PYTHON_SCRIPT'
import redis
from app.core.config import settings

try:
    r = redis.from_url(settings.REDIS_URL)
    r.ping()
    print('✅ Redis configurado correctamente')
    print('   Los agentes correrán automáticamente')
except Exception as e:
    print(f'⚠️  Error conectando a Redis: {e}')
    print('   Los agentes no correrán automáticamente')
    PYTHON_SCRIPT
else
    echo -e "${YELLOW}⚠️  REDIS_URL no configurado${NC}"
    echo "   Agrega Redis en Railway para activar agentes automáticos"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 Setup completado!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📋 Próximos pasos:${NC}"
echo "  1. Verifica que el backend esté corriendo"
echo "  2. Configura el frontend en Vercel"
echo "  3. Agrega REDIS para agentes automáticos (opcional)"
echo ""
echo -e "${BLUE}👤 Credenciales demo:${NC}"
echo "  Email: demo@clientflow.pro"
echo "  Password: demo123"
echo ""
echo -e "${BLUE}🔗 URLs:${NC}"
echo "  API: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo ""
