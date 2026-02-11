"""
Agentes Inteligentes para ClientFlow Pro

Este paquete contiene los agentes de IA que automatizan tareas clave:

Módulo Core:
- Remindy: Sistema anti no-show
- Followup: CRM con seguimiento automático
- Brief: Inteligencia pre-cita

Módulo Growth:
- ContentAgent: Generador de contenido para redes sociales
- ReviewAgent: Gestión automática de reviews
- ReferralAgent: Programa de referidos automatizado
"""

from .remindy import RemindyAgent
from .followup import FollowupAgent
from .brief import BriefAgent
from .content_agent import ContentAgent
from .review_agent import ReviewAgent
from .referral_agent import ReferralAgent

__all__ = [
    "RemindyAgent", 
    "FollowupAgent", 
    "BriefAgent",
    "ContentAgent",
    "ReviewAgent",
    "ReferralAgent"
]
