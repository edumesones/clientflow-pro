# 🚀 Guía de Despliegue - ClientFlow Pro

## Frontend (Vercel) - LISTO PARA DESPLEGAR

### Paso 1: Autenticación en Vercel
```bash
cd /home/lobster/.openclaw/workspace/clientflow-pro/frontend
npx vercel login
```

### Paso 2: Deploy a Vercel
```bash
npx vercel --prod
```

### Variables de Entorno (Configurar en Vercel Dashboard)
Una vez desplegado, ve a tu proyecto en https://vercel.com/dashboard y configura:

| Variable | Valor (Desarrollo) | Valor (Producción Backend) |
|----------|-------------------|---------------------------|
| `REACT_APP_API_URL` | `http://localhost:8000` | URL de tu backend (ej: `https://api.tudominio.com`) |
| `REACT_APP_WS_URL` | `ws://localhost:8000` | URL WebSocket del backend |

> ⚠️ **IMPORTANTE**: Las variables `REACT_APP_*` deben configurarse ANTES del build. Cada cambio requiere re-deploy.

---

## Backend (Opciones)

Como Vercel es serverless y optimizado para Node.js, el backend Python/FastAPI necesita otro host:

### Opción 1: Railway (Recomendada) ⭐
```bash
# Instalar CLI
npm install -g @railway/cli

# Login y despliegue
cd /home/lobster/.openclaw/workspace/clientflow-pro/backend
railway login
railway init
railway up
```
- **Pros**: Fácil de usar, buen free tier, deploys automáticos
- **Cons**: Limitado en el plan gratuito
- **URL**: https://railway.app

### Opción 2: Render
1. Crear cuenta en https://render.com
2. New Web Service → Conectar tu repo
3. Configurar:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
4. Variables de entorno desde el archivo `.env`

- **Pros**: Free tier generoso, buena documentación
- **Cons**: Spin-up lento en plan gratuito (sleep después de inactividad)

### Opción 3: Fly.io
```bash
# Instalar CLI
curl -L https://fly.io/install.sh | sh

# Desplegar
cd /home/lobster/.openclaw/workspace/clientflow-pro/backend
fly launch
fly deploy
```
- **Pros**: Muy rápido, excelente para apps pequeñas
- **Cons**: Requiere tarjeta de crédito (aunque el free tier es gratis)

### Opción 4: DigitalOcean / AWS / GCP
Para producción a mayor escala.

---

## Configuración del Backend para Producción

### Variables de Entorno Necesarias
```bash
# Backend (.env)
DATABASE_URL=sqlite:///./clientflow.db  # O PostgreSQL en producción
SECRET_KEY=tu-clave-secreta-muy-larga
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (IMPORTANTE)
# Debes configurar el dominio de tu frontend en Vercel
CORS_ORIGINS=https://tu-frontend.vercel.app
```

### Cambios necesarios en el backend

1. **CORS**: Actualizar `app/main.py` para permitir el dominio de Vercel:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-frontend.vercel.app"],  # Tu dominio de Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Base de datos**: En producción, considera migrar de SQLite a PostgreSQL:
```python
# En app/core/database.py
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clientflow.db")
```

---

## Checklist de Despliegue

### Frontend (Vercel)
- [ ] Login en Vercel CLI
- [ ] Deploy ejecutado (`npx vercel --prod`)
- [ ] Variables de entorno configuradas en dashboard
- [ ] URL del frontend anotada

### Backend (Railway/Render/Fly.io)
- [ ] Servicio creado
- [ ] Variables de entorno configuradas
- [ ] CORS actualizado con URL del frontend
- [ ] Base de datos configurada
- [ ] URL del backend anotada

### Integración
- [ ] Actualizar `REACT_APP_API_URL` en Vercel con URL del backend
- [ ] Re-deploy del frontend con nueva configuración
- [ ] Probar login en la app desplegada
- [ ] Verificar que las llamadas API funcionan

---

## URLs Esperadas

| Servicio | URL Ejemplo |
|----------|--------------|
| Frontend Vercel | `https://clientflow-pro.vercel.app` |
| Backend Railway | `https://clientflow-api.up.railway.app` |
| Backend Render | `https://clientflow-api.onrender.com` |

---

## Soporte

Si encuentras problemas:
1. Revisar logs en Vercel Dashboard → deployments
2. Verificar CORS en el backend
3. Confirmar que las variables de entorno están seteadas
4. Revisar que el backend está accesible (health check)
