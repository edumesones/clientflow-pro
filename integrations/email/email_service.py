import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from jinja2 import Template
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_TLS
        self.from_name = settings.SMTP_FROM_NAME
        self.from_email = settings.SMTP_FROM_EMAIL

    def _get_smtp_connection(self):
        context = ssl.create_default_context()
        server = smtplib.SMTP(self.host, self.port)
        if self.use_tls:
            server.starttls(context=context)
        if self.user and self.password:
            server.login(self.user, self.password)
        return server

    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        if not settings.ENABLE_EMAIL:
            print(f"[EMAIL DISABLED] Would send to {to_email}: {subject}")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            with self._get_smtp_connection() as server:
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            print(f"[EMAIL SENT] to {to_email}: {subject}")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")
            return False

    def send_appointment_confirmation(
        self, 
        to_email: str, 
        client_name: str,
        professional_name: str,
        appointment_date: str,
        appointment_time: str,
        service_type: Optional[str] = None
    ):
        subject = f"Confirmación de tu cita con {professional_name}"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">¡Tu cita ha sido confirmada!</h2>
                
                <p>Hola {client_name},</p>
                
                <p>Tu cita con <strong>{professional_name}</strong> ha sido confirmada:</p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Fecha:</strong> {appointment_date}</p>
                    <p><strong>Hora:</strong> {appointment_time}</p>
                    {f'<p><strong>Servicio:</strong> {service_type}</p>' if service_type else ''}
                </div>
                
                <p>Recibirás recordatorios antes de tu cita.</p>
                
                <p style="color: #666; font-size: 12px;">
                    Este es un mensaje automático de ClientFlow Pro.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html)

    def send_appointment_reminder(
        self,
        to_email: str,
        client_name: str,
        professional_name: str,
        appointment_date: str,
        appointment_time: str,
        hours_before: int
    ):
        subject = f"Recordatorio: Tu cita es en {hours_before} horas"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #e74c3c;">⏰ Recordatorio de cita</h2>
                
                <p>Hola {client_name},</p>
                
                <p>Te recordamos que tienes una cita programada:</p>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <p><strong>Profesional:</strong> {professional_name}</p>
                    <p><strong>Fecha:</strong> {appointment_date}</p>
                    <p><strong>Hora:</strong> {appointment_time}</p>
                </div>
                
                <p>Si necesitas cancelar o reprogramar, por favor contáctanos lo antes posible.</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html)

    def send_lead_follow_up(
        self,
        to_email: str,
        lead_name: str,
        professional_name: str,
        day: int
    ):
        subject = f"{professional_name} - Siguiendo en contacto"
        
        messages = {
            1: "Gracias por tu interés. ¿Tienes alguna pregunta?",
            3: "Quería asegurarme de que recibiste mi información. ¿Hay algo en lo que pueda ayudarte?",
            7: "Último seguimiento: ¿Te gustaría agendar una llamada para conversar sobre tus necesidades?"
        }
        
        message = messages.get(day, "¿Cómo puedo ayudarte?")
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Hola {lead_name}</h2>
                
                <p>{message}</p>
                
                <p>Saludos,<br>{professional_name}</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html)

    def send_review_request(
        self,
        to_email: str,
        client_name: str,
        professional_name: str
    ):
        subject = f"¿Cómo fue tu experiencia con {professional_name}?"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Tu opinión es importante</h2>
                
                <p>Hola {client_name},</p>
                
                <p>Espero que hayas tenido una excelente experiencia. Tu feedback me ayuda a mejorar.</p>
                
                <p>¿Te tomarías un momento para dejarme una reseña?</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="#" style="background: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Dejar Reseña
                    </a>
                </div>
                
                <p>¡Gracias por tu confianza!</p>
                
                <p>{professional_name}</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html)

email_service = EmailService()
