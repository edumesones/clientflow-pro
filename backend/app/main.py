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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
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
