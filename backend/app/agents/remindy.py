"""
Agente Remindy - Sistema Anti No-Show

Este agente:
1. Monitorea citas próximas (24h y 1h antes)
2. Envía recordatorios con solicitud de confirmación
3. Si no hay confirmación, ofrece reagendar automáticamente
4. Calcula score de riesgo de no-show por cliente
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.models import (
    Appointment, AppointmentStatus, AppointmentConfirmation, 
    ConfirmationStatus, NoShowPattern, User
)
from app.core.email import send_email
from app.agents.base import BaseAgent

class RemindyAgent(BaseAgent):
    """Agente que reduce no-shows mediante confirmaciones inteligentes"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def run(self) -> Dict[str, Any]:
        """Ejecuta el ciclo completo de anti no-show"""
        results = {
            "reminders_sent": 0,
            "confirmations_processed": 0,
            "rescheduled": 0,
            "errors": []
        }
        
        try:
            # 1. Enviar recordatorios 24h antes
            reminders_24h = self._send_24h_reminders()
            results["reminders_sent"] += reminders_24h
            
            # 2. Enviar recordatorios 1h antes
            reminders_1h = self._send_1h_reminders()
            results["reminders_sent"] += reminders_1h
            
            # 3. Procesar confirmaciones pendientes
            confirmations = self._process_pending_confirmations()
            results["confirmations_processed"] += confirmations
            
            # 4. Auto-reagendar citas no confirmadas
            rescheduled = self._auto_reschedule_unconfirmed()
            results["rescheduled"] += rescheduled
            
            # 5. Actualizar patrones de no-show
            self._update_noshow_patterns()
            
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    def _send_24h_reminders(self) -> int:
        """Envía recordatorios a 24 horas de la cita"""
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        # Buscar citas de mañana sin recordatorio 24h enviado
        appointments = self.db.query(Appointment).filter(
            and_(
                Appointment.appointment_date == tomorrow,
                Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]),
                Appointment.reminder_24h_sent == False
            )
        ).all()
        
        count = 0
        for appt in appointments:
            # Crear o actualizar registro de confirmación
            confirmation = self.db.query(AppointmentConfirmation).filter(
                AppointmentConfirmation.appointment_id == appt.id
            ).first()
            
            if not confirmation:
                confirmation = AppointmentConfirmation(
                    appointment_id=appt.id,
                    status=ConfirmationStatus.PENDING
                )
                self.db.add(confirmation)
            
            # Generar mensaje personalizado con IA
            message = self._generate_reminder_message(appt, "24h")
            
            # Enviar por email (y WhatsApp si está configurado)
            if appt.client and appt.client.email:
                send_email(
                    to_email=appt.client.email,
                    subject="⏰ Recordatorio de tu cita mañana - ¿Confirmas?",
                    body=message
                )
            
            # Maritar como enviado
            appt.reminder_24h_sent = True
            confirmation.reminder_24h_sent = datetime.now()
            count += 1
        
        self.db.commit()
        return count
    
    def _send_1h_reminders(self) -> int:
        """Envía recordatorios a 1 hora de la cita"""
        # Lógica similar para recordatorios 1h antes
        return 0  # TODO: Implementar
    
    def _process_pending_confirmations(self) -> int:
        """Procesa respuestas de confirmación pendientes"""
        # Verificar citas con confirmación pendiente por más de 12h
        cutoff = datetime.now() - timedelta(hours=12)
        
        pending = self.db.query(AppointmentConfirmation).filter(
            and_(
                AppointmentConfirmation.status == ConfirmationStatus.PENDING,
                AppointmentConfirmation.reminder_24h_sent < cutoff
            )
        ).all()
        
        count = 0
        for conf in pending:
            # Marcar como no respondido
            conf.status = ConfirmationStatus.NO_RESPONSE
            count += 1
        
        self.db.commit()
        return count
    
    def _auto_reschedule_unconfirmed(self) -> int:
        """Ofrece reagendar citas no confirmadas"""
        # Buscar citas sin confirmación 6h antes
        cutoff = datetime.now() - timedelta(hours=6)
        
        unconfirmed = self.db.query(AppointmentConfirmation).filter(
            and_(
                AppointmentConfirmation.status == ConfirmationStatus.NO_RESPONSE,
                AppointmentConfirmation.reminder_24h_sent < cutoff
            )
        ).all()
        
        count = 0
        for conf in unconfirmed:
            # Generar mensaje de reagendamiento
            appt = conf.appointment
            if appt:
                message = self._generate_reschedule_offer(appt)
                
                if appt.client and appt.client.email:
                    send_email(
                        to_email=appt.client.email,
                        subject="📅 ¿Reagendamos tu cita?",
                        body=message
                    )
                
                conf.auto_rescheduled = True
                count += 1
        
        self.db.commit()
        return count
    
    def _update_noshow_patterns(self):
        """Actualiza los patrones de no-show por cliente"""
        # Analizar citas completadas/no-show de los últimos 90 días
        cutoff = datetime.now() - timedelta(days=90)
        
        clients = self.db.query(User).filter(User.role == "client").all()
        
        for client in clients:
            total = self.db.query(Appointment).filter(
                and_(
                    Appointment.client_id == client.id,
                    Appointment.created_at >= cutoff
                )
            ).count()
            
            no_shows = self.db.query(Appointment).filter(
                and_(
                    Appointment.client_id == client.id,
                    Appointment.status == AppointmentStatus.NO_SHOW,
                    Appointment.created_at >= cutoff
                )
            ).count()
            
            # Calcular score de fiabilidad
            if total > 0:
                reliability = int(((total - no_shows) / total) * 100)
            else:
                reliability = 100
            
            # Guardar o actualizar patrón
            pattern = self.db.query(NoShowPattern).filter(
                NoShowPattern.client_id == client.id
            ).first()
            
            if not pattern:
                pattern = NoShowPattern(client_id=client.id)
                self.db.add(pattern)
            
            pattern.total_appointments = total
            pattern.no_shows = no_shows
            pattern.reliability_score = reliability
            pattern.last_updated = datetime.now()
        
        self.db.commit()
    
    def _generate_reminder_message(self, appointment, timing: str) -> str:
        """Genera mensaje de recordatorio personalizado"""
        professional = appointment.professional
        client = appointment.client
        
        prompt = f"""
        Genera un email de recordatorio de cita médica/profesional en español.
        
        Detalles:
        - Cliente: {client.full_name if client else 'Paciente'}
        - Profesional: {professional.user.full_name if professional else 'Especialista'}
        - Fecha: {appointment.appointment_date}
        - Hora: {appointment.start_time}
        - Servicio: {appointment.service_type or 'Consulta'}
        - Timing: {timing} antes
        
        El email debe:
        1. Ser amable y profesional
        2. Pedir confirmación (responder "CONFIRMAR")
        3. Incluir opción de cancelar/reagendar
        4. Ser breve (máximo 150 palabras)
        
        Formato: Email completo con asunto (pero sin incluir "Asunto:" explícito)
        """
        
        return self.generate_text(
            prompt=prompt,
            system_prompt="Eres un asistente de agenda médica/profesional. Genera emails cortos y amables.",
            temperature=0.7
        )
    
    def _generate_reschedule_offer(self, appointment) -> str:
        """Genera oferta de reagendamiento"""
        prompt = f"""
        Genera un email ofreciendo reagendar una cita que no fue confirmada.
        
        Detalles:
        - Fecha original: {appointment.appointment_date}
        - Servicio: {appointment.service_type or 'Consulta'}
        
        El email debe:
        1. Ser comprensivo (quizás el horario no funcionó)
        2. Ofrecer fácil reagendamiento
        3. Mantener tono profesional pero cercano
        4. Máximo 100 palabras
        """
        
        return self.generate_text(
            prompt=prompt,
            system_prompt="Eres un asistente de servicio al cliente amable.",
            temperature=0.8
        )
