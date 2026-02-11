"""
Agente ReviewBooster - Solicita y gestiona reviews automáticamente

Este agente:
1. Detecta citas completadas exitosamente
2. Envía solicitud de review personalizada (24-48h post-cita)
3. Publica reviews en página pública del profesional
4. Gestiona recompensas por reviews
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.models import (
    ReviewRequest, ReviewStatus, PublicReview,
    Appointment, AppointmentStatus, GrowthMetrics,
    Professional, User
)
from app.core.email import send_email
from app.agents.base import BaseAgent
import json

class ReviewAgent(BaseAgent):
    """Agente que gestiona reviews y testimonios automáticamente"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def run(self) -> Dict[str, Any]:
        """Ejecuta el ciclo de gestión de reviews"""
        results = {
            "reviews_requested": 0,
            "reviews_received": 0,
            "reviews_published": 0,
            "errors": []
        }
        
        try:
            # 1. Identificar citas completadas y solicitar reviews
            requested = self._request_reviews_for_completed_appointments()
            results["reviews_requested"] = requested
            
            # 2. Procesar reviews recibidas
            received = self._process_received_reviews()
            results["reviews_received"] = received
            
            # 3. Publicar reviews aprobadas
            published = self._publish_approved_reviews()
            results["reviews_published"] = published
            
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    def request_review_for_appointment(self, appointment_id: int) -> bool:
        """Solicita review para una cita específica"""
        try:
            appointment = self.db.query(Appointment).filter(
                Appointment.id == appointment_id
            ).first()
            
            if not appointment or appointment.status != AppointmentStatus.COMPLETED:
                return False
            
            # Verificar si ya se solicitó
            existing = self.db.query(ReviewRequest).filter(
                ReviewRequest.appointment_id == appointment_id
            ).first()
            
            if existing:
                return False
            
            professional = appointment.professional
            client = appointment.client
            
            if not professional or not client:
                return False
            
            # Generar mensaje personalizado
            message = self._generate_review_request_message(
                professional=professional,
                client=client,
                appointment=appointment
            )
            
            # Enviar email
            if client.email:
                send_email(
                    to_email=client.email,
                    subject=f"¿Cómo fue tu experiencia con {professional.user.full_name if professional.user else 'nosotros'}?",
                    body=message
                )
            
            # Crear registro
            review_request = ReviewRequest(
                appointment_id=appointment_id,
                professional_id=professional.id,
                client_id=client.id,
                request_message=message,
                sent_at=datetime.now(),
                status=ReviewStatus.REQUESTED
            )
            
            self.db.add(review_request)
            self.db.commit()
            
            return True
            
        except Exception as e:
            print(f"Error requesting review: {e}")
            self.db.rollback()
            return False
    
    def _request_reviews_for_completed_appointments(self) -> int:
        """Busca citas completadas sin review solicitada"""
        # Citas completadas en las últimas 48h sin review request
        cutoff = datetime.now() - timedelta(hours=48)
        
        appointments = self.db.query(Appointment).filter(
            and_(
                Appointment.status == AppointmentStatus.COMPLETED,
                Appointment.updated_at >= cutoff,
                ~Appointment.review_requests.any()  # Sin review request
            )
        ).all()
        
        count = 0
        for appt in appointments:
            if self.request_review_for_appointment(appt.id):
                count += 1
        
        return count
    
    def _process_received_reviews(self) -> int:
        """Procesa reviews que han sido recibidas"""
        # En un sistema real, esto vendría de un formulario o integración
        # Aquí simulamos el procesamiento
        
        pending_reviews = self.db.query(ReviewRequest).filter(
            and_(
                ReviewRequest.status == ReviewStatus.REQUESTED,
                ReviewRequest.sent_at <= datetime.now() - timedelta(days=7)
            )
        ).all()
        
        # Recordatorio para reviews no respondidas
        for review in pending_reviews:
            # Podríamos enviar un recordatorio suave aquí
            pass
        
        return 0  # Depende de integración externa
    
    def submit_review(self, review_request_id: int, rating: int, 
                     review_text: str, client_name: str = None) -> bool:
        """Procesa una review enviada por un cliente"""
        try:
            review_request = self.db.query(ReviewRequest).filter(
                ReviewRequest.id == review_request_id
            ).first()
            
            if not review_request:
                return False
            
            # Actualizar request
            review_request.client_rating = rating
            review_request.client_review_text = review_text
            review_request.received_at = datetime.now()
            review_request.status = ReviewStatus.RECEIVED
            
            # Crear public review
            public_review = PublicReview(
                professional_id=review_request.professional_id,
                review_request_id=review_request.id,
                client_name=client_name or "Cliente anónimo",
                rating=rating,
                review_text=review_text,
                service_received=review_request.appointment.service_type if review_request.appointment else "Consulta",
                keywords=json.dumps(self._extract_keywords(review_text)),
                is_featured=(rating >= 5)  # Destacar si es 5 estrellas
            )
            
            self.db.add(public_review)
            
            # Publicar automáticamente si rating >= 4
            if rating >= 4:
                review_request.status = ReviewStatus.PUBLISHED
                review_request.published_at = datetime.now()
                review_request.published_on_website = True
                public_review.published_at = datetime.now()
            
            self.db.commit()
            
            # Enviar agradecimiento
            self._send_review_thank_you(review_request, rating)
            
            return True
            
        except Exception as e:
            print(f"Error submitting review: {e}")
            self.db.rollback()
            return False
    
    def _publish_approved_reviews(self) -> int:
        """Publica reviews aprobadas"""
        # Reviews recibidas pero no publicadas
        reviews = self.db.query(ReviewRequest).filter(
            ReviewRequest.status == ReviewStatus.RECEIVED
        ).all()
        
        count = 0
        for review in reviews:
            if review.client_rating >= 4:  # Auto-publicar buenas reviews
                review.status = ReviewStatus.PUBLISHED
                review.published_at = datetime.now()
                review.published_on_website = True
                count += 1
        
        self.db.commit()
        return count
    
    def _generate_review_request_message(self, professional, client, appointment) -> str:
        """Genera mensaje de solicitud de review"""
        
        prompt = f"""
        Escribe un email corto pidiendo una review/testimonio.
        
        Contexto:
        - Profesional: {professional.user.full_name if professional.user else 'Consultor'}
        - Cliente: {client.full_name if client else 'Cliente'}
        - Servicio: {appointment.service_type or 'Consulta'}
        - La cita fue exitosa
        
        El email debe:
        1. Agradecer por la cita
        2. Pedir honestamente un testimonio (2-3 oraciones)
        3. Mencionar que ayuda a otros a encontrar el servicio
        4. Incluir link de review (placeholder [REVIEW_LINK])
        5. No sonar desesperado o pushy
        
        Máximo 150 palabras.
        """
        
        return self.generate_text(
            prompt=prompt,
            system_prompt="Eres un experto en customer success. Pides reviews de forma natural.",
            temperature=0.7
        ) or f"""
        Hola {client.full_name if client else ''},
        
        Gracias por confiar en mí para tu {appointment.service_type or 'consulta'}.
        
        Si te fue útil, ¿me ayudarías con un breve testimonio? Solo 2-3 oraciones sobre tu experiación ayudan mucho a otros a encontrar este servicio.
        
        Puedes dejarlo aquí: [REVIEW_LINK]
        
        ¡Gracias!
        {professional.user.full_name if professional.user else ''}
        """
    
    def _send_review_thank_you(self, review_request, rating: int):
        """Envía agradecimiento por la review"""
        if rating >= 4:
            prompt = "Genera un email corto agradeciendo una review positiva de 5 estrellas. Mencionar que significa mucho. Máximo 50 palabras."
        else:
            prompt = "Genera un email corto agradeciendo una review constructiva. Mencionar que se tomará en cuenta para mejorar. Máximo 50 palabras."
        
        message = self.generate_text(prompt=prompt, temperature=0.7)
        
        if review_request.client and review_request.client.email:
            send_email(
                to_email=review_request.client.email,
                subject="Gracias por tu feedback",
                body=message or "Gracias por tomarte el tiempo de compartir tu experiencia."
            )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae keywords del texto para SEO"""
        # Palabras comunes a ignorar
        stopwords = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'con']
        
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 4 and w not in stopwords]
        
        return list(set(keywords))[:10]  # Top 10 keywords únicos
    
    def get_public_reviews(self, professional_id: int, featured_only: bool = False) -> List[Dict[str, Any]]:
        """Obtiene reviews públicas de un profesional"""
        query = self.db.query(PublicReview).filter(
            PublicReview.professional_id == professional_id
        )
        
        if featured_only:
            query = query.filter(PublicReview.is_featured == True)
        
        reviews = query.order_by(PublicReview.published_at.desc()).all()
        
        return [
            {
                "id": r.id,
                "client_name": r.client_name,
                "rating": r.rating,
                "review_text": r.review_text,
                "service": r.service_received,
                "is_featured": r.is_featured,
                "published_at": r.published_at.isoformat() if r.published_at else None
            }
            for r in reviews
        ]
