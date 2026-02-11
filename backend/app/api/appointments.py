from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.schemas.schemas import (
    AppointmentCreate, 
    AppointmentResponse, 
    AppointmentUpdate,
    AppointmentStatus
)
from app.services.appointment_service import (
    create_appointment,
    get_appointment_by_id,
    get_appointments_by_professional,
    get_upcoming_appointments,
    update_appointment,
    cancel_appointment
)
from app.services.professional_service import get_professional_by_user_id
from app.models.models import User, UserRole

router = APIRouter()

@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    professional_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[AppointmentStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar citas"""
    if current_user.role == UserRole.PROFESSIONAL:
        prof = get_professional_by_user_id(db, current_user.id)
        if prof:
            professional_id = prof.id
    
    if not professional_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    appointments = get_appointments_by_professional(
        db, professional_id, start_date, end_date, status
    )
    return appointments

@router.get("/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener próximas citas"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can access this endpoint"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    
    appointments = get_upcoming_appointments(db, professional.id, limit)
    return appointments

@router.post("/", response_model=AppointmentResponse)
async def create_appointment_endpoint(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nueva cita"""
    # Si el usuario es profesional, usar su propio ID
    if current_user.role == UserRole.PROFESSIONAL and not appointment_data.professional_id:
        prof = get_professional_by_user_id(db, current_user.id)
        if prof:
            appointment_data.professional_id = prof.id
    
    appointment = create_appointment(db, appointment_data)
    return appointment

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener detalle de una cita"""
    appointment = get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.PROFESSIONAL:
        prof = get_professional_by_user_id(db, current_user.id)
        if prof and appointment.professional_id != prof.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    elif current_user.role == UserRole.CLIENT:
        if appointment.client_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return appointment

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment_endpoint(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar cita"""
    appointment = get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.PROFESSIONAL:
        prof = get_professional_by_user_id(db, current_user.id)
        if prof and appointment.professional_id != prof.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    updated = update_appointment(db, appointment_id, appointment_update)
    return updated

@router.post("/{appointment_id}/cancel")
async def cancel_appointment_endpoint(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancelar cita"""
    appointment = get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.PROFESSIONAL:
        prof = get_professional_by_user_id(db, current_user.id)
        if prof and appointment.professional_id != prof.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    elif current_user.role == UserRole.CLIENT:
        if appointment.client_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    cancel_appointment(db, appointment_id)
    return {"message": "Appointment cancelled successfully"}
