from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List

from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.schemas.schemas import DashboardData, DashboardStats, UpcomingAppointment, RecentLead
from app.services.professional_service import get_professional_by_user_id
from app.services.appointment_service import get_upcoming_appointments
from app.services.lead_service import get_recent_leads, get_lead_stats
from app.models.models import Appointment, AppointmentStatus, Lead, User, UserRole

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estadísticas del dashboard"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can access dashboard"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    
    today = date.today()
    first_day_this_month = today.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    
    # Contar leads
    total_leads = db.query(Lead).filter(Lead.professional_id == professional.id).count()
    new_leads_today = db.query(Lead).filter(
        Lead.professional_id == professional.id,
        Lead.created_at >= datetime.combine(today, datetime.min.time())
    ).count()
    
    # Contar citas
    total_appointments = db.query(Appointment).filter(
        Appointment.professional_id == professional.id
    ).count()
    
    upcoming_appointments = db.query(Appointment).filter(
        Appointment.professional_id == professional.id,
        Appointment.appointment_date >= today,
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).count()
    
    # Calcular tasas
    converted_leads = db.query(Lead).filter(
        Lead.professional_id == professional.id,
        Lead.status == "converted"
    ).count()
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    
    no_shows = db.query(Appointment).filter(
        Appointment.professional_id == professional.id,
        Appointment.status == AppointmentStatus.NO_SHOW
    ).count()
    completed = db.query(Appointment).filter(
        Appointment.professional_id == professional.id,
        Appointment.status == AppointmentStatus.COMPLETED
    ).count()
    no_show_rate = (no_shows / (completed + no_shows) * 100) if (completed + no_shows) > 0 else 0
    
    # Ingresos
    revenue_this_month = db.query(Appointment).filter(
        Appointment.professional_id == professional.id,
        Appointment.appointment_date >= first_day_this_month,
        Appointment.status == AppointmentStatus.COMPLETED
    ).with_entities(Appointment.price).all()
    revenue_this_month = sum([r[0] or 0 for r in revenue_this_month])
    
    revenue_last_month = db.query(Appointment).filter(
        Appointment.professional_id == professional.id,
        Appointment.appointment_date >= first_day_last_month,
        Appointment.appointment_date < first_day_this_month,
        Appointment.status == AppointmentStatus.COMPLETED
    ).with_entities(Appointment.price).all()
    revenue_last_month = sum([r[0] or 0 for r in revenue_last_month])
    
    return DashboardStats(
        total_leads=total_leads,
        new_leads_today=new_leads_today,
        total_appointments=total_appointments,
        upcoming_appointments=upcoming_appointments,
        conversion_rate=round(conversion_rate, 2),
        no_show_rate=round(no_show_rate, 2),
        revenue_this_month=revenue_this_month,
        revenue_last_month=revenue_last_month
    )

@router.get("/upcoming-appointments", response_model=List[UpcomingAppointment])
async def get_dashboard_upcoming(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener próximas citas para el dashboard"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can access dashboard"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    
    appointments = get_upcoming_appointments(db, professional.id, limit)
    
    result = []
    for appt in appointments:
        client_name = appt.client.full_name if appt.client else (appt.lead_name or "Sin nombre")
        client_email = appt.client.email if appt.client else appt.lead_email
        client_phone = appt.client.phone if appt.client else appt.lead_phone
        
        result.append(UpcomingAppointment(
            id=appt.id,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            appointment_date=appt.appointment_date,
            start_time=appt.start_time,
            service_type=appt.service_type,
            status=appt.status.value
        ))
    
    return result

@router.get("/recent-leads", response_model=List[RecentLead])
async def get_dashboard_leads(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener leads recientes para el dashboard"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can access dashboard"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    
    leads = get_recent_leads(db, professional.id, limit)
    
    return [
        RecentLead(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            status=lead.status.value,
            created_at=lead.created_at
        ) for lead in leads
    ]

# Alias routes for frontend compatibility
@router.get("/upcoming", response_model=List[UpcomingAppointment])
async def get_dashboard_upcoming_alias(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Alias for /upcoming-appointments"""
    return await get_dashboard_upcoming(limit, db, current_user)

@router.get("/leads/recent", response_model=List[RecentLead])
async def get_dashboard_leads_alias(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Alias for /recent-leads"""
    return await get_dashboard_leads(limit, db, current_user)

@router.get("/data", response_model=DashboardData)
async def get_full_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener todos los datos del dashboard"""
    stats = await get_dashboard_stats(db, current_user)
    upcoming = await get_dashboard_upcoming(db=db, current_user=current_user)
    recent = await get_dashboard_leads(db=db, current_user=current_user)
    
    return DashboardData(
        stats=stats,
        upcoming_appointments=upcoming,
        recent_leads=recent
    )
