from sqlalchemy.orm import Session
from datetime import datetime, date, time, timedelta
from typing import List, Optional
from app.models.models import Appointment, AppointmentStatus, User
from app.schemas.schemas import AppointmentCreate, AppointmentUpdate
from app.core.config import settings
from fastapi import HTTPException, status

def get_appointment_by_id(db: Session, appointment_id: int):
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()

def get_appointments_by_professional(
    db: Session, 
    professional_id: int, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[AppointmentStatus] = None
):
    query = db.query(Appointment).filter(Appointment.professional_id == professional_id)
    
    if start_date:
        query = query.filter(Appointment.appointment_date >= start_date)
    if end_date:
        query = query.filter(Appointment.appointment_date <= end_date)
    if status:
        query = query.filter(Appointment.status == status)
    
    return query.order_by(Appointment.appointment_date, Appointment.start_time).all()

def get_appointments_by_client(db: Session, client_id: int):
    return db.query(Appointment).filter(
        Appointment.client_id == client_id
    ).order_by(Appointment.appointment_date.desc()).all()

def get_upcoming_appointments(db: Session, professional_id: int, limit: int = 10):
    today = date.today()
    now = datetime.now().time()
    
    return db.query(Appointment).filter(
        Appointment.professional_id == professional_id,
        Appointment.appointment_date >= today,
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).order_by(Appointment.appointment_date, Appointment.start_time).limit(limit).all()

def create_appointment(db: Session, appointment: AppointmentCreate):
    # Calcular end_time basado en la duración del profesional
    from app.services.professional_service import get_professional_by_id
    professional = get_professional_by_id(db, appointment.professional_id)
    
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    
    # Calcular end_time
    start_datetime = datetime.combine(appointment.appointment_date, appointment.start_time)
    end_datetime = start_datetime + timedelta(minutes=professional.appointment_duration)
    end_time = end_datetime.time()
    
    # Verificar disponibilidad
    existing = db.query(Appointment).filter(
        Appointment.professional_id == appointment.professional_id,
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.start_time == appointment.start_time,
        Appointment.status.notin_([AppointmentStatus.CANCELLED])
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time slot not available"
        )
    
    db_appointment = Appointment(
        professional_id=appointment.professional_id,
        client_id=appointment.client_id,
        lead_name=appointment.lead_name,
        lead_email=appointment.lead_email,
        lead_phone=appointment.lead_phone,
        appointment_date=appointment.appointment_date,
        start_time=appointment.start_time,
        end_time=end_time,
        service_type=appointment.service_type,
        notes=appointment.notes,
        price=appointment.price,
        status=AppointmentStatus.CONFIRMED
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    # Si tiene email, crear usuario o vincular lead
    if appointment.lead_email and not appointment.client_id:
        # Buscar usuario existente
        user = db.query(User).filter(User.email == appointment.lead_email).first()
        if user:
            db_appointment.client_id = user.id
            db.commit()
    
    return db_appointment

def update_appointment(db: Session, appointment_id: int, appointment_update: AppointmentUpdate):
    db_appointment = get_appointment_by_id(db, appointment_id)
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    update_data = appointment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_appointment, field, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def cancel_appointment(db: Session, appointment_id: int):
    return update_appointment(db, appointment_id, AppointmentUpdate(status=AppointmentStatus.CANCELLED))

def get_available_slots(
    db: Session, 
    professional_id: int, 
    date: date,
    duration: int = 60
) -> List[time]:
    """Obtener slots disponibles para una fecha específica"""
    from app.models.models import AvailabilitySlot
    from app.services.professional_service import get_professional_by_id
    
    professional = get_professional_by_id(db, professional_id)
    if not professional or not professional.is_accepting_appointments:
        return []
    
    # Obtener día de la semana (0=Lunes)
    day_of_week = date.weekday()
    
    # Obtener slots de disponibilidad
    availability_slots = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.professional_id == professional_id,
        AvailabilitySlot.day_of_week == day_of_week,
        AvailabilitySlot.is_active == True
    ).all()
    
    if not availability_slots:
        return []
    
    # Obtener citas existentes para esa fecha
    existing_appointments = db.query(Appointment).filter(
        Appointment.professional_id == professional_id,
        Appointment.appointment_date == date,
        Appointment.status.notin_([AppointmentStatus.CANCELLED])
    ).all()
    
    occupied_times = set()
    for appt in existing_appointments:
        occupied_times.add(appt.start_time)
    
    # Generar slots disponibles
    available_slots = []
    slot_duration = timedelta(minutes=duration)
    
    for slot in availability_slots:
        current_time = datetime.combine(date, slot.start_time)
        end_time = datetime.combine(date, slot.end_time)
        
        while current_time + slot_duration <= end_time:
            time_obj = current_time.time()
            if time_obj not in occupied_times:
                available_slots.append(time_obj)
            current_time += slot_duration
    
    return sorted(available_slots)
