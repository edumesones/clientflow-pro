from sqlalchemy.orm import Session
from app.models.models import Professional, AvailabilitySlot
from app.schemas.schemas import ProfessionalCreate, ProfessionalUpdate, AvailabilitySlotCreate
from fastapi import HTTPException, status
from slugify import slugify

def get_professional_by_slug(db: Session, slug: str):
    return db.query(Professional).filter(Professional.slug == slug).first()

def get_professional_by_user_id(db: Session, user_id: int):
    return db.query(Professional).filter(Professional.user_id == user_id).first()

def get_professional_by_id(db: Session, professional_id: int):
    return db.query(Professional).filter(Professional.id == professional_id).first()

def create_professional(db: Session, professional: ProfessionalCreate):
    # Generar slug si no se proporciona
    slug = professional.slug
    if not slug:
        base_slug = slugify(professional.bio[:50] if professional.bio else f"pro-{professional.user_id}")
        slug = base_slug
        counter = 1
        while get_professional_by_slug(db, slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
    
    db_professional = Professional(
        user_id=professional.user_id,
        slug=slug,
        bio=professional.bio,
        specialty=professional.specialty,
        timezone=professional.timezone,
        appointment_duration=professional.appointment_duration,
        buffer_time=professional.buffer_time,
        advance_booking_days=professional.advance_booking_days,
        is_accepting_appointments=professional.is_accepting_appointments
    )
    db.add(db_professional)
    db.commit()
    db.refresh(db_professional)
    return db_professional

def update_professional(db: Session, professional_id: int, professional_update: ProfessionalUpdate):
    db_professional = get_professional_by_id(db, professional_id)
    if not db_professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    
    update_data = professional_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_professional, field, value)
    
    db.commit()
    db.refresh(db_professional)
    return db_professional

def get_professionals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Professional).offset(skip).limit(limit).all()

# Availability Slots

def create_availability_slot(db: Session, slot: AvailabilitySlotCreate):
    db_slot = AvailabilitySlot(**slot.dict())
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

def get_availability_slots(db: Session, professional_id: int):
    return db.query(AvailabilitySlot).filter(
        AvailabilitySlot.professional_id == professional_id,
        AvailabilitySlot.is_active == True
    ).all()

def delete_availability_slot(db: Session, slot_id: int, professional_id: int):
    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.id == slot_id,
        AvailabilitySlot.professional_id == professional_id
    ).first()
    if slot:
        slot.is_active = False
        db.commit()
    return slot

def set_availability_schedule(db: Session, professional_id: int, slots: list):
    # Desactivar slots existentes
    db.query(AvailabilitySlot).filter(
        AvailabilitySlot.professional_id == professional_id
    ).update({"is_active": False})
    
    # Crear nuevos slots
    for slot_data in slots:
        slot = AvailabilitySlot(
            professional_id=professional_id,
            day_of_week=slot_data.day_of_week,
            start_time=slot_data.start_time,
            end_time=slot_data.end_time,
            is_active=True
        )
        db.add(slot)
    
    db.commit()
