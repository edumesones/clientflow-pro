"""
Módulo de envío de emails para ClientFlow Pro
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    from_name: Optional[str] = None,
    from_email: Optional[str] = None
) -> bool:
    """
    Envía un email usando SMTP
    
    Args:
        to_email: Email del destinatario
        subject: Asunto del email
        html_content: Contenido HTML del email
        text_content: Contenido de texto plano (opcional)
        from_name: Nombre del remitente (opcional)
        from_email: Email del remitente (opcional)
    
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    # Si el email está deshabilitado, solo loggear
    if not settings.ENABLE_EMAIL:
        logger.info(f"[EMAIL DISABLED] Would send to {to_email}: {subject}")
        return True
    
    # Si no hay configuración SMTP, loggear warning
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning(f"[SMTP NOT CONFIGURED] Cannot send email to {to_email}: {subject}")
        return False
    
    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name or settings.SMTP_FROM_NAME} <{from_email or settings.SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        
        # Agregar contenido de texto plano si existe
        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)
        
        # Agregar contenido HTML
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        # Conectar y enviar
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def send_appointment_reminder(
    to_email: str,
    client_name: str,
    professional_name: str,
    service_name: str,
    appointment_date: str,
    appointment_time: str,
    confirmation_link: Optional[str] = None,
    reschedule_link: Optional[str] = None
) -> bool:
    """
    Envía un recordatorio de cita al cliente
    """
    subject = f"Recordatorio de cita - {service_name}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4F46E5;">¡Hola {client_name}!</h2>
            <p>Te recordamos que tienes una cita programada:</p>
            
            <div style="background: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Servicio:</strong> {service_name}</p>
                <p style="margin: 5px 0;"><strong>Profesional:</strong> {professional_name}</p>
                <p style="margin: 5px 0;"><strong>Fecha:</strong> {appointment_date}</p>
                <p style="margin: 5px 0;"><strong>Hora:</strong> {appointment_time}</p>
            </div>
            
            <p>Por favor confirma tu asistencia para que podamos preparar todo para ti.</p>
            
            <div style="margin: 30px 0; text-align: center;">
                {f'<a href="{confirmation_link}" style="background: #10B981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 5px;">Confirmar asistencia</a>' if confirmation_link else ''}
                {f'<a href="{reschedule_link}" style="background: #6B7280; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 5px;">Reagendar</a>' if reschedule_link else ''}
            </div>
            
            <p style="color: #6B7280; font-size: 14px; margin-top: 30px;">
                Si tienes alguna pregunta, no dudes en contactarnos.<br>
                Gracias por confiar en nosotros.
            </p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Hola {client_name},
    
    Te recordamos que tienes una cita programada:
    
    Servicio: {service_name}
    Profesional: {professional_name}
    Fecha: {appointment_date}
    Hora: {appointment_time}
    
    Por favor confirma tu asistencia.
    
    Gracias!
    """
    
    return send_email(to_email, subject, html_content, text_content)


def send_welcome_email(to_email: str, name: str) -> bool:
    """
    Envía email de bienvenida a nuevos usuarios
    """
    subject = "¡Bienvenido a ClientFlow Pro!"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4F46E5;">¡Bienvenido {name}!</h2>
            <p>Gracias por unirte a ClientFlow Pro. Estamos emocionados de ayudarte a gestionar tus citas de manera más eficiente.</p>
            <p>Con ClientFlow Pro podrás:</p>
            <ul>
                <li>Gestionar citas fácilmente</li>
                <li>Reducir no-shows con recordatorios automáticos</li>
                <li>Organizar tu agenda de forma inteligente</li>
            </ul>
            <p style="margin-top: 30px;">
                <a href="#" style="background: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px;">
                    Comenzar ahora
                </a>
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_content)
