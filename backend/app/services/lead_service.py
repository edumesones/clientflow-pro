from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.models import Lead, LeadStatus, Appointment
from app.schemas.schemas import LeadCreate, LeadUpdate
from app.core.config import settings
from fastapi import HTTPException, status

def get_lead_by_id(db: Session, lead_id: int):
    return db.query(Lead).filter(Lead.id == lead_id).first()

def get_leads_by_professional(
    db: Session, 
    professional_id: int,
    status: Optional[LeadStatus] = None,
    skip: int = 0, 
    limit: int = 100
):
    query = db.query(Lead).filter(Lead.professional_id == professional_id)
    
    if status:
        query = query.filter(Lead.status == status)
    
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()

def get_recent_leads(db: Session, professional_id: int, limit: int = 10):
    return db.query(Lead).filter(
        Lead.professional_id == professional_id
    ).order_by(Lead.created_at.desc()).limit(limit).all()

def create_lead(db: Session, lead: LeadCreate):
    db_lead = Lead(
        professional_id=lead.professional_id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        source=lead.source or "web",
        message=lead.message,
        status=LeadStatus.NEW,
        first_contact_date=datetime.utcnow()
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def update_lead(db: Session, lead_id: int, lead_update: LeadUpdate):
    db_lead = get_lead_by_id(db, lead_id)
    if not db_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    update_data = lead_update.dict(exclude_unset=True)
    
    # Si se marca como convertido, actualizar last_contact_date
    if "status" in update_data and update_data["status"] == LeadStatus.CONVERTED:
        update_data["last_contact_date"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_lead, field, value)
    
    db.commit()
    db.refresh(db_lead)
    return db_lead

def mark_lead_contacted(db: Session, lead_id: int):
    return update_lead(db, lead_id, LeadUpdate(
        status=LeadStatus.CONTACTED,
        last_contact_date=datetime.utcnow()
    ))

def get_leads_for_follow_up(db: Session, days: int) -> List[Lead]:
    """Obtener leads que necesitan follow-up"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    if days == 1:
        return db.query(Lead).filter(
            Lead.status == LeadStatus.NEW,
            Lead.created_at <= cutoff_date,
            Lead.follow_up_1_sent == False
        ).all()
    elif days == 3:
        return db.query(Lead).filter(
            Lead.status == LeadStatus.CONTACTED,
            Lead.first_contact_date <= cutoff_date,
            Lead.follow_up_3_sent == False
        ).all()
    elif days == 7:
        return db.query(Lead).filter(
            Lead.status.in_([LeadStatus.NEW, LeadStatus.CONTACTED]),
            Lead.created_at <= cutoff_date,
            Lead.follow_up_7_sent == False
        ).all()
    
    return []

def get_lead_stats(db: Session, professional_id: int):
    """Obtener estadísticas de leads"""
    total = db.query(Lead).filter(Lead.professional_id == professional_id).count()
    converted = db.query(Lead).filter(
        Lead.professional_id == professional_id,
        Lead.status == LeadStatus.CONVERTED
    ).count()
    new_leads = db.query(Lead).filter(
        Lead.professional_id == professional_id,
        Lead.status == LeadStatus.NEW
    ).count()
    
    conversion_rate = (converted / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "converted": converted,
        "new": new_leads,
        "conversion_rate": round(conversion_rate, 2)
    }
