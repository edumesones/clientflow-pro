from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.schemas.schemas import AvailabilitySlotResponse, AvailabilitySlotCreate, AvailabilitySchedule
from app.services.professional_service import (
    get_availability_slots,
    set_availability_schedule,
    delete_availability_slot,
    get_professional_by_user_id
)
from app.services.appointment_service import get_available_slots
from app.models.models import User, UserRole

router = APIRouter()

@router.get("/slots", response_model=List[AvailabilitySlotResponse])
async def get_my_availability(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener mis horarios de disponibilidad"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can manage availability"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    
    slots = get_availability_slots(db, professional.id)
    return slots

@router.post("/schedule")
async def set_schedule(
    schedule: AvailabilitySchedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Establecer horario de disponibilidad"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can manage availability"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    
    set_availability_schedule(db, professional.id, schedule.slots)
    return {"message": "Schedule updated successfully"}

@router.delete("/slots/{slot_id}")
async def delete_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar slot de disponibilidad"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can manage availability"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    
    delete_availability_slot(db, slot_id, professional.id)
    return {"message": "Slot deleted successfully"}

@router.get("/{professional_id}/available")
async def get_available_times(
    professional_id: int,
    date: date,
    db: Session = Depends(get_db)
):
    """Obtener horarios disponibles para una fecha (público)"""
    slots = get_available_slots(db, professional_id, date)
    return {"date": date, "available_slots": slots}
