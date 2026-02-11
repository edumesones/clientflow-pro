"""
Clase base para todos los agentes de ClientFlow Pro
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
import openai

class BaseAgent(ABC):
    """Clase base para todos los agentes inteligentes"""
    
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """Genera texto usando OpenAI"""
        if not settings.OPENAI_API_KEY:
            return ""
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = openai.chat.completions.create(
                model=settings.OPENAI_MODEL or "gpt-4",
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating text: {e}")
            return ""
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Método principal que ejecuta el agente"""
        pass
