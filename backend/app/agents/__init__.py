"""
Agentes Inteligentes para ClientFlow Pro

Este paquete contiene los agentes de IA que automatizan tareas clave:
- Remindy: Sistema anti no-show
- Followup: CRM con seguimiento automático
- Brief: Inteligencia pre-cita
"""

from .remindy import RemindyAgent
from .followup import FollowupAgent
from .brief import BriefAgent

__all__ = ["RemindyAgent", "FollowupAgent", "BriefAgent"]
