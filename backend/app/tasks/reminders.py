from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Appointment, AppointmentStatus, Reminder, ReminderStatus
from app.services.appointment_service import get_appointment_by_id
from integrations.email.email_service import email_service
from integrations.whatsapp.whatsapp_service import whatsapp_service
from integrations.sms.sms_service import sms_service

@shared_task
def send_reminder(reminder_id: int):
    """Enviar un recordatorio específico"""
    db = SessionLocal()
    try:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder or reminder.status != ReminderStatus.SCHEDULED:
            return
        
        appointment = reminder.appointment
        professional = appointment.professional
        
        # Determinar destinatario
        client_name = appointment.client.full_name if appointment.client else appointment.lead_name
        client_email = appointment.client.email if appointment.client else appointment.lead_email
        client_phone = appointment.client.phone if appointment.client else appointment.lead_phone
        
        if not client_name:
            client_name = "Cliente"
        
        # Enviar según el canal
        success = False
        
        if reminder.channel == "email" and client_email:
            success = email_service.send_appointment_reminder(
                to_email=client_email,
                client_name=client_name,
                professional_name=professional.user.full_name,
                appointment_date=appointment.appointment_date.strftime("%d/%m/%Y"),
                appointment_time=appointment.start_time.strftime("%H:%M"),
                hours_before=24 if reminder.reminder_type == "24h" else 1
            )
        elif reminder.channel == "whatsapp" and client_phone:
            success = whatsapp_service.send_appointment_reminder(
                to_phone=client_phone,
                client_name=client_name,
                professional_name=professional.user.full_name,
                appointment_date=appointment.appointment_date.strftime("%d/%m/%Y"),
                appointment_time=appointment.start_time.strftime("%H:%M"),
                hours_before=24 if reminder.reminder_type == "24h" else 1
            )
        elif reminder.channel == "sms" and client_phone:
            success = sms_service.send_appointment_reminder(
                to_number=client_phone,
                client_name=client_name,
                professional_name=professional.user.full_name,
                appointment_date=appointment.appointment_date.strftime("%d/%m/%Y"),
                appointment_time=appointment.start_time.strftime("%H:%M"),
                hours_before=24 if reminder.reminder_type == "24h" else 1
            )
        
        # Actualizar estado
        reminder.status = ReminderStatus.SENT if success else ReminderStatus.FAILED
        reminder.sent_at = datetime.utcnow()
        db.commit()
        
        # Actualizar flags de la cita
        if reminder.reminder_type == "24h":
            appointment.reminder_24h_sent = True
        elif reminder.reminder_type == "1h":
            appointment.reminder_1h_sent = True
        db.commit()
        
    finally:
        db.close()

@shared_task
def check_and_send_reminders():
    """Verificar y enviar recordatorios programados"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Buscar recordatorios que deban enviarse
        reminders = db.query(Reminder).filter(
            Reminder.status == ReminderStatus.SCHEDULED,
            Reminder.scheduled_at <= now
        ).all()
        
        for reminder in reminders:
            send_reminder.delay(reminder.id)
        
        return f"Scheduled {len(reminders)} reminders"
    finally:
        db.close()

@shared_task
def schedule_appointment_reminders(appointment_id: int):
    """Programar recordatorios para una cita nueva"""
    db = SessionLocal()
    try:
        appointment = get_appointment_by_id(db, appointment_id)
        if not appointment:
            return
        
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.start_time
        )
        
        # Recordatorio 24h antes
        reminder_24h_time = appointment_datetime - timedelta(hours=24)
        if reminder_24h_time > datetime.now():
            for channel in ["email", "whatsapp", "sms"]:
                reminder = Reminder(
                    appointment_id=appointment_id,
                    reminder_type="24h",
                    channel=channel,
                    scheduled_at=reminder_24h_time,
                    status=ReminderStatus.SCHEDULED
                )
                db.add(reminder)
        
        # Recordatorio 1h antes
        reminder_1h_time = appointment_datetime - timedelta(hours=1)
        if reminder_1h_time > datetime.now():
            for channel in ["email", "whatsapp", "sms"]:
                reminder = Reminder(
                    appointment_id=appointment_id,
                    reminder_type="1h",
                    channel=channel,
                    scheduled_at=reminder_1h_time,
                    status=ReminderStatus.SCHEDULED
                )
                db.add(reminder)
        
        db.commit()
        
    finally:
        db.close()

@shared_task
def send_post_appointment_review_request(appointment_id: int):
    """Enviar solicitud de review después de la cita"""
    db = SessionLocal()
    try:
        appointment = get_appointment_by_id(db, appointment_id)
        if not appointment or appointment.review_requested:
            return
        
        client_email = appointment.client.email if appointment.client else appointment.lead_email
        client_name = appointment.client.full_name if appointment.client else appointment.lead_name
        professional = appointment.professional
        
        if client_email:
            email_service.send_review_request(
                to_email=client_email,
                client_name=client_name or "Cliente",
                professional_name=professional.user.full_name
            )
        
        appointment.review_requested = True
        db.commit()
        
    finally:
        db.close()
