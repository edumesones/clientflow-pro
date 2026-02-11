from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.core.database import get_db
from app.schemas.schemas import (
    PublicProfessional, 
    AvailableSlot, 
    PublicBookingRequest, 
    PublicBookingResponse,
    LeadCreate,
    LeadResponse
)
from app.services.professional_service import get_professional_by_slug
from app.services.appointment_service import get_available_slots, create_appointment
from app.services.lead_service import create_lead
from app.models.models import LeadStatus

router = APIRouter()

@router.get("/professionals/{slug}", response_model=PublicProfessional)
async def get_public_professional(
    slug: str,
    db: Session = Depends(get_db)
):
    """Obtener información pública de un profesional"""
    professional = get_professional_by_slug(db, slug)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    
    if not professional.is_accepting_appointments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This professional is not accepting appointments"
        )
    
    return PublicProfessional(
        id=professional.id,
        slug=professional.slug,
        full_name=professional.user.full_name,
        bio=professional.bio,
        specialty=professional.specialty,
        appointment_duration=professional.appointment_duration
    )

@router.get("/professionals/{slug}/availability")
async def get_public_availability(
    slug: str,
    date: date,
    db: Session = Depends(get_db)
):
    """Obtener disponibilidad pública de un profesional"""
    professional = get_professional_by_slug(db, slug)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    
    slots = get_available_slots(db, professional.id, date)
    
    return {
        "professional_id": professional.id,
        "date": date,
        "available_slots": [s.isoformat() for s in slots]
    }

@router.post("/book", response_model=PublicBookingResponse)
async def public_booking(
    booking: PublicBookingRequest,
    db: Session = Depends(get_db)
):
    """Realizar una reserva pública"""
    professional = get_professional_by_slug(db, booking.professional_slug)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    
    if not professional.is_accepting_appointments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This professional is not accepting appointments"
        )
    
    # Verificar disponibilidad
    available = get_available_slots(db, professional.id, booking.appointment_date)
    if booking.start_time not in available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected time slot is not available"
        )
    
    # Crear cita
    from app.schemas.schemas import AppointmentCreate
    appointment_data = AppointmentCreate(
        professional_id=professional.id,
        appointment_date=booking.appointment_date,
        start_time=booking.start_time,
        lead_name=booking.name,
        lead_email=booking.email,
        lead_phone=booking.phone,
        service_type=booking.service_type,
        notes=booking.notes
    )
    
    try:
        appointment = create_appointment(db, appointment_data)
        
        # Crear lead si no existe
        lead_data = LeadCreate(
            name=booking.name,
            email=booking.email,
            phone=booking.phone,
            source="web_booking",
            message=booking.notes,
            professional_id=professional.id
        )
        create_lead(db, lead_data)
        
        return PublicBookingResponse(
            success=True,
            message="Appointment booked successfully!",
            appointment_id=appointment.id
        )
    except Exception as e:
        return PublicBookingResponse(
            success=False,
            message=f"Error booking appointment: {str(e)}"
        )

@router.post("/leads", response_model=LeadResponse)
async def public_lead_form(
    lead_data: LeadCreate,
    db: Session = Depends(get_db)
):
    """Enviar formulario de contacto (lead)"""
    lead = create_lead(db, lead_data)
    return lead
