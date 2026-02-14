# Tasks Pendientes - ClientFlow Pro

## 🔴 URGENTE: Fix Login en Frontend
**Estado:** Pendiente  
**Prioridad:** Alta

### Problema
El login en el frontend no funciona. Posibles causas:
- URL de API incorrecta (REACT_APP_API_URL)
- CORS issues entre Vercel y Railway
- Manejo de tokens incorrecto
- Endpoint de login no respondiendo

### Pasos para debuggear
1. [ ] Verificar que `REACT_APP_API_URL` esté configurado en Vercel
2. [ ] Probar login manualmente con curl desde frontend
3. [ ] Revisar CORS en backend (Railway)
4. [ ] Verificar que el endpoint `/api/auth/login` funcione
5. [ ] Revisar manejo de tokens en AuthContext.js

### Criterios de éxito
- Login con demo@clientflow.pro / demo123 funciona
- Token se guarda correctamente
- Redirección a /dashboard funciona

---

## 🟡 Mostrar Todos los Elementos Creados en Frontend
**Estado:** Pendiente  
**Prioridad:** Media

### Problema
El frontend no muestra todos los elementos creados:
- Clientes no aparecen en lista
- Citas no se visualizan
- Leads no se muestran
- Disponibilidad no carga

### Posibles causas
- Endpoints de API no conectados
- Componentes no hacen fetch correctamente
- Renderizado condicional incorrecto
- Estados vacíos no manejan loading apropiadamente

### Pasos
1. [ ] Verificar que todos los endpoints de API funcionen:
   - GET /api/users/clients
   - GET /api/appointments
   - GET /api/leads
   - GET /api/availability
2. [ ] Revisar que los componentes hagan fetch al montarse
3. [ ] Verificar manejo de estado (loading, error, empty)
4. [ ] Probar creación de elementos y verificar que aparezcan

### Criterios de éxito
- Lista de clientes carga y muestra datos
- Citas aparecen en el calendario/lista
- Leads se visualizan
- Datos de perfil se cargan

---

## Notas
- Backend: https://clientflow-pro-production.up.railway.app
- Frontend: https://clientflow-pro.vercel.app
- Demo: demo@clientflow.pro / demo123
