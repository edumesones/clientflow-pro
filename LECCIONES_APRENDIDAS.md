# Lecciones Aprendidas - ClientFlow Pro

## Resumen del Proyecto
**ClientFlow Pro** es una aplicación full-stack para gestión de citas, leads y clientes para profesionales.
- **Frontend:** React SPA desplegado en Vercel
- **Backend:** FastAPI desplegado en Railway
- **Base de datos:** PostgreSQL en Railway

---

## 🔴 Problema Principal: Los datos no se cargaban en el frontend

### Síntomas
- Login funcionaba correctamente
- Pero después de hacer login, el dashboard aparecía vacío o en "Cargando..." infinito
- No se podían ver citas, clientes ni leads
- No se podían crear nuevas citas

### Causa Raíz
**El token JWT no se estaba enviando en las peticiones autenticadas.**

### Por qué pasó esto

#### 1. Configuración del token en AuthContext (funcionaba solo parcialmente)
```javascript
// AuthContext.js - Después del login
localStorage.setItem('token', access_token);
api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
```

**Problema:** Esto funciona inmediatamente después del login, pero cuando:
- El usuario recarga la página
- Navega a otra sección
- Abre la app en una nueva pestaña

El header `api.defaults.headers` **no persiste** entre importaciones de módulos o recargas.

#### 2. Solución: Interceptor de request en Axios
```javascript
// api.js - La solución correcta
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

**Por qué funciona:** El interceptor se ejecuta **antes de cada petición HTTP**, garantizando que el token actual siempre se incluya.

---

## 🟡 Problema Secundario: Formatos de respuesta inconsistentes

### Síntomas
- Algunas páginas mostraban datos, otras no
- Errores de "cannot read property of undefined"

### Causa
El backend devolvía diferentes formatos según el endpoint:
- Algunos: `{ items: [...], total: X, page: X }` (paginado)
- Otros: `[...]` (array directo)

### Solución
Manejar ambos formatos con un fallback:
```javascript
// Antes (fallaba con formato paginado)
setClients(response.data);

// Después (funciona con ambos formatos)
const clientsData = response.data?.items || response.data || [];
setClients(clientsData);
```

---

## 🔧 Fixes Aplicados

### 1. Agregar interceptor de request en `api.js`
```javascript
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

### 2. Actualizar todos los componentes para manejar formato paginado
- `Dashboard.js`
- `AppointmentsPage.js`
- `ClientsPage.js`
- `LeadsPage.js`

### 3. Agregar endpoints faltantes en el backend
El frontend esperaba:
- `/api/dashboard/upcoming`
- `/api/dashboard/leads/recent`

Pero el backend tenía:
- `/api/dashboard/upcoming-appointments`
- `/api/dashboard/recent-leads`

**Solución:** Crear aliases en el backend para mantener compatibilidad.

---

## 🎯 Patrones y Mejores Prácticas Aprendidas

### 1. Siempre usar interceptores para autenticación
❌ **No hacer esto:**
```javascript
// Fragil - no persiste después de recargas
api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

✅ **Hacer esto:**
```javascript
// Robusto - se ejecuta en cada petición
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 2. Manejar múltiples formatos de respuesta
```javascript
// Defensivo: funciona con paginado o array directo
const data = response.data?.items || response.data || [];
```

### 3. Logging estratégico para debugging
```javascript
// En desarrollo, loguear la API URL y errores
console.log('API URL:', API_URL);
console.error('API Error:', error.message, error.response?.data);
```

### 4. CORS: Configurar correctamente en el backend
```python
# FastAPI - Permitir origen del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://clientflow-pro.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Variables de entorno en Vercel
Recordar que las variables de entorno en Vercel:
- Deben comenzar con `REACT_APP_` para ser accesibles en el frontend
- Necesitan un redeploy para aplicarse

```bash
# Configurar en Vercel
REACT_APP_API_URL=https://clientflow-pro-production.up.railway.app
```

---

## 🐛 Debugging: Técnicas útiles

### 1. Verificar el build en Vercel
```bash
# Verificar que el código está en el build
curl -s https://clientflow-pro.vercel.app/static/js/main.XXXX.js | grep "tu-codigo"
```

### 2. Probar endpoints manualmente
```bash
# Obtener token
TOKEN=$(curl -s -X POST "$API/api/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@clientflow.pro", "password": "demo123"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Probar endpoint
curl -s "$API/api/dashboard/stats" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Agregar debug visual en el UI
```javascript
// Mostrar información de debug en la interfaz
<div style={{fontSize: '11px', color: '#666'}}>
  Debug: API URL = {process.env.REACT_APP_API_URL}
</div>
```

---

## 📋 Checklist para próximos proyectos

- [ ] Configurar interceptor de request para token JWT
- [ ] Manejar formatos paginados y directos en el frontend
- [ ] Documentar formato de respuesta de cada endpoint
- [ ] Configurar CORS en backend con origen específico
- [ ] Agregar variables de entorno en Vercel con `REACT_APP_` prefix
- [ ] Implementar loading states y error handling en todos los componentes
- [ ] Agregar logs de debug en desarrollo
- [ ] Verificar que los endpoints del frontend existan en el backend

---

## 🚀 Arquitectura Final Funcional

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Vercel        │────▶│   Railway        │────▶│   PostgreSQL    │
│   (Frontend)    │     │   (FastAPI)      │     │   (Database)    │
│   React SPA     │◀────│   Backend        │◀────│                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
       │                         │
       │ 1. Login POST           │
       │────────────────────────▶│
       │                         │
       │ 2. Token + Refresh      │
       │◀────────────────────────│
       │                         │
       │ 3. API Calls con Auth   │
       │    Header: Bearer XXX   │
       │────────────────────────▶│
       │                         │
       │ 4. JSON Response        │
       │◀────────────────────────│
```

---

## Conclusión

El problema principal era un error de arquitectura en la autenticación: confiar en `api.defaults.headers` en lugar de un interceptor de request. 

**La lección más importante:** 
> En aplicaciones SPA con autenticación JWT, siempre usar interceptores de request para garantizar que cada petición incluya el token actualizado.

---

*Documento creado: 14 de febrero de 2026*
*Proyecto: ClientFlow Pro*
