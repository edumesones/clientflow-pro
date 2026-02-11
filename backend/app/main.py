from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, professionals, appointments, leads, availability, dashboard, public

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas al iniciar (en desarrollo)
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)
    yield
    # Cleanup al cerrar (si es necesario)

app = FastAPI(
    title="ClientFlow Pro API",
    description="API para gestión de citas, leads y clientes",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Usar configuración desde settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas API
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(professionals.router, prefix="/api/professionals", tags=["Profesionales"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Citas"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(availability.router, prefix="/api/availability", tags=["Disponibilidad"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(public.router, prefix="/api/public", tags=["Público"])

@app.get("/")
async def root():
    return {
        "message": "ClientFlow Pro API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/init-db")
async def init_database():
    """Inicializa la base de datos y crea datos de ejemplo."""
    try:
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        
        # Importar y ejecutar seed
        from scripts.seed_data import seed_database
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            seed_database(db)
            db.commit()
            return {"status": "success", "message": "Database initialized with demo data"}
        except Exception as e:
            db.rollback()
            # Si ya existe el usuario, está bien
            return {"status": "success", "message": "Database already initialized"}
        finally:
            db.close()
    except Exception as e:
        return {"status": "error", "message": str(e)}
