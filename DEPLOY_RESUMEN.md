# 🚀 RESUMEN DE DESPLIEGUE - ClientFlow Pro

## ✅ Estado Actual: TODO PREPARADO

Todo el proyecto está configurado y listo para desplegar. Solo faltan 3 comandos.

---

## 📋 PASOS PARA DESPLEGAR (Ejecutar en orden)

### 1️⃣ Ir al directorio del frontend
```bash
cd /home/lobster/.openclaw/workspace/clientflow-pro/frontend
```

### 2️⃣ Login en Vercel (solo la primera vez)
```bash
npx vercel login
```
> Esto abrirá un navegador para autenticarte con tu cuenta de Vercel.

### 3️⃣ Desplegar a producción
```bash
npx vercel --prod
```

---

## 🔗 URL ESPERADA DEL FRONTEND

Después del despliegue, tu frontend estará disponible en:
```
https://clientflow-pro-frontend-[random].vercel.app
```

O si configuras un dominio personalizado:
```
https://tu-dominio.com
```

---

## ⚙️ CONFIGURAR VARIABLES DE ENTORNO

Después del primer despliegue, debes configurar las variables:

### Opción A: Por CLI
```bash
cd /home/lobster/.openclaw/workspace/clientflow-pro/frontend
npx vercel env add REACT_APP_API_URL
# Ingresa la URL de tu backend cuando te lo pida

npx vercel env add REACT_APP_WS_URL  
# Ingresa la URL WebSocket de tu backend
```

### Opción B: Por Dashboard
1. Ve a https://vercel.com/dashboard
2. Haz clic en tu proyecto
3. Ve a "Settings" → "Environment Variables"
4. Agrega:
   - `REACT_APP_API_URL` = URL de tu backend
   - `REACT_APP_WS_URL` = URL WebSocket del backend

### Valores de ejemplo (para desarrollo local):
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### Valores de ejemplo (con backend en Railway):
```
REACT_APP_API_URL=https://clientflow-api.up.railway.app
REACT_APP_WS_URL=wss://clientflow-api.up.railway.app
```

> ⚠️ **IMPORTANTE**: Después de cambiar variables, re-deploy:
> ```bash
> npx vercel --prod
> ```

---

## 🖥️ BACKEND - DÓNDE DESPLEGAR

Vercel NO soporta Python/FastAPI nativamente. Opciones para el backend:

| Servicio | Comando | Free Tier | URL |
|----------|---------|-----------|-----|
| **Railway** ⭐ | `railway up` | Sí (limitado) | https://railway.app |
| **Render** | Web UI | Sí (sleep) | https://render.com |
| **Fly.io** | `fly deploy` | Sí (con CC) | https://fly.io |
| **Heroku** | `git push heroku` | No (pago) | https://heroku.com |

Ver `DEPLOY.md` para instrucciones detalladas de cada opción.

---

## 📁 ARCHIVOS CREADOS

| Archivo | Descripción |
|---------|-------------|
| `frontend/vercel.json` | Configuración de build para Vercel |
| `frontend/deploy.sh` | Script interactivo de despliegue |
| `frontend/package.json` | Scripts de npm para deploy |
| `frontend/README.md` | Documentación específica del frontend |
| `DEPLOY.md` | Guía completa de despliegue (frontend + backend) |

---

## 🧪 VERIFICAR QUE TODO FUNCIONA

Después de desplegar:

1. **Abrir la URL del frontend** en navegador
2. **Verificar que carga** sin errores 404
3. **Probar login** (necesita backend funcionando)
4. **Revisar consola** (F12 → Console) por errores CORS

Si ves errores de CORS, actualiza el backend para permitir el dominio de Vercel:
```python
allow_origins=["https://tu-frontend.vercel.app"]
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### "The specified token is not valid"
```bash
npx vercel login
```

### "Cannot find module"
```bash
npm install
```

### 404 en rutas de la app
El `vercel.json` está configurado correctamente. Si persisten, verifica que el archivo esté en el directorio `frontend/`.

### Errores CORS
El backend debe permitir el origen:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-frontend.vercel.app"],
    ...
)
```

---

## 📞 COMANDOS ÚTILES

```bash
# Ver logs en tiempo real
npx vercel logs --url https://tu-app.vercel.app

# Abrir dashboard del proyecto
npx vercel

# Ver información del proyecto
npx vercel inspect

# Eliminar despliegue
npx vercel remove
```

---

## ✅ CHECKLIST FINAL

- [ ] Comandos de despliegue ejecutados
- [ ] URL del frontend anotada
- [ ] Variables de entorno configuradas en Vercel
- [ ] Backend desplegado en Railway/Render/Fly.io
- [ ] CORS configurado en backend con URL del frontend
- [ ] Login funciona en producción
- [ ] Todas las llamadas API responden correctamente

---

## 📚 MÁS INFORMACIÓN

- Guía completa: `DEPLOY.md`
- Docs de Vercel: https://vercel.com/docs
- Docs de React: https://create-react-app.dev/docs/deployment#vercel

---

¡Todo listo! Ejecuta los 3 comandos del inicio para desplegar. 🚀
