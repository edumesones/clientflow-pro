# 🔧 Configuración End-to-End Completa

## Servicios Requeridos para Automatización Total

### 1. 📧 EMAIL (SMTP) - Obligatorio
**Opciones:**

#### A) Gmail (Gratis, para desarrollo)
```bash
# Crear App Password:
# 1. Ir a https://myaccount.google.com/apppasswords
# 2. Generar contraseña para "ClientFlow Pro"
# 3. Copiar la contraseña de 16 caracteres

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tuemail@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App Password
```

#### B) SendGrid (Recomendado para producción)
```bash
# 1. Crear cuenta en https://sendgrid.com
# 2. Verificar dominio
# 3. Crear API Key
# 4. Usar SMTP Relay

SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxx  # API Key
```

#### C) AWS SES (Escalable)
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=AKIAxxxxxxxxxxxxx
SMTP_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### 2. 💬 WHATSAPP - Opcional pero recomendado

#### A) WhatsApp Business API (Meta) - Producción
```bash
# Requiere:
# 1. Business Manager verificado
# 2. Línea de negocio aprobada
# 3. Aproximación por partners (mensualidad ~$50-200)

WHATSAPP_API_KEY=xxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=xxxxxxxx
WHATSAPP_BUSINESS_ACCOUNT_ID=xxxxxxxx
```

#### B) CallMeBot (Gratis para pruebas)
```bash
# 1. Abrir WhatsApp
# 2. Enviar mensaje a +34 644 10 52 55 con "I allow callmebot to send me messages"
# 3. Recibir API Key

WHATSAPP_PROVIDER=callmebot
CALLMEBOT_API_KEY=xxxxxx
```

#### C) WhatsApp Web.js (Self-hosted)
```bash
# Requiere servidor Node.js adicional
# Escanea QR cada cierto tiempo
WHATSAPP_PROVIDER=webjs
WHATSAPP_WEBJS_URL=http://localhost:3001
```

---

### 3. 🧠 OPENAI - Obligatorio para Agentes IA

```bash
# 1. Ir a https://platform.openai.com
# 2. Crear API Key
# 3. Configurar límites de gasto (recomendado $20-50/mes)

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4  # o gpt-3.5-turbo para ahorrar
```

**Costos estimados:**
- GPT-4: ~$0.03-0.06 por interacción
- GPT-3.5: ~$0.002-0.004 por interacción
- 100 leads/mes con GPT-4: ~$15-30
- 100 leads/mes con GPT-3.5: ~$2-5

---

### 4. 🗄️ BASE DE DATOS - Ya configurado (Railway PostgreSQL)

Ya está configurado automáticamente por Railway.

```bash
DATABASE_URL=postgresql://...  # Auto-generado por Railway
```

---

### 5. 📨 REDIS - Para Celery (Agentes Automáticos)

```bash
# Agregar Redis en Railway Dashboard
# Se crea automáticamente REDIS_URL

REDIS_URL=redis://default:xxxx@containers-xxxxx.railway.app:6379
```

---

### 6. 🌐 DOMINIO PERSONALIZADO - Opcional

```bash
# Configurar en Vercel:
# 1. Comprar dominio o usar existente
# 2. Agregar a Vercel Project Settings
# 3. Configurar DNS

FRONTEND_URL=https://tudominio.com
```

---

## 📋 Variables de Entorno Completas

### Para Railway (Backend)
```bash
# Base de Datos (auto)
DATABASE_URL=postgresql://...

# Redis (auto después de agregar)
REDIS_URL=redis://...

# Seguridad
SECRET_KEY=super-secret-key-min-32-chars-long

# Email (configurar según proveedor)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=maria.consultora@gmail.com
SMTP_PASSWORD=abcd-efgh-ijkl-mnop
SMTP_FROM_NAME="María González"
SMTP_FROM_EMAIL=maria.consultora@gmail.com

# OpenAI (obligatorio)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4

# WhatsApp (opcional)
ENABLE_WHATSAPP=false
WHATSAPP_PROVIDER=callmebot
CALLMEBOT_API_KEY=xxxxxx

# Feature Flags
ENABLE_EMAIL=true
ENABLE_AI_FEATURES=true
AUTO_SEED=true

# Configuración de Negocio
DEFAULT_TIMEZONE=America/Mexico_City
DEFAULT_APPOINTMENT_DURATION=60
```

### Para Vercel (Frontend)
```bash
REACT_APP_API_URL=https://clientflow-pro-production.up.railway.app
REACT_APP_WS_URL=wss://clientflow-pro-production.up.railway.app
```

---

## 🚀 Script de Setup Automatizado

Crear archivo `setup-production.sh`:

```bash
#!/bin/bash
# Setup completo para producción

echo "🚀 Configurando ClientFlow Pro para producción..."

# 1. Verificar variables requeridas
required_vars=(
    "DATABASE_URL"
    "REDIS_URL"
    "SECRET_KEY"
    "SMTP_HOST"
    "SMTP_USER"
    "SMTP_PASSWORD"
    "OPENAI_API_KEY"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=($var)
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Variables faltantes:"
    printf '%s\n' "${missing_vars[@]}"
    exit 1
fi

echo "✅ Todas las variables configuradas"

# 2. Crear tablas
echo "📊 Creando tablas de base de datos..."
cd backend
python -c "
from app.core.database import engine
from app.models.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Tablas creadas')
"

# 3. Crear usuario demo
echo "👤 Creando usuario demo..."
python -c "
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.models import User, UserRole

db = SessionLocal()
if not db.query(User).filter(User.email == 'demo@clientflow.pro').first():
    user = User(
        email='demo@clientflow.pro',
        hashed_password=get_password_hash('demo123'),
        full_name='Dr. Ana García',
        role=UserRole.PROFESSIONAL,
        is_active=True
    )
    db.add(user)
    db.commit()
    print('✅ Usuario demo creado')
else:
    print('✅ Usuario demo ya existe')
db.close()
"

# 4. Verificar conexiones
echo "🔍 Verificando conexiones..."

# Email
python -c "
import smtplib
from app.core.config import settings
try:
    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    server.starttls()
    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    server.quit()
    print('✅ Email configurado correctamente')
except Exception as e:
    print(f'⚠️  Error email: {e}')
"

# OpenAI
python -c "
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
        print(f'⚠️  Error OpenAI: {e}')
"

# Redis
python -c "
import redis
from app.core.config import settings
if settings.REDIS_URL:
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print('✅ Redis configurado correctamente')
    except Exception as e:
        print(f'⚠️  Error Redis: {e}')
"

echo ""
echo "🎉 Setup completado!"
echo ""
echo "📋 Resumen:"
echo "  • Backend: https://tu-backend.railway.app"
echo "  • Frontend: https://tu-frontend.vercel.app"
echo "  • API Docs: https://tu-backend.railway.app/docs"
echo ""
echo "👤 Credenciales demo:"
echo "  Email: demo@clientflow.pro"
echo "  Password: demo123"
```

---

## 🧪 Testing del Flujo Completo

### Test 1: Email
```bash
curl -X POST https://tu-backend.railway.app/api/test/email \
  -H "Content-Type: application/json" \
  -d '{"to": "tuemail@gmail.com", "subject": "Test", "body": "Funciona!"}'
```

### Test 2: Agente Remindy
```bash
curl -X POST https://tu-backend.railway.app/api/agents/remindy/run
```

### Test 3: Crear Lead y Procesar
```bash
# Crear lead
curl -X POST https://tu-backend.railway.app/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Cliente",
    "email": "test@ejemplo.com",
    "message": "Necesito consulta"
  }'

# Procesar con Followup (reemplazar {lead_id})
curl -X POST https://tu-backend.railway.app/api/agents/followup/process-lead/{lead_id}
```

---

## 💰 Costos Mensuales Estimados

| Servicio | Costo | Notas |
|----------|-------|-------|
| **Railway** | $0-5 | Free tier generoso |
| **PostgreSQL** | $0 | Incluido en Railway |
| **Redis** | $0 | Incluido en Railway |
| **Email (SendGrid)** | $0 | 100 emails/día gratis |
| **OpenAI GPT-4** | $20-50 | Según volumen |
| **WhatsApp (CallMeBot)** | $0 | Gratis para pruebas |
| **Vercel** | $0 | Free tier |
| **Dominio** | $10-15/año | Opcional |
| **TOTAL** | **$20-70/mes** | Para operación completa |

---

## ✅ Checklist Pre-Launch

- [ ] Variables de entorno configuradas en Railway
- [ ] Email SMTP verificado (enviar test)
- [ ] OpenAI API Key funciona
- [ ] Redis agregado y conectado
- [ ] Usuario demo creado
- [ ] Frontend desplegado en Vercel
- [ ] CORS configurado con URL de Vercel
- [ ] Celery worker corriendo
- [ ] Celery beat (scheduler) corriendo
- [ ] Test de flujo completo exitoso
- [ ] Dominio personalizado (opcional)

---

## 🆘 Troubleshooting Común

### "Email no se envía"
- Verificar App Password (no usar contraseña normal de Gmail)
- Verificar que SMTP_PORT sea 587 (TLS)
- Verificar que ALLOW less secure apps esté deshabilitado (usar App Password)

### "OpenAI no responde"
- Verificar que la API Key tenga saldo
- Verificar límites de rate
- Intentar con GPT-3.5-turbo primero

### "Agentes no corren automáticamente"
- Verificar REDIS_URL configurado
- Verificar que Celery worker esté corriendo
- Verificar logs: `railway logs`

### "CORS error"
- Verificar CORS_ORIGINS incluye URL de Vercel
- Verificar no haya trailing slash

---

**¿Quieres que configuremos alguno de estos servicios específicos ahora?**
