from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "sqlite:///./clientflow.db"
    
    # Seguridad
    SECRET_KEY: str = "tu-clave-secreta-muy-larga-y-segura-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # Email SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    SMTP_FROM_NAME: str = "ClientFlow Pro"
    SMTP_FROM_EMAIL: str = "noreply@clientflow.pro"
    
    # WhatsApp
    WHATSAPP_API_KEY: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = None
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: Optional[str] = None
    WHATSAPP_API_VERSION: str = "v17.0"
    
    # SMS
    SMS_PROVIDER: str = "twilio"
    SMS_API_KEY: Optional[str] = None
    SMS_API_SECRET: Optional[str] = None
    SMS_FROM_NUMBER: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Feature Flags
    ENABLE_WHATSAPP: bool = False
    ENABLE_SMS: bool = False
    ENABLE_EMAIL: bool = True
    ENABLE_AI_FEATURES: bool = False
    
    # Configuración de negocio
    DEFAULT_TIMEZONE: str = "America/Mexico_City"
    DEFAULT_APPOINTMENT_DURATION: int = 60
    REMINDER_24H_HOURS: int = 24
    REMINDER_1H_HOURS: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
