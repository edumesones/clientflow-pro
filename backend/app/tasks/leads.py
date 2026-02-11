from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Lead, LeadStatus
from integrations.email.email_service import email_service
from integrations.whatsapp.whatsapp_service import whatsapp_service

@shared_task
def send_lead_follow_up(lead_id: int, day: int):
    """Enviar seguimiento a un lead específico"""
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead or lead.status == LeadStatus.CONVERTED or lead.status == LeadStatus.LOST:
            return
        
        professional = lead.professional
        
        # Enviar email
        if lead.email:
            email_service.send_lead_follow_up(
                to_email=lead.email,
                lead_name=lead.name,
                professional_name=professional.user.full_name,
                day=day
            )
        
        # Enviar WhatsApp
        if lead.phone:
            whatsapp_service.send_lead_follow_up(
                to_phone=lead.phone,
                lead_name=lead.name,
                professional_name=professional.user.full_name,
                day=day
            )
        
        # Actualizar flags
        if day == 1:
            lead.follow_up_1_sent = True
            lead.follow_up_1_date = datetime.utcnow()
            lead.status = LeadStatus.CONTACTED
        elif day == 3:
            lead.follow_up_3_sent = True
            lead.follow_up_3_date = datetime.utcnow()
            lead.status = LeadStatus.FOLLOWED_UP
        elif day == 7:
            lead.follow_up_7_sent = True
            lead.follow_up_7_date = datetime.utcnow()
        
        lead.last_contact_date = datetime.utcnow()
        db.commit()
        
    finally:
        db.close()

@shared_task
def process_follow_ups():
    """Procesar seguimientos automáticos de leads"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Día 1: Leads nuevos
        day_1_leads = db.query(Lead).filter(
            Lead.status == LeadStatus.NEW,
            Lead.created_at <= now - timedelta(days=1),
            Lead.follow_up_1_sent == False
        ).all()
        
        for lead in day_1_leads:
            send_lead_follow_up.delay(lead.id, 1)
        
        # Día 3: Leads contactados
        day_3_leads = db.query(Lead).filter(
            Lead.status == LeadStatus.CONTACTED,
            Lead.first_contact_date <= now - timedelta(days=3),
            Lead.follow_up_3_sent == False
        ).all()
        
        for lead in day_3_leads:
            send_lead_follow_up.delay(lead.id, 3)
        
        # Día 7: Último seguimiento
        day_7_leads = db.query(Lead).filter(
            Lead.status.in_([LeadStatus.NEW, LeadStatus.CONTACTED, LeadStatus.FOLLOWED_UP]),
            Lead.created_at <= now - timedelta(days=7),
            Lead.follow_up_7_sent == False
        ).all()
        
        for lead in day_7_leads:
            send_lead_follow_up.delay(lead.id, 7)
        
        return f"Scheduled follow-ups: {len(day_1_leads)} day-1, {len(day_3_leads)} day-3, {len(day_7_leads)} day-7"
        
    finally:
        db.close()
