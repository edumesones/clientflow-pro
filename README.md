# ClientFlow Pro - SaaS de Gestión de Clientes

## Descripción
ClientFlow Pro es un SaaS completo para profesionales que necesitan gestionar citas, leads y clientes de manera eficiente. Incluye calendario inteligente, seguimiento automático de leads, recordatorios multicanal y un mini-CRM.

## Características Principales

### 1. Calendario Inteligente
- Sistema de reservas donde los clientes pueden agendar citas directamente
- Disponibilidad configurable por profesional
- Sincronización de horarios

### 2. Seguimiento Automático de Leads
- Captura automática de leads desde formularios web
- Automatización de emails de seguimiento (día 1, 3, 7)
- Marcado de estado (nuevo, contactado, convertido, perdido)

### 3. Recordatorios Multicanal
- WhatsApp, SMS y Email
- Recordatorios 24h y 1h antes de la cita
- Solicitud de review post-cita

### 4. Mini-CRM
- Historial completo de clientes
- Notas y próximos pasos
- Estadísticas de conversión y no-shows

## Stack Técnico

- **Backend**: Python 3.11+ / FastAPI
- **Frontend**: React 18+ / TypeScript
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **ORM**: SQLAlchemy
- **Integraciones**: WhatsApp API, SMTP Email, SMS API

## Instalación

### Requisitos Previos
- Python 3.11 o superior
- Node.js 18 o superior
- Docker y Docker Compose (opcional pero recomendado)

### Instalación con Docker (Recomendado)

```bash
# Clonar el repositorio
cd clientflow-pro

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Iniciar todos los servicios
docker-compose up -d

# Verificar estado
docker-compose ps
```

### Instalación Manual

#### Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
python scripts/init_db.py

# Cargar datos de ejemplo
python scripts/seed_data.py

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tus configuraciones

# Iniciar servidor de desarrollo
npm start
```

## Estructura del Proyecto

```
clientflow-pro/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Rutas/endpoints
│   │   ├── core/           # Configuración y utilidades
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Esquemas Pydantic
│   │   ├── services/       # Lógica de negocio
│   │   └── utils/          # Utilidades
│   ├── tests/              # Tests
│   └── requirements.txt    # Dependencias Python
├── frontend/               # React App
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Páginas
│   │   ├── services/       # Servicios API
│   │   ├── context/        # Contextos React
│   │   └── styles/         # Estilos CSS
│   └── package.json        # Dependencias Node
├── database/               # Scripts de base de datos
│   ├── migrations/         # Migraciones Alembic
│   └── seed/               # Datos de ejemplo
├── integrations/           # Integraciones externas
│   ├── whatsapp/           # WhatsApp API
│   ├── email/              # SMTP Email
│   └── sms/                # SMS API
├── docs/                   # Documentación
├── docker-compose.yml      # Configuración Docker
└── README.md              # Este archivo
```

## Configuración

### Variables de Entorno Principales

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a la BD | `sqlite:///./clientflow.db` |
| `OPENAI_API_KEY` | API Key de OpenAI (opcional) | `sk-...` |
| `SECRET_KEY` | Clave secreta para JWT | `tu-clave-secreta` |
| `SMTP_HOST` | Servidor SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Puerto SMTP | `587` |
| `SMTP_USER` | Usuario SMTP | `tucorreo@gmail.com` |
| `SMTP_PASSWORD` | Contraseña SMTP | `tu-password` |
| `WHATSAPP_API_KEY` | API Key de WhatsApp Business | `...` |
| `SMS_API_KEY` | API Key de proveedor SMS | `...` |

## Uso

### Panel de Administración
Accede a `http://localhost:3000/admin` para gestionar:
- Calendario de citas
- Lista de leads
- Estadísticas
- Configuración

### Página Pública de Reserva
Cada profesional tiene una URL única:
```
http://localhost:3000/book/{professional_slug}
```

### API Documentation
La documentación interactiva de la API está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Datos de Demo

El sistema incluye datos de ejemplo para probar:

- **Usuario admin**: admin@clientflow.pro / admin123
- **Profesional demo**: demo@clientflow.pro / demo123
- **Slots de disponibilidad**: Lunes a Viernes, 9:00 - 18:00

## Desarrollo

### Ejecutar Tests
```bash
cd backend
pytest

cd frontend
npm test
```

### Formatear Código
```bash
cd backend
black app/
isort app/

cd frontend
npm run lint
npm run format
```

## Producción

### Checklist de Despliegue
- [ ] Configurar PostgreSQL
- [ ] Configurar variables de entorno de producción
- [ ] Configurar SSL/TLS
- [ ] Configurar backups automáticos
- [ ] Configurar monitoreo
- [ ] Configurar dominio personalizado

### Despliegue con Docker
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Licencia
MIT License - Ver LICENSE para más detalles.

## Soporte
Para soporte técnico, contactar a: soporte@clientflow.pro

## Roadmap
- [ ] Integración con Google Calendar
- [ ] App móvil nativa
- [ ] Sistema de pagos integrado
- [ ] IA para análisis de sentimiento de clientes
- [ ] Multi-tenant avanzado
