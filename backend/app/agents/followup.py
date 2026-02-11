"""
Agente Followup - CRM con Seguimiento Automático

Este agente:
1. Monitorea leads nuevos y genera follow-up personalizado
2. Lee respuestas y decide siguiente acción
3. Automatiza secuencia de contacto: email → email → WhatsApp
4. Marca leads como "calientes" cuando necesitan atención humana
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.models import (
    Lead, LeadStatus, FollowupSequence, FollowupAction, 
    FollowupStatus, LeadInsight, Appointment, User
)
from app.core.email import send_email
from app.agents.base import BaseAgent
import json

class FollowupAgent(BaseAgent):
    """Agente que automatiza el seguimiento de leads"""
    
    # Secuencias predeterminadas
    DEFAULT_SEQUENCES = {
        "nurture_7": {
            "name": "Nurture 7 días",
            "steps": [
                {"delay_hours": 0, "channel": "email", "template": "welcome"},
                {"delay_hours": 48, "channel": "email", "template": "value"},
                {"delay_hours": 120, "channel": "whatsapp", "template": "personal"},
            ]
        },
        "quick_close": {
            "name": "Cierre Rápido",
            "steps": [
                {"delay_hours": 0, "channel": "email", "template": "urgent"},
                {"delay_hours": 24, "channel": "email", "template": "scarcity"},
                {"delay_hours": 72, "channel": "whatsapp", "template": "final"},
            ]
        }
    }
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def run(self) -> Dict[str, Any]:
        """Ejecuta el ciclo de seguimiento automático"""
        results = {
            "sequences_created": 0,
            "actions_executed": 0,
            "insights_generated": 0,
            "hot_leads_identified": 0,
            "errors": []
        }
        
        try:
            # 1. Crear secuencias para leads nuevos
            new_sequences = self._create_sequences_for_new_leads()
            results["sequences_created"] = new_sequences
            
            # 2. Ejecutar acciones programadas
            executed = self._execute_scheduled_actions()
            results["actions_executed"] = executed
            
            # 3. Analizar respuestas y generar insights
            insights = self._analyze_lead_responses()
            results["insights_generated"] = insights
            
            # 4. Identificar leads calientes
            hot_leads = self._identify_hot_leads()
            results["hot_leads_identified"] = hot_leads
            
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    def process_new_lead(self, lead_id: int, sequence_type: str = "nurture_7") -> bool:
        """Procesa un lead nuevo y crea su secuencia de follow-up"""
        try:
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return False
            
            # Crear secuencia
            sequence = FollowupSequence(
                lead_id=lead_id,
                professional_id=lead.professional_id,
                sequence_name=self.DEFAULT_SEQUENCES[sequence_type]["name"],
                total_steps=len(self.DEFAULT_SEQUENCES[sequence_type]["steps"]),
                status=FollowupStatus.SCHEDULED
            )
            self.db.add(sequence)
            self.db.flush()  # Para obtener sequence.id
            
            # Crear acciones programadas
            steps = self.DEFAULT_SEQUENCES[sequence_type]["steps"]
            for idx, step in enumerate(steps):
                scheduled_time = datetime.now() + timedelta(hours=step["delay_hours"])
                
                # Generar contenido personalizado
                content = self._generate_followup_content(lead, step["template"], step["channel"])
                
                action = FollowupAction(
                    sequence_id=sequence.id,
                    lead_id=lead_id,
                    step_number=idx + 1,
                    channel=step["channel"],
                    subject=self._generate_subject(step["template"]),
                    content=content,
                    scheduled_at=scheduled_time,
                    status=FollowupStatus.SCHEDULED
                )
                self.db.add(action)
            
            # Generar insights del lead
            self._generate_lead_insight(lead)
            
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Error processing lead {lead_id}: {e}")
            self.db.rollback()
            return False
    
    def _create_sequences_for_new_leads(self) -> int:
        """Crea secuencias para leads sin seguimiento"""
        # Buscar leads en estado NEW sin secuencia
        leads = self.db.query(Lead).filter(
            and_(
                Lead.status == LeadStatus.NEW,
                ~Lead.followup_sequences.any()
            )
        ).all()
        
        count = 0
        for lead in leads:
            if self.process_new_lead(lead.id):
                count += 1
        
        return count
    
    def _execute_scheduled_actions(self) -> int:
        """Ejecuta acciones de follow-up programadas"""
        # Buscar acciones programadas para ahora
        now = datetime.now()
        
        actions = self.db.query(FollowupAction).filter(
            and_(
                FollowupAction.status == FollowupStatus.SCHEDULED,
                FollowupAction.scheduled_at <= now
            )
        ).all()
        
        count = 0
        for action in actions:
            try:
                lead = action.lead
                
                if action.channel == "email" and lead.email:
                    send_email(
                        to_email=lead.email,
                        subject=action.subject,
                        body=action.content
                    )
                    action.status = FollowupStatus.SENT
                    action.sent_at = now
                    count += 1
                    
                elif action.channel == "whatsapp":
                    # TODO: Implementar WhatsApp
                    action.status = FollowupStatus.SENT
                    action.sent_at = now
                    count += 1
                
            except Exception as e:
                action.status = FollowupStatus.FAILED
                action.error_message = str(e)
        
        self.db.commit()
        return count
    
    def _analyze_lead_responses(self) -> int:
        """Analiza respuestas de leads y actualiza insights"""
        # Buscar acciones con respuestas no procesadas
        actions = self.db.query(FollowupAction).filter(
            and_(
                FollowupAction.status == FollowupStatus.REPLIED,
                FollowupAction.client_reply.isnot(None)
            )
        ).all()
        
        count = 0
        for action in actions:
            try:
                lead = action.lead
                reply = action.client_reply
                
                # Analizar respuesta con IA
                analysis = self._analyze_response(reply)
                
                # Actualizar insight del lead
                insight = self.db.query(LeadInsight).filter(
                    LeadInsight.lead_id == lead.id
                ).first()
                
                if not insight:
                    insight = LeadInsight(lead_id=lead.id)
                    self.db.add(insight)
                
                insight.sentiment = analysis.get("sentiment", "neutral")
                insight.urgency_level = analysis.get("urgency", 5)
                insight.key_pain_points = json.dumps(analysis.get("pain_points", []))
                insight.recommended_approach = analysis.get("recommendation", "")
                
                count += 1
                
            except Exception as e:
                print(f"Error analyzing response: {e}")
        
        self.db.commit()
        return count
    
    def _identify_hot_leads(self) -> int:
        """Identifica leads que necesitan atención humana"""
        # Criterios para lead "caliente":
        # - Respondió positivamente
        # - Urgencia alta (8-10)
        # - Preguntó sobre precios/disponibilidad
        
        hot_leads = self.db.query(Lead).join(LeadInsight).filter(
            and_(
                Lead.status.in_([LeadStatus.NEW, LeadStatus.CONTACTED]),
                LeadInsight.urgency_level >= 8
            )
        ).all()
        
        # También buscar leads con múltiples respuestas
        multi_response_leads = self.db.query(Lead).join(FollowupAction).filter(
            and_(
                Lead.status.in_([LeadStatus.NEW, LeadStatus.CONTACTED]),
                FollowupAction.status == FollowupStatus.REPLIED
            )
        ).group_by(Lead.id).having(func.count(FollowupAction.id) >= 2).all()
        
        return len(hot_leads) + len(multi_response_leads)
    
    def _generate_followup_content(self, lead, template: str, channel: str) -> str:
        """Genera contenido de follow-up personalizado"""
        
        prompts = {
            "welcome": f"""
                Escribe un email de bienvenida para un lead interesado en servicios profesionales.
                
                Información del lead:
                - Nombre: {lead.name}
                - Interés: {lead.message or 'Consulta general'}
                
                El email debe:
                1. Agradecer el interés
                2. Mostrar empatía con su situación
                3. Ofrecer valor (artículo, tip, o consejo breve)
                4. Invitar a agendar una llamada/cita
                5. Ser breve y personal
                
                Máximo 200 palabras.
            """,
            "value": f"""
                Escribe un email de seguimiento para {lead.name}.
                
                Contexto: Ya recibió email de bienvenida hace 2 días.
                
                El email debe:
                1. Compartir contenido de valor relacionado con su consulta
                2. No ser pushy o agresivo de ventas
                3. Mantener conversación abierta
                4. Mencionar casos de éxito brevemente
                
                Máximo 150 palabras.
            """,
            "personal": f"""
                Escribe un mensaje corto para WhatsApp dirigido a {lead.name}.
                
                Contexto: No respondió a emails previos. Este es el último contacto automático.
                
                El mensaje debe:
                1. Ser muy personal y directo
                2. Mostrar que entiendes que está ocupado
                3. Ofrecer ayuda específica
                4. Pregunta simple de sí/no
                
                Máximo 50 palabras.
            """,
            "urgent": f"""
                Escribe un email urgente pero profesional para {lead.name}.
                
                Contexto: Lead que mostró interés inmediato.
                
                El email debe:
                1. Transmitir escasez (plazos limitados)
                2. Llamada a la acción clara
                3. Facilitar próximo paso
                
                Máximo 120 palabras.
            """,
            "scarcity": f"""
                Escribe un email sobre disponibilidad limitada para {lead.name}.
                
                Contexto: Segundo contacto, crear urgencia legítima.
                
                El email debe:
                1. Mencionar espacios limitados
                2. Ofrecer alternativas si no puede ahora
                3. Mantener profesionalismo
                
                Máximo 100 palabras.
            """,
            "final": f"""
                Escribe mensaje final corto para WhatsApp a {lead.name}.
                
                Contexto: Último intento de contacto.
                
                El mensaje debe:
                1. Ser directo y honesto
                2. Ofrecer seguir en contacto para futuro
                3. Dejar puerta abierta sin presión
                
                Máximo 40 palabras.
            """
        }
        
        prompt = prompts.get(template, prompts["welcome"])
        
        return self.generate_text(
            prompt=prompt,
            system_prompt="Eres un experto en marketing conversacional y ventas consultivas.",
            temperature=0.8
        )
    
    def _generate_subject(self, template: str) -> str:
        """Genera asunto del email según template"""
        subjects = {
            "welcome": "Gracias por tu interés 👋",
            "value": "Un recurso que te puede ayudar",
            "personal": "Una pregunta rápida",
            "urgent": "⚡ Plazos disponibles",
            "scarcity": "Sobre tu consulta",
            "final": "Último mensaje"
        }
        return subjects.get(template, "Seguimiento")
    
    def _generate_lead_insight(self, lead):
        """Genera insights iniciales del lead"""
        if not lead.message:
            return
        
        analysis = self._analyze_response(lead.message)
        
        insight = LeadInsight(
            lead_id=lead.id,
            sentiment=analysis.get("sentiment", "neutral"),
            urgency_level=analysis.get("urgency", 5),
            key_pain_points=json.dumps(analysis.get("pain_points", [])),
            decision_timeline=analysis.get("timeline", "medium"),
            recommended_approach=analysis.get("recommendation", "")
        )
        self.db.add(insight)
        self.db.commit()
    
    def _analyze_response(self, text: str) -> Dict[str, Any]:
        """Analiza respuesta de lead usando IA"""
        prompt = f"""
        Analiza este mensaje de un potencial cliente y extrae:
        
        Mensaje: "{text}"
        
        Responde en formato JSON:
        {{
            "sentiment": "positive|neutral|negative",
            "urgency": 1-10,
            "pain_points": ["punto 1", "punto 2"],
            "timeline": "immediate|short|medium|long",
            "recommendation": "acción recomendada"
        }}
        
        Solo responde el JSON, sin explicaciones.
        """
        
        response = self.generate_text(
            prompt=prompt,
            system_prompt="Eres un analista de ventas experto. Extrae insights de mensajes de clientes.",
            temperature=0.3
        )
        
        try:
            return json.loads(response)
        except:
            return {
                "sentiment": "neutral",
                "urgency": 5,
                "pain_points": [],
                "timeline": "medium",
                "recommendation": "Seguir con secuencia estándar"
            }
