from app.core.config import settings

class SMSService:
    """Servicio de SMS usando Twilio (placeholder para implementación real)"""
    
    def __init__(self):
        self.provider = settings.SMS_PROVIDER
        self.api_key = settings.SMS_API_KEY
        self.api_secret = settings.SMS_API_SECRET
        self.from_number = settings.SMS_FROM_NUMBER
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """Enviar SMS (placeholder)"""
        if not settings.ENABLE_SMS or not self.api_key:
            print(f"[SMS DISABLED] Would send to {to_number}: {message[:50]}...")
            return True
        
        # Aquí iría la implementación real usando Twilio:
        # from twilio.rest import Client
        # client = Client(self.api_key, self.api_secret)
        # message = client.messages.create(
        #     body=message,
        #     from_=self.from_number,
        #     to=to_number
        # )
        
        print(f"[SMS SENT] to {to_number}: {message[:50]}...")
        return True
    
    def send_appointment_confirmation(
        self,
        to_number: str,
        client_name: str,
        professional_name: str,
        appointment_date: str,
        appointment_time: str
    ):
        message = f"ClientFlow Pro: Hola {client_name}, tu cita con {professional_name} el {appointment_date} a las {appointment_time} ha sido confirmada."
        return self.send_sms(to_number, message)
    
    def send_appointment_reminder(
        self,
        to_number: str,
        client_name: str,
        professional_name: str,
        appointment_date: str,
        appointment_time: str,
        hours_before: int
    ):
        message = f"ClientFlow Pro: Recordatorio: Tu cita con {professional_name} es el {appointment_date} a las {appointment_time} (en {hours_before}h)."
        return self.send_sms(to_number, message)
    
    def send_short_reminder(
        self,
        to_number: str,
        professional_name: str,
        appointment_time: str
    ):
        """Recordatorio corto 1 hora antes"""
        message = f"Recordatorio: Tienes cita con {professional_name} a las {appointment_time}."
        return self.send_sms(to_number, message)

sms_service = SMSService()
