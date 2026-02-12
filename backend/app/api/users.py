from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.auth import get_current_active_user, get_current_user
from app.schemas.schemas import (
    UserResponse,
    UserUpdate,
    ProfessionalCreate,
    ProfessionalResponse,
    ProfessionalUpdate,
    ClientResponse,
    ClientStats
)
from app.services.user_service import update_user, get_user_by_id
from app.services.professional_service import (
    create_professional, 
    get_professional_by_user_id,
    get_professional_by_id,
    update_professional
)
from app.models.models import User, UserRole, Appointment, AppointmentStatus, Professional
from sqlalchemy import func, distinct, Integer

router = APIRouter()


# ========== CLIENT ENDPOINTS (MUST BE BEFORE /{user_id}) ==========

def get_current_professional(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Professional:
    """Dependency para obtener el profesional actual"""
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a professional user"
        )
    return professional


@router.get("/clients", response_model=List[ClientResponse])
async def get_clients(
    status: Optional[str] = Query(None, description="Filter by status: active, inactive, vip"),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_professional: Professional = Depends(get_current_professional)
):
    """Obtener lista de clientes del profesional actual"""

    # Subquery para obtener la última cita de cada cliente
    last_appointment_subq = (
        db.query(
            Appointment.client_id,
            func.max(Appointment.appointment_date).label('last_date')
        )
        .filter(Appointment.professional_id == current_professional.id)
        .group_by(Appointment.client_id)
        .subquery()
    )

    # Query principal de clientes
    query = (
        db.query(
            User.id,
            User.full_name,
            User.email,
            User.phone,
            User.created_at,
            func.count(distinct(Appointment.id)).label('total_appointments'),
            last_appointment_subq.c.last_date.label('last_appointment_date'),
            func.sum(
                func.cast(Appointment.status == AppointmentStatus.NO_SHOW, Integer)
            ).label('no_shows')
        )
        .join(Appointment, User.id == Appointment.client_id)
        .outerjoin(last_appointment_subq, User.id == last_appointment_subq.c.client_id)
        .filter(Appointment.professional_id == current_professional.id)
        .filter(User.role == UserRole.CLIENT)
        .group_by(User.id, last_appointment_subq.c.last_date)
    )

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern)) |
            (User.phone.ilike(search_pattern))
        )

    # Execute query
    results = query.offset(skip).limit(limit).all()

    # Transform to response format
    clients = []
    for row in results:
        no_shows = row.no_shows or 0
        total = row.total_appointments
        no_show_rate = round((no_shows / total * 100), 1) if total > 0 else 0.0

        # Determine status based on activity
        if status == "vip":
            # For now, VIP is based on number of appointments
            if total < 10:
                continue
        elif status == "inactive":
            # Inactive if last appointment was more than 3 months ago
            from datetime import datetime, timedelta
            if row.last_appointment_date:
                last_date = row.last_appointment_date
                if (datetime.now().date() - last_date).days <= 90:
                    continue
            else:
                continue

        client_status = "vip" if total >= 10 else "active"

        clients.append(ClientResponse(
            id=row.id,
            full_name=row.full_name,
            email=row.email,
            phone=row.phone,
            total_appointments=total,
            last_appointment_date=row.last_appointment_date,
            status=client_status,
            no_show_rate=no_show_rate,
            created_at=row.created_at
        ))

    return clients


@router.get("/clients/{client_id}/stats", response_model=ClientStats)
async def get_client_stats(
    client_id: int,
    db: Session = Depends(get_db),
    current_professional: Professional = Depends(get_current_professional)
):
    """Obtener estadísticas detalladas de un cliente"""

    # Verify client exists
    client = db.query(User).filter(User.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Get appointment stats
    appointments = db.query(Appointment).filter(
        Appointment.professional_id == current_professional.id,
        Appointment.client_id == client_id
    ).all()

    if not appointments:
        return ClientStats(
            total_appointments=0,
            completed=0,
            cancelled=0,
            no_show=0,
            no_show_rate=0.0,
            average_rating=None
        )

    total = len(appointments)
    completed = sum(1 for a in appointments if a.status == AppointmentStatus.COMPLETED)
    cancelled = sum(1 for a in appointments if a.status == AppointmentStatus.CANCELLED)
    no_show = sum(1 for a in appointments if a.status == AppointmentStatus.NO_SHOW)
    no_show_rate = round((no_show / total * 100), 1) if total > 0 else 0.0

    return ClientStats(
        total_appointments=total,
        completed=completed,
        cancelled=cancelled,
        no_show=no_show,
        no_show_rate=no_show_rate,
        average_rating=None  # TODO: Implement ratings system
    )


# ========== USER ENDPOINTS ==========

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de usuarios (solo admin)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# IMPORTANT: This route must be AFTER all other specific routes like /clients
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un usuario específico"""
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar usuario"""
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = update_user(db, user_id, user_update)
    return user


# ========== PROFESSIONAL ENDPOINTS ==========

@router.post("/professional", response_model=ProfessionalResponse)
async def create_professional_profile(
    professional_data: ProfessionalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear perfil de profesional"""
    # Verificar que el usuario no tenga ya un perfil de profesional
    existing = get_professional_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Professional profile already exists"
        )
    
    professional_data.user_id = current_user.id
    professional = create_professional(db, professional_data)
    
    # Actualizar rol del usuario
    current_user.role = UserRole.PROFESSIONAL
    db.commit()
    
    return professional


@router.get("/professional/me", response_model=ProfessionalResponse)
async def get_my_professional_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener mi perfil de profesional"""
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    return professional


@router.put("/professional/{professional_id}", response_model=ProfessionalResponse)
async def update_professional_profile(
    professional_id: int,
    professional_update: ProfessionalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar perfil de profesional"""
    professional = get_professional_by_id(db, professional_id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    
    if professional.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated = update_professional(db, professional_id, professional_update)
    return updated
