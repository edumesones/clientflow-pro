from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, professionals, appointments, leads, availability, dashboard, public

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas al iniciar
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed en producción si está habilitado
    if os.getenv("AUTO_SEED", "false").lower() == "true":
        try:
            from app.core.database import SessionLocal
            from app.core.security import get_password_hash
            from app.models.models import User, UserRole
            
            db = SessionLocal()
            try:
                # Verificar si existe usuario demo
                existing = db.query(User).filter(User.email == "demo@clientflow.pro").first()
                if not existing:
                    user = User(
                        email="demo@clientflow.pro",
                        hashed_password=get_password_hash("demo123"),
                        full_name="Dr. Ana García",
                        role=UserRole.PROFESSIONAL,
                        is_active=True
                    )
                    db.add(user)
                    db.commit()
                    print("✅ Usuario demo creado automáticamente")
            finally:
                db.close()
        except Exception as e:
            print(f"⚠️ Error en auto-seed: {e}")
    
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

@app.get("/create-demo")
async def create_demo_user():
    """Crea el usuario demo directamente."""
    try:
        from app.core.database import SessionLocal
        from app.core.security import get_password_hash
        from app.models.models import User, UserRole
        from sqlalchemy import select
        
        db = SessionLocal()
        try:
            # Verificar si ya existe
            result = db.execute(select(User).where(User.email == "demo@clientflow.pro"))
            existing = result.scalar_one_or_none()
            
            if existing:
                return {"status": "exists", "message": "User demo@clientflow.pro already exists"}
            
            # Crear usuario
            user = User(
                email="demo@clientflow.pro",
                hashed_password=get_password_hash("demo123"),
                full_name="Dr. Ana García",
                role=UserRole.PROFESSIONAL,
                is_active=True
            )
            db.add(user)
            db.commit()
            
            return {"status": "success", "message": "Demo user created", "email": "demo@clientflow.pro", "password": "demo123"}
        finally:
            db.close()
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

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

@app.get("/setup")
async def setup_database():
    """Inicializa la base de datos y crea datos de ejemplo."""
    try:
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        
        # Importar y ejecutar seed
        from scripts.seed_data import seed_data
        import io
        import sys
        
        # Capturar el output de seed_data
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        try:
            seed_data(force=True)
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            if "Datos de ejemplo cargados" in output or "ya contiene datos" in output:
                return {"status": "success", "message": "Database initialized with demo data", "details": output}
            else:
                return {"status": "success", "message": "Database tables created"}
        except SystemExit:
            # seed_data puede llamar a sys.exit
            output = buffer.getvalue()
            sys.stdout = old_stdout
            return {"status": "success", "message": "Database initialized", "details": output}
        except Exception as e:
            sys.stdout = old_stdout
            return {"status": "success", "message": "Database tables created (seed may need manual run)"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/init")
async def init_db_alternate():
    """Endpoint alternativo para inicializar la base de datos."""
    try:
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        
        # Importar y ejecutar seed
        from scripts.seed_data import seed_data
        import io
        import sys
        
        # Capturar el output de seed_data
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        try:
            seed_data(force=True)
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            if "Datos de ejemplo cargados" in output or "ya contiene datos" in output:
                return {"status": "success", "message": "Database initialized with demo data", "details": output}
            else:
                return {"status": "success", "message": "Database tables created"}
        except SystemExit:
            output = buffer.getvalue()
            sys.stdout = old_stdout
            return {"status": "success", "message": "Database initialized", "details": output}
        except Exception as e:
            sys.stdout = old_stdout
            return {"status": "success", "message": "Database tables created (seed may need manual run)"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
