# ClientFlow Pro - Frontend

Aplicación React para la gestión de clientes, citas y leads.

## 🚀 Despliegue Rápido a Vercel

### Opción 1: Script Automático (Recomendado)
```bash
cd frontend
./deploy.sh
```

### Opción 2: Comandos Manuales
```bash
# 1. Login en Vercel (solo la primera vez)
npx vercel login

# 2. Deploy a producción
npx vercel --prod
```

### Opción 3: Conectando GitHub (Recomendado para CI/CD)
1. Sube el código a GitHub
2. Ve a https://vercel.com/new
3. Importa tu repositorio
4. Configura las variables de entorno
5. ¡Listo! Cada push a main se desplegará automáticamente

## ⚙️ Variables de Entorno

Crear archivo `.env.local` para desarrollo:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

Para producción, configurar en Vercel Dashboard:
1. Ve a tu proyecto en https://vercel.com/dashboard
2. Settings → Environment Variables
3. Agrega:
   - `REACT_APP_API_URL` = URL de tu backend
   - `REACT_APP_WS_URL` = URL WebSocket de tu backend

## 📦 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `npm start` | Inicia servidor de desarrollo |
| `npm run build` | Crea build de producción |
| `npm test` | Ejecuta tests |
| `npm run deploy` | Despliega a producción en Vercel |
| `npm run deploy:preview` | Despliega preview en Vercel |

## 🔧 Configuración de Build

El archivo `vercel.json` contiene la configuración para:
- Build con React Scripts
- SPA routing (todas las rutas → index.html)
- Caching de assets estáticos

## 🌐 Arquitectura

```
┌─────────────────┐         ┌──────────────────┐
│   Vercel        │ ──────► │  Backend API     │
│  (Frontend)     │  HTTP   │  (Railway/       │
│  React App      │         │   Render/etc)    │
└─────────────────┘         └──────────────────┘
       │                            │
       │                            ▼
       │                     ┌──────────────────┐
       │                     │   PostgreSQL/    │
       │                     │   SQLite         │
       │                     └──────────────────┘
       ▼
┌─────────────────┐
│  LocalStorage   │
│  (Auth Token)   │
└─────────────────┘
```

## 🐛 Troubleshooting

### Error: "Invalid token"
Ejecuta `npx vercel login` para autenticarte.

### Error: "Cannot find module"
Ejecuta `npm install` antes de desplegar.

### La app muestra 404 en rutas
El archivo `vercel.json` configura el routing SPA. Si modificas el build, asegúrate de mantener la configuración de routes.

### CORS Error
El backend debe permitir el origen de Vercel:
```python
allow_origins=["https://tu-app.vercel.app"]
```

## 📚 Documentación Completa

Ver [DEPLOY.md](../DEPLOY.md) para la guía completa incluyendo despliegue del backend.
