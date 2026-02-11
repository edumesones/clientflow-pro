from datetime import datetime, date
from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.models import Appointment, AppointmentStatus, Lead, LeadStatus, StatsDaily

@shared_task
def update_daily_stats():
    """Actualizar estadísticas diarias"""
    db = SessionLocal()
    try:
        today = date.today()
        
        # Obtener profesionales activos
        professionals = db.query(Appointment.professional_id).distinct().all()
        
        for (professional_id,) in professionals:
            # Calcular estadísticas del día
            new_leads = db.query(Lead).filter(
                Lead.professional_id == professional_id,
                func.date(Lead.created_at) == today
            ).count()
            
            converted_leads = db.query(Lead).filter(
                Lead.professional_id == professional_id,
                Lead.status == LeadStatus.CONVERTED,
                func.date(Lead.updated_at) == today
            ).count()
            
            appointments_booked = db.query(Appointment).filter(
                Appointment.professional_id == professional_id,
                func.date(Appointment.created_at) == today
            ).count()
            
            appointments_completed = db.query(Appointment).filter(
                Appointment.professional_id == professional_id,
                Appointment.status == AppointmentStatus.COMPLETED,
                Appointment.appointment_date == today
            ).count()
            
            appointments_cancelled = db.query(Appointment).filter(
                Appointment.professional_id == professional_id,
                Appointment.status == AppointmentStatus.CANCELLED,
                func.date(Appointment.updated_at) == today
            ).count()
            
            no_shows = db.query(Appointment).filter(
                Appointment.professional_id == professional_id,
                Appointment.status == AppointmentStatus.NO_SHOW,
                Appointment.appointment_date == today
            ).count()
            
            revenue = db.query(func.sum(Appointment.price)).filter(
                Appointment.professional_id == professional_id,
                Appointment.status == AppointmentStatus.COMPLETED,
                Appointment.appointment_date == today
            ).scalar() or 0
            
            # Crear o actualizar registro de estadísticas
            stats = db.query(StatsDaily).filter(
                StatsDaily.professional_id == professional_id,
                StatsDaily.date == today
            ).first()
            
            if stats:
                stats.new_leads = new_leads
                stats.converted_leads = converted_leads
                stats.appointments_booked = appointments_booked
                stats.appointments_completed = appointments_completed
                stats.appointments_cancelled = appointments_cancelled
                stats.no_shows = no_shows
                stats.revenue = revenue
            else:
                stats = StatsDaily(
                    professional_id=professional_id,
                    date=today,
                    new_leads=new_leads,
                    converted_leads=converted_leads,
                    appointments_booked=appointments_booked,
                    appointments_completed=appointments_completed,
                    appointments_cancelled=appointments_cancelled,
                    no_shows=no_shows,
                    revenue=revenue
                )
                db.add(stats)
            
            db.commit()
        
        return f"Updated stats for {len(professionals)} professionals"
        
    finally:
        db.close()
