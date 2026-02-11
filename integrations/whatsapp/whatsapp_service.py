from app.core.config import settings

class WhatsAppService:
    """Servicio de WhatsApp Business API (placeholder para implementación real)"""
    
    def __init__(self):
        self.api_key = settings.WHATSAPP_API_KEY
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.business_account_id = settings.WHATSAPP_BUSINESS_ACCOUNT_ID
        self.api_version = settings.WHATSAPP_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    def _send_message(self, to_phone: str, message: str, template_name: str = None) -> bool:
        """Enviar mensaje de WhatsApp (placeholder)"""
        if not settings.ENABLE_WHATSAPP or not self.api_key:
            print(f"[WHATSAPP DISABLED] Would send to {to_phone}: {message[:50]}...")
            return True
        
        # Aquí iría la implementación real usando la API de WhatsApp Business
        # Ejemplo con requests:
        # url = f"{self.base_url}/{self.phone_number_id}/messages"
        # headers = {"Authorization": f"Bearer {self.api_key}"}
        # data = {...}
        # response = requests.post(url, headers=headers, json=data)
        
        print(f"[WHATSAPP SENT] to {to_phone}: {message[:50]}...")
        return True
    
    def send_appointment_confirmation(
        self,
        to_phone: str,
        client_name: str,
        professional_name: str,
        appointment_date: str,
        appointment_time: str
    ):
        message = f"""¡Hola {client_name}! ✅

Tu cita con {professional_name} ha sido confirmada:

📅 Fecha: {appointment_date}
🕐 Hora: {appointment_time}

Recibirás recordatorios antes de tu cita.

Gracias por tu preferencia!"""
        
        return self._send_message(to_phone, message)
    
    def send_appointment_reminder(
        self,
        to_phone: str,
        client_name: str,
        professional_name: str,
        appointment_date: str,
        appointment_time: str,
        hours_before: int
    ):
        message = f"""⏰ Recordatorio de cita

Hola {client_name},

Te recordamos que tu cita con {professional_name} es:

📅 {appointment_date} a las {appointment_time}

⏳ En {hours_before} horas

Si necesitas cancelar, por favor avísanos lo antes posible."""
        
        return self._send_message(to_phone, message)
    
    def send_lead_follow_up(
        self,
        to_phone: str,
        lead_name: str,
        professional_name: str,
        day: int
    ):
        messages = {
            1: f"Hola {lead_name}, gracias por tu interés. ¿Tienes alguna pregunta sobre nuestros servicios?",
            3: f"Hola {lead_name}, quería asegurarme de que recibiste mi información. ¿En qué puedo ayudarte?",
            7: f"Hola {lead_name}, ¿te gustaría agendar una llamada para conversar sobre tus necesidades?"
        }
        
        message = messages.get(day, f"Hola {lead_name}, ¿cómo puedo ayudarte?")
        message += f"\n\n- {professional_name}"
        
        return self._send_message(to_phone, message)
    
    def send_review_request(
        self,
        to_phone: str,
        client_name: str,
        professional_name: str
    ):
        message = f"""Hola {client_name},

Espero que hayas tenido una excelente experiencia. Tu opinión me ayuda a mejorar.

¿Te tomarías un momento para dejarme una reseña?

[Link de reseña]

¡Gracias por tu confianza!

{professional_name}"""
        
        return self._send_message(to_phone, message)

whatsapp_service = WhatsAppService()
