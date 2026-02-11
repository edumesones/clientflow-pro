"""
Agente Brief - Inteligencia Pre-Cita

Este agente:
1. Analiza todo el historial del cliente antes de la cita
2. Genera un briefing ejecutivo para el profesional
3. Identifica temas pendientes y sugerencias de preparación
4. Aprende patrones del cliente para futuras citas
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.models import (
    Appointment, AppointmentBrief, BriefStatus, ClientInsight,
    AppointmentStatus, ClientNote, Lead, User
)
from app.agents.base import BaseAgent
import json

class BriefAgent(BaseAgent):
    """Agente que genera inteligencia pre-cita para profesionales"""
    
    # Tiempo antes de la cita para generar brief (30 minutos)
    BRIEF_GENERATION_WINDOW = timedelta(minutes=30)
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def run(self) -> Dict[str, Any]:
        """Ejecuta el ciclo de generación de briefs"""
        results = {
            "briefs_generated": 0,
            "insights_updated": 0,
            "errors": []
        }
        
        try:
            # 1. Generar briefs para citas próximas
            briefs = self._generate_pending_briefs()
            results["briefs_generated"] = briefs
            
            # 2. Actualizar insights de clientes
            insights = self._update_client_insights()
            results["insights_updated"] = insights
            
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    def generate_brief_for_appointment(self, appointment_id: int) -> Optional[AppointmentBrief]:
        """Genera un brief específico para una cita"""
        try:
            appointment = self.db.query(Appointment).filter(
                Appointment.id == appointment_id
            ).first()
            
            if not appointment:
                return None
            
            client = appointment.client
            professional = appointment.professional
            
            if not client or not professional:
                return None
            
            # Recopilar datos del cliente
            client_data = self._gather_client_data(client.id, professional.id)
            
            # Generar contenido con IA
            brief_content = self._generate_brief_content(appointment, client_data)
            
            # Crear o actualizar brief
            brief = self.db.query(AppointmentBrief).filter(
                AppointmentBrief.appointment_id == appointment_id
            ).first()
            
            if not brief:
                brief = AppointmentBrief(
                    appointment_id=appointment_id,
                    professional_id=professional.id,
                    client_id=client.id
                )
                self.db.add(brief)
            
            # Actualizar campos
            brief.executive_summary = brief_content.get("summary", "")
            brief.previous_interactions = json.dumps(client_data.get("interactions", []))
            brief.previous_appointments_summary = brief_content.get("appointments_summary", "")
            brief.open_topics = json.dumps(brief_content.get("open_topics", []))
            brief.follow_up_items = json.dumps(brief_content.get("follow_up_items", []))
            brief.client_preferences = json.dumps(client_data.get("preferences", {}))
            brief.communication_style = brief_content.get("communication_style", "neutral")
            brief.suggested_questions = json.dumps(brief_content.get("suggested_questions", []))
            brief.materials_to_prepare = json.dumps(brief_content.get("materials", []))
            brief.status = BriefStatus.GENERATED
            brief.generated_at = datetime.now()
            
            self.db.commit()
            return brief
            
        except Exception as e:
            print(f"Error generating brief: {e}")
            self.db.rollback()
            return None
    
    def _generate_pending_briefs(self) -> int:
        """Genera briefs para citas que ocurren en la próxima hora"""
        now = datetime.now()
        window_end = now + timedelta(hours=1)
        
        # Buscar citas en la próxima hora sin brief generado
        appointments = self.db.query(Appointment).filter(
            and_(
                Appointment.appointment_date == now.date(),
                Appointment.start_time >= now.time(),
                Appointment.start_time <= window_end.time(),
                Appointment.status.in_([
                    AppointmentStatus.PENDING,
                    AppointmentStatus.CONFIRMED
                ]),
                ~Appointment.brief.has()  # Sin brief existente
            )
        ).all()
        
        count = 0
        for appt in appointments:
            if self.generate_brief_for_appointment(appt.id):
                count += 1
        
        return count
    
    def _gather_client_data(self, client_id: int, professional_id: int) -> Dict[str, Any]:
        """Recopila toda la información disponible del cliente"""
        data = {
            "interactions": [],
            "preferences": {},
            "appointments": [],
            "notes": [],
            "emails": [],
            "insights": None
        }
        
        # Historial de citas
        appointments = self.db.query(Appointment).filter(
            and_(
                Appointment.client_id == client_id,
                Appointment.professional_id == professional_id
            )
        ).order_by(Appointment.appointment_date.desc()).all()
        
        for appt in appointments:
            data["appointments"].append({
                "date": appt.appointment_date.isoformat(),
                "service": appt.service_type,
                "status": appt.status.value,
                "notes": appt.notes
            })
        
        # Notas del cliente
        notes = self.db.query(ClientNote).filter(
            and_(
                ClientNote.client_id == client_id,
                ClientNote.professional_id == professional_id
            )
        ).order_by(ClientNote.created_at.desc()).all()
        
        for note in notes:
            data["notes"].append({
                "date": note.created_at.isoformat(),
                "content": note.content,
                "next_steps": note.next_steps
            })
        
        # Insights acumulados
        insight = self.db.query(ClientInsight).filter(
            and_(
                ClientInsight.client_id == client_id,
                ClientInsight.professional_id == professional_id
            )
        ).first()
        
        if insight:
            data["insights"] = {
                "communication_preferences": json.loads(insight.communication_preferences) if insight.communication_preferences else {},
                "decision_making_style": insight.decision_making_style,
                "common_topics": json.loads(insight.common_topics) if insight.common_topics else [],
                "pain_points": json.loads(insight.pain_points_history) if insight.pain_points_history else [],
                "personality_notes": insight.personality_notes
            }
        
        return data
    
    def _generate_brief_content(self, appointment: Appointment, client_data: Dict) -> Dict[str, Any]:
        """Genera el contenido del brief usando IA"""
        
        # Preparar contexto
        context = {
            "client_name": appointment.client.full_name if appointment.client else "Cliente",
            "service_type": appointment.service_type or "Consulta",
            "appointment_date": appointment.appointment_date.isoformat(),
            "appointment_time": appointment.start_time.isoformat(),
            "previous_appointments": len(client_data.get("appointments", [])),
            "notes_count": len(client_data.get("notes", [])),
            "insights": client_data.get("insights", {})
        }
        
        prompt = f"""
        Genera un briefing profesional para una cita con un cliente.
        
        CONTEXTO DEL CLIENTE:
        {json.dumps(context, indent=2, ensure_ascii=False)}
        
        HISTORIAL DE CITAS:
        {json.dumps(client_data.get("appointments", [])[:5], indent=2, ensure_ascii=False)}
        
        NOTAS PREVIAS:
        {json.dumps(client_data.get("notes", [])[:3], indent=2, ensure_ascii=False)}
        
        Genera un JSON con esta estructura:
        {{
            "summary": "Resumen ejecutivo en 2-3 oraciones del cliente y su situación",
            "appointments_summary": "Resumen de citas anteriores y resultados",
            "open_topics": ["Tema pendiente 1", "Tema pendiente 2"],
            "follow_up_items": ["Seguimiento 1", "Seguimiento 2"],
            "communication_style": "formal|casual|direct",
            "suggested_questions": ["Pregunta sugerida 1", "Pregunta sugerida 2", "Pregunta sugerida 3"],
            "materials": ["Material a preparar 1", "Material a preparar 2"]
        }}
        
        El briefing debe ser:
        - Profesional pero personal
        - Enfocado en temas pendientes
        - Útil para la preparación
        - En español
        
        Responde SOLO el JSON, sin explicaciones adicionales.
        """
        
        response = self.generate_text(
            prompt=prompt,
            system_prompt="Eres un asistente ejecutivo que prepara briefings detallados para profesionales antes de reuniones con clientes.",
            temperature=0.6
        )
        
        try:
            return json.loads(response)
        except:
            # Fallback si el JSON no es válido
            return {
                "summary": f"Cita con {context['client_name']} para {context['service_type']}",
                "appointments_summary": f"{context['previous_appointments']} citas previas",
                "open_topics": [],
                "follow_up_items": [],
                "communication_style": "neutral",
                "suggested_questions": ["¿En qué puedo ayudarle hoy?"],
                "materials": []
            }
    
    def _update_client_insights(self) -> int:
        """Actualiza insights acumulados de clientes"""
        # Buscar clientes con citas recientes sin insights actualizados
        recent_date = datetime.now() - timedelta(days=30)
        
        clients = self.db.query(User).join(Appointment).filter(
            and_(
                User.role == "client",
                Appointment.created_at >= recent_date
            )
        ).distinct().all()
        
        count = 0
        for client in clients:
            try:
                # Analizar patrones recientes
                recent_appointments = self.db.query(Appointment).filter(
                    Appointment.client_id == client.id
                ).order_by(Appointment.created_at.desc()).limit(5).all()
                
                if recent_appointments:
                    self._analyze_and_update_insight(client, recent_appointments)
                    count += 1
                    
            except Exception as e:
                print(f"Error updating insight for client {client.id}: {e}")
        
        return count
    
    def _analyze_and_update_insight(self, client: User, appointments: List[Appointment]):
        """Analiza citas recientes y actualiza insights del cliente"""
        # Recopilar datos para análisis
        notes_text = ""
        for appt in appointments:
            if appt.notes:
                notes_text += f"{appt.notes}\n"
        
        services = [appt.service_type for appt in appointments if appt.service_type]
        
        prompt = f"""
        Analiza el perfil de un cliente basado en sus citas recientes:
        
        Servicios solicitados: {', '.join(services) if services else 'No especificado'}
        Notas de citas: {notes_text[:500]}
        
        Extrae:
        1. Temas recurrentes de interés
        2. Estilo de comunicación aparente
        3. Patrones de comportamiento
        4. Posibles pain points
        
        Responde en JSON:
        {{
            "common_topics": ["tema1", "tema2"],
            "communication_style": "descripción del estilo",
            "behavior_patterns": ["patrón1", "patrón2"],
            "pain_points": ["pain1", "pain2"],
            "personality_notes": "notas sobre personalidad"
        }}
        """
        
        response = self.generate_text(
            prompt=prompt,
            system_prompt="Eres un analista de comportamiento del cliente.",
            temperature=0.5
        )
        
        try:
            analysis = json.loads(response)
            
            # Actualizar o crear insight
            for appt in appointments:
                if appt.professional_id:
                    insight = self.db.query(ClientInsight).filter(
                        and_(
                            ClientInsight.client_id == client.id,
                            ClientInsight.professional_id == appt.professional_id
                        )
                    ).first()
                    
                    if not insight:
                        insight = ClientInsight(
                            client_id=client.id,
                            professional_id=appt.professional_id
                        )
                        self.db.add(insight)
                    
                    insight.common_topics = json.dumps(analysis.get("common_topics", []))
                    insight.decision_making_style = analysis.get("communication_style", "")
                    insight.pain_points_history = json.dumps(analysis.get("pain_points", []))
                    insight.personality_notes = analysis.get("personality_notes", "")
                    insight.total_appointments = len(appointments)
                    insight.last_updated = datetime.now()
                    
                    break  # Solo actualizar para un professional
            
            self.db.commit()
            
        except Exception as e:
            print(f"Error parsing insight analysis: {e}")
    
    def get_brief_for_dashboard(self, appointment_id: int) -> Dict[str, Any]:
        """Obtiene el brief formateado para mostrar en el dashboard"""
        brief = self.db.query(AppointmentBrief).filter(
            AppointmentBrief.appointment_id == appointment_id
        ).first()
        
        if not brief:
            return {"error": "Brief not found"}
        
        return {
            "status": brief.status.value,
            "executive_summary": brief.executive_summary,
            "previous_appointments": json.loads(brief.previous_appointments_summary) if brief.previous_appointments_summary else [],
            "open_topics": json.loads(brief.open_topics) if brief.open_topics else [],
            "follow_up_items": json.loads(brief.follow_up_items) if brief.follow_up_items else [],
            "client_preferences": json.loads(brief.client_preferences) if brief.client_preferences else {},
            "communication_style": brief.communication_style,
            "suggested_questions": json.loads(brief.suggested_questions) if brief.suggested_questions else [],
            "materials_to_prepare": json.loads(brief.materials_to_prepare) if brief.materials_to_prepare else [],
            "generated_at": brief.generated_at.isoformat() if brief.generated_at else None
        }
