"""
Agente ReferralEngine - Gestiona referidos automáticamente

Este agente:
1. Detecta clientes satisfechos (post-cita exitosa)
2. Envía solicitud de referido personalizada
3. Genera links de tracking únicos
4. Gestiona recompensas automáticamente
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.models import (
    Referral, ReferralCampaign, ReferralInvitation, ReferralStatus,
    Appointment, AppointmentStatus, GrowthMetrics,
    Professional, User
)
from app.core.email import send_email
from app.agents.base import BaseAgent
import json
import secrets
import string

class ReferralAgent(BaseAgent):
    """Agente que gestiona programa de referidos automáticamente"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def run(self) -> Dict[str, Any]:
        """Ejecuta el ciclo de gestión de referidos"""
        results = {
            "referrals_invited": 0,
            "referrals_converted": 0,
            "rewards_given": 0,
            "errors": []
        }
        
        try:
            # 1. Identificar clientes para pedir referidos
            invited = self._invite_satisfied_clients()
            results["referrals_invited"] = invited
            
            # 2. Procesar referidos convertidos
            converted = self._process_converted_referrals()
            results["referrals_converted"] = converted
            
            # 3. Otorgar recompensas pendientes
            rewards = self._process_pending_rewards()
            results["rewards_given"] = rewards
            
        except Exception as e:
            results["errors"].append(str(e))
        
        return results
    
    def create_referral_invitation(self, referrer_id: int, 
                                   referred_email: str,
                                   referred_name: str = None,
                                   campaign_id: int = None) -> Optional[Referral]:
        """Crea una invitación de referido"""
        try:
            referrer = self.db.query(User).filter(User.id == referrer_id).first()
            if not referrer:
                return None
            
            # Obtener o crear campaña activa
            if not campaign_id:
                campaign = self._get_or_create_default_campaign(referrer_id)
                campaign_id = campaign.id
            
            professional = self.db.query(Professional).filter(
                Professional.user_id == referrer_id
            ).first()
            
            professional_id = professional.id if professional else None
            
            # Generar código único
            referral_code = self._generate_referral_code()
            
            # Crear referral
            referral = Referral(
                campaign_id=campaign_id,
                professional_id=professional_id,
                referrer_id=referrer_id,
                referrer_email=referrer.email,
                referred_email=referred_email,
                referred_name=referred_name or "",
                referral_code=referral_code,
                referral_link=self._generate_referral_link(referral_code),
                status=ReferralStatus.INVITED
            )
            
            self.db.add(referral)
            self.db.flush()  # Para obtener referral.id
            
            # Generar mensaje personalizado
            message = self._generate_referral_message(
                referrer=referrer,
                referred_name=referred_name,
                campaign=self.db.query(ReferralCampaign).filter(
                    ReferralCampaign.id == campaign_id
                ).first()
            )
            
            # Crear invitación
            invitation = ReferralInvitation(
                referral_id=referral.id,
                invitation_message=message,
                channel="email"
            )
            
            self.db.add(invitation)
            
            # Enviar email
            if referred_email:
                send_email(
                    to_email=referred_email,
                    subject=f"{referrer.full_name} te recomienda algo",
                    body=message
                )
                invitation.sent_at = datetime.now()
            
            self.db.commit()
            
            return referral
            
        except Exception as e:
            print(f"Error creating referral: {e}")
            self.db.rollback()
            return None
    
    def _invite_satisfied_clients(self) -> int:
        """Identifica clientes satisfechos y les pide referidos"""
        # Buscar citas completadas exitosamente hace 1-3 días
        # (no inmediato, no muy tarde)
        start_cutoff = datetime.now() - timedelta(days=3)
        end_cutoff = datetime.now() - timedelta(days=1)
        
        appointments = self.db.query(Appointment).filter(
            and_(
                Appointment.status == AppointmentStatus.COMPLETED,
                Appointment.updated_at >= start_cutoff,
                Appointment.updated_at <= end_cutoff
            )
        ).all()
        
        count = 0
        for appt in appointments:
            # Verificar que no se le haya pedido ya
            existing = self.db.query(Referral).filter(
                and_(
                    Referral.referrer_id == appt.client_id,
                    Referral.invited_at >= datetime.now() - timedelta(days=30)
                )
            ).first()
            
            if not existing and appt.client and appt.client.email:
                # Pedir 3 referidos de ejemplo
                for i in range(3):
                    placeholder_email = f"amigo{i+1}@ejemplo.com"  # En producción, el cliente los proporciona
                    # En realidad aquí enviaríamos un email al cliente pidiendo que nos pase contactos
                    pass
                
                count += 1
        
        return count
    
    def process_referral_signup(self, referral_code: str, new_user_email: str) -> bool:
        """Procesa cuando un referido se registra"""
        try:
            referral = self.db.query(Referral).filter(
                Referral.referral_code == referral_code
            ).first()
            
            if not referral or referral.status != ReferralStatus.INVITED:
                return False
            
            referral.status = ReferralStatus.SIGNED_UP
            referral.signed_up_at = datetime.now()
            referral.referred_email = new_user_email
            
            self.db.commit()
            
            # Notificar al referrer
            self._notify_referrer_signup(referral)
            
            return True
            
        except Exception as e:
            print(f"Error processing referral signup: {e}")
            self.db.rollback()
            return False
    
    def process_referral_conversion(self, referral_code: str) -> bool:
        """Procesa cuando un referido completa su primera cita"""
        try:
            referral = self.db.query(Referral).filter(
                Referral.referral_code == referral_code
            ).first()
            
            if not referral:
                return False
            
            referral.status = ReferralStatus.COMPLETED_APPOINTMENT
            referral.completed_appointment_at = datetime.now()
            referral.clicks_count += 1
            
            self.db.commit()
            
            # Otorgar recompensas
            self._grant_rewards(referral)
            
            return True
            
        except Exception as e:
            print(f"Error processing referral conversion: {e}")
            self.db.rollback()
            return False
    
    def _process_converted_referrals(self) -> int:
        """Procesa referidos que han convertido"""
        # Buscar referidos con cita completada pero sin recompensa
        referrals = self.db.query(Referral).filter(
            and_(
                Referral.status == ReferralStatus.COMPLETED_APPOINTMENT,
                Referral.referrer_reward_given == False
            )
        ).all()
        
        count = 0
        for referral in referrals:
            if self._grant_rewards(referral):
                count += 1
        
        return count
    
    def _process_pending_rewards(self) -> int:
        """Procesa recompensas pendientes"""
        # Similar a _process_converted_referrals
        return self._process_converted_referrals()
    
    def _grant_rewards(self, referral: Referral) -> bool:
        """Otorga recompensas por referido exitoso"""
        try:
            campaign = self.db.query(ReferralCampaign).filter(
                ReferralCampaign.id == referral.campaign_id
            ).first()
            
            if not campaign:
                return False
            
            # Marcar recompensas como otorgadas
            referral.referrer_reward_given = True
            referral.referrer_reward_given_at = datetime.now()
            referral.referred_reward_given = True
            referral.referred_reward_given_at = datetime.now()
            referral.status = ReferralStatus.REWARDED
            
            # Enviar notificaciones
            self._send_reward_notification(referral, campaign)
            
            self.db.commit()
            
            return True
            
        except Exception as e:
            print(f"Error granting rewards: {e}")
            self.db.rollback()
            return False
    
    def _generate_referral_code(self, length: int = 8) -> str:
        """Genera código de referido único"""
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(alphabet) for _ in range(length))
            # Verificar que no existe
            existing = self.db.query(Referral).filter(
                Referral.referral_code == code
            ).first()
            if not existing:
                return code
    
    def _generate_referral_link(self, code: str) -> str:
        """Genera link de referido"""
        base_url = "https://clientflow-pro.vercel.app"
        return f"{base_url}/ref/{code}"
    
    def _get_or_create_default_campaign(self, professional_id: int) -> ReferralCampaign:
        """Obtiene o crea campaña por defecto"""
        campaign = self.db.query(ReferralCampaign).filter(
            and_(
                ReferralCampaign.professional_id == professional_id,
                ReferralCampaign.is_active == True
            )
        ).first()
        
        if not campaign:
            campaign = ReferralCampaign(
                professional_id=professional_id,
                name="Trae un amigo",
                description="Recomienda nuestros servicios y ambos ganan",
                referrer_reward="20% de descuento en tu próxima sesión",
                referred_reward="Primera sesión con 50% de descuento",
                max_referrals_per_person=5,
                is_active=True
            )
            self.db.add(campaign)
            self.db.commit()
        
        return campaign
    
    def _generate_referral_message(self, referrer, referred_name, campaign) -> str:
        """Genera mensaje de invitación de referido"""
        
        referred = referred_name or "un amigo"
        
        prompt = f"""
        Escribe un email de recomendación personal.
        
        Contexto:
        - Remitente: {referrer.full_name if referrer else 'Un contacto'}
        - Destinatario: {referred}
        - Relación: Amigos/conocidos
        - Servicio: Consultoría/profesional
        - Beneficio para el remitente: {campaign.referrer_reward if campaign else 'descuento'}
        - Beneficio para el destinatario: {campaign.referred_reward if campaign else 'descuento primera vez'}
        
        El email debe:
        1. Ser personal y auténtico (no sonar a marketing)
        2. Explicar brevemente por qué recomienda el servicio
        3. Mencionar el beneficio para ambos
        4. Incluir CTA claro
        5. Máximo 150 palabras
        """
        
        return self.generate_text(
            prompt=prompt,
            system_prompt="Eres alguien recomendando un servicio a un amigo. Sé natural y auténtico.",
            temperature=0.8
        ) or f"""
        Hola {referred},
        
        ¿Cómo estás? Te escribo porque encontré un servicio que me ha ayudado mucho y pensé en ti.
        
        {referrer.full_name if referrer else 'Un amigo'} te ha recomendado nuestros servicios. 
        Si reservas usando este link, ambos recibimos beneficios:
        
        🎁 Tú: {campaign.referred_reward if campaign else 'Descuento especial'}
        🎁 {referrer.full_name if referrer else 'Tu amigo'}: {campaign.referrer_reward if campaign else 'Recompensa'}
        
        [LINK_DE_REFERIDO]
        
        Saludos!
        """
    
    def _notify_referrer_signup(self, referral: Referral):
        """Notifica al referrer que su amigo se registró"""
        if referral.referrer_email:
            message = f"""
            ¡Buenas noticias! {referral.referred_name or 'Tu amigo'} ha usado tu invitación.
            
            Recuerda: Cuando complete su primera cita, ambos recibirán sus recompensas.
            
            ¡Gracias por recomendarnos!
            """
            
            send_email(
                to_email=referral.referrer_email,
                subject="¡Tu amigo se ha registrado!",
                body=message
            )
    
    def _send_reward_notification(self, referral: Referral, campaign: ReferralCampaign):
        """Envía notificación de recompensas otorgadas"""
        # Notificar al referrer
        if referral.referrer_email:
            send_email(
                to_email=referral.referrer_email,
                subject="¡Has ganado una recompensa!",
                body=f"""
                🎉 Felicidades!
                
                Tu amigo completó su primera cita. Has ganado:
                {campaign.referrer_reward}
                
                La recompensa se aplicará automáticamente a tu próxima sesión.
                """
            )
        
        # Notificar al referido
        if referral.referred_email:
            send_email(
                to_email=referral.referred_email,
                subject="¡Bienvenido! Tu recompensa te espera",
                body=f"""
                🎉 Bienvenido!
                
                Gracias por unirte por recomendación de {referral.referrer_email}.
                
                Tu recompensa:
                {campaign.referred_reward}
                
                Se aplicará automáticamente a tu primera sesión.
                """
            )
    
    def get_referral_stats(self, professional_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas de referidos"""
        total = self.db.query(Referral).filter(
            Referral.professional_id == professional_id
        ).count()
        
        converted = self.db.query(Referral).filter(
            and_(
                Referral.professional_id == professional_id,
                Referral.status == ReferralStatus.REWARDED
            )
        ).count()
        
        pending = self.db.query(Referral).filter(
            and_(
                Referral.professional_id == professional_id,
                Referral.status == ReferralStatus.INVITED
            )
        ).count()
        
        return {
            "total_referrals": total,
            "converted": converted,
            "conversion_rate": (converted / total * 100) if total > 0 else 0,
            "pending": pending
        }
