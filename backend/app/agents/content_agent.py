"""
Agente ContentGenerator - Genera contenido para redes sociales automáticamente

Este agente:
1. Analiza el nicho y servicios del profesional
2. Genera posts personalizados para Instagram/LinkedIn
3. Incluye CTAs estratégicos al link de reserva
4. Programa publicación (o guarda en borradores)
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.models import (
    GeneratedContent, ContentStrategy, ContentStatus,
    GrowthMetrics, Professional
)
from app.agents.base import BaseAgent
import json
import random

class ContentAgent(BaseAgent):
    """Agente que genera contenido de marketing automáticamente"""
    
    # Templates de contenido por industria
    CONTENT_TEMPLATES = {
        "consulting": [
            "3 errores que cometen {target} con {topic}",
            "El framework que usé para ayudar a {client_type} a {result}",
            "Preguntas que debes hacerte antes de contratar {service}",
            "Caso de estudio: Cómo {client} logró {result} en {timeframe}",
            "La verdad sobre {topic} que nadie te cuenta"
        ],
        "therapy": [
            "3 señales de que necesitas apoyo con {topic}",
            "Lo que he aprendido de {client_type} sobre {topic}",
            "Pequeños cambios que hacen gran diferencia en {topic}",
            "Testimonio anónimo: 'Cómo {service} cambió mi vida'",
            "Mitos sobre {topic} que debemos dejar atrás"
        ],
        "legal": [
            "Lo que todo {target} debe saber sobre {topic}",
            "Errores costosos que cometen {target} sin darse cuenta",
            "Guía rápida: {topic} en 5 minutos",
            "Caso real: Cómo protegimos a {client} de {problem}",
            "Preguntas frecuentes sobre {topic}"
        ],
        "coaching": [
            "El mindset shift que cambió todo para {client_type}",
            "Por qué {common_belief} está frenando tu {goal}",
            "3 hábitos de {successful_people} que puedes copiar hoy",
            "De {before_state} a {after_state}: La historia de {client}",
            "El ejercicio de 5 minutos que recomiendo a todos mis clientes"
        ]
    }
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def run(self) -> Dict[str, Any]:
        """Ejecuta el ciclo de generación de contenido"""
        results = {
            "content_generated": 0,
            "content_scheduled": 0,
            "errors": []
        }
        
        try:
            # 1. Generar contenido para profesionales activos
            generated = self._generate_content_for_professionals()
            results["content_generated"] = generated
            
            # 2. Programar contenido según estrategia
            scheduled = self._schedule_generated_content()
            results["content_scheduled"] = scheduled
            
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    def generate_content_for_professional(self, professional_id: int, 
                                         platform: str = "instagram",
                                         content_type: str = "post") -> Optional[GeneratedContent]:
        """Genera un contenido específico para un profesional"""
        try:
            # Obtener estrategia del profesional
            strategy = self.db.query(ContentStrategy).filter(
                ContentStrategy.professional_id == professional_id
            ).first()
            
            if not strategy:
                # Crear estrategia por defecto
                strategy = self._create_default_strategy(professional_id)
            
            professional = self.db.query(Professional).filter(
                Professional.id == professional_id
            ).first()
            
            if not professional:
                return None
            
            # Detectar industria
            industry = self._detect_industry(professional.specialty)
            
            # Seleccionar template
            templates = self.CONTENT_TEMPLATES.get(industry, self.CONTENT_TEMPLATES["consulting"])
            template = random.choice(templates)
            
            # Generar contenido con IA
            content_data = self._generate_content_with_ai(
                professional=professional,
                strategy=strategy,
                template=template,
                platform=platform
            )
            
            # Crear registro
            content = GeneratedContent(
                professional_id=professional_id,
                platform=platform,
                content_type=content_type,
                title=content_data.get("title", ""),
                content=content_data.get("content", ""),
                hashtags=json.dumps(content_data.get("hashtags", [])),
                cta_text=content_data.get("cta", "Reserva tu consulta aquí 👇"),
                link_to_include=strategy.booking_link or "",
                status=ContentStatus.DRAFT,
                predicted_engagement_score=content_data.get("engagement_score", 5),
                target_audience=strategy.target_audience_description or "general"
            )
            
            self.db.add(content)
            self.db.commit()
            
            return content
            
        except Exception as e:
            print(f"Error generating content: {e}")
            self.db.rollback()
            return None
    
    def _generate_content_for_professionals(self) -> int:
        """Genera contenido para todos los profesionales activos"""
        strategies = self.db.query(ContentStrategy).filter(
            ContentStrategy.is_active == True
        ).all()
        
        count = 0
        for strategy in strategies:
            # Verificar cuánto contenido tiene pendiente
            pending = self.db.query(GeneratedContent).filter(
                and_(
                    GeneratedContent.professional_id == strategy.professional_id,
                    GeneratedContent.status.in_([ContentStatus.DRAFT, ContentStatus.SCHEDULED])
                )
            ).count()
            
            # Si tiene menos de 5 posts pendientes, generar más
            if pending < 5:
                platforms = json.loads(strategy.preferred_platforms) if strategy.preferred_platforms else ["instagram"]
                
                for platform in platforms[:2]:  # Máximo 2 plataformas
                    if self.generate_content_for_professional(
                        strategy.professional_id, 
                        platform=platform
                    ):
                        count += 1
        
        return count
    
    def _generate_content_with_ai(self, professional, strategy, template, platform) -> Dict[str, Any]:
        """Genera contenido usando OpenAI"""
        
        # Preparar variables para el template
        variables = {
            "target": strategy.target_audience_description or "emprendedores",
            "topic": professional.specialty or "tu negocio",
            "service": professional.specialty or "mi servicio",
            "client_type": "mis clientes",
            "result": "multiplicar sus ventas",
            "timeframe": "3 meses",
            "client": "un cliente reciente",
            "before_state": "estancado",
            "after_state": "crecer consistentemente",
            "successful_people": "emprendedores exitosos",
            "common_belief": "trabajar más horas",
            "goal": "crecimiento",
            "problem": "un error común"
        }
        
        # Completar template
        title = template.format(**variables)
        
        # Generar contenido completo
        prompt = f"""
        Escribe un post de {platform} para un profesional:
        
        Nombre: {professional.user.full_name if professional.user else 'Profesional'}
        Especialidad: {professional.specialty or 'Consultoría'}
        Bio: {professional.bio or 'Experto en su campo'}
        Audiencia: {strategy.target_audience_description or 'Emprendedores'}
        Tono: {strategy.tone_of_voice or 'profesional'}
        
        TÍTULO PROPUESTO: {title}
        
        REQUISITOS:
        1. Post de {platform} (formato adecuado)
        2. Contenido valioso y práctico
        3. Incluir CTA suave al final (no agresivo)
        4. Mencionar link de reserva indirectamente
        5. En español
        
        FORMATO DE RESPUESTA (JSON):
        {{
            "title": "título del post",
            "content": "contenido completo del post",
            "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
            "cta": "call to action específico",
            "engagement_score": 7
        }}
        
        Responde SOLO el JSON.
        """
        
        response = self.generate_text(
            prompt=prompt,
            system_prompt="Eres un experto en marketing de contenidos para redes sociales.",
            temperature=0.8
        )
        
        try:
            return json.loads(response)
        except:
            # Fallback
            return {
                "title": title,
                "content": f"{title}\n\n[Contenido generado automáticamente]\n\n¿Quieres saber más? Agenda una consulta gratuita.",
                "hashtags": ["#negocios", "#emprendedores", "#consultoria"],
                "cta": "Link en bio para agendar",
                "engagement_score": 5
            }
    
    def _create_default_strategy(self, professional_id: int) -> ContentStrategy:
        """Crea una estrategia de contenido por defecto"""
        professional = self.db.query(Professional).filter(
            Professional.id == professional_id
        ).first()
        
        strategy = ContentStrategy(
            professional_id=professional_id,
            tone_of_voice="professional",
            posting_frequency=3,
            preferred_platforms=json.dumps(["instagram", "linkedin"]),
            content_pillars=json.dumps(["tips", "case_studies", "common_mistakes"]),
            target_audience_description="emprendedores y pequeñas empresas",
            booking_link=f"https://clientflow-pro.vercel.app/book/{professional.slug if professional else 'demo'}",
            optimal_posting_times=json.dumps({"instagram": "14:00", "linkedin": "09:00"})
        )
        
        self.db.add(strategy)
        self.db.commit()
        
        return strategy
    
    def _detect_industry(self, specialty: Optional[str]) -> str:
        """Detecta la industria basada en especialidad"""
        if not specialty:
            return "consulting"
        
        specialty_lower = specialty.lower()
        
        if any(word in specialty_lower for word in ["psic", "terapia", "salud", "mental"]):
            return "therapy"
        elif any(word in specialty_lower for word in ["legal", "abogado", "ley", "derecho"]):
            return "legal"
        elif any(word in specialty_lower for word in ["coach", "life coach", "desarrollo personal"]):
            return "coaching"
        else:
            return "consulting"
    
    def _schedule_generated_content(self) -> int:
        """Programa contenido según la estrategia"""
        draft_content = self.db.query(GeneratedContent).filter(
            GeneratedContent.status == ContentStatus.DRAFT
        ).all()
        
        count = 0
        for content in draft_content:
            # Programar para próximos días
            content.scheduled_at = datetime.now() + timedelta(days=random.randint(1, 7))
            content.status = ContentStatus.SCHEDULED
            count += 1
        
        self.db.commit()
        return count
    
    def get_content_calendar(self, professional_id: int) -> List[Dict[str, Any]]:
        """Obtiene el calendario de contenido para un profesional"""
        content = self.db.query(GeneratedContent).filter(
            GeneratedContent.professional_id == professional_id
        ).order_by(GeneratedContent.scheduled_at).all()
        
        return [
            {
                "id": c.id,
                "platform": c.platform,
                "title": c.title,
                "status": c.status.value,
                "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else None,
                "engagement_score": c.predicted_engagement_score
            }
            for c in content
        ]
