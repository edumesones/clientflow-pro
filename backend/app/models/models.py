from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Float, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PROFESSIONAL = "professional"
    CLIENT = "client"

class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    FOLLOWED_UP = "followed_up"
    CONVERTED = "converted"
    LOST = "lost"

class ReminderStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50))
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    professional_profile = relationship("Professional", back_populates="user", uselist=False)
    client_appointments = relationship("Appointment", foreign_keys="Appointment.client_id", back_populates="client")
    leads = relationship("Lead", back_populates="user")

class Professional(Base):
    __tablename__ = "professionals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    slug = Column(String(100), unique=True, index=True)
    bio = Column(Text)
    specialty = Column(String(255))
    timezone = Column(String(50), default="America/Mexico_City")
    appointment_duration = Column(Integer, default=60)  # minutos
    buffer_time = Column(Integer, default=15)  # minutos entre citas
    advance_booking_days = Column(Integer, default=30)
    is_accepting_appointments = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="professional_profile")
    availability_slots = relationship("AvailabilitySlot", back_populates="professional")
    appointments = relationship("Appointment", back_populates="professional")

class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    day_of_week = Column(Integer)  # 0=Lunes, 6=Domingo
    start_time = Column(Time)
    end_time = Column(Time)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    professional = relationship("Professional", back_populates="availability_slots")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    client_id = Column(Integer, ForeignKey("users.id"))
    
    # Si es un lead que aún no es cliente
    lead_name = Column(String(255))
    lead_email = Column(String(255))
    lead_phone = Column(String(50))
    
    appointment_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    notes = Column(Text)
    service_type = Column(String(255))
    price = Column(Float)
    
    # Recordatorios
    reminder_24h_sent = Column(Boolean, default=False)
    reminder_1h_sent = Column(Boolean, default=False)
    review_requested = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    professional = relationship("Professional", back_populates="appointments")
    client = relationship("User", foreign_keys=[client_id], back_populates="client_appointments")
    reminders = relationship("Reminder", back_populates="appointment")
    
    # Relaciones con agentes inteligentes
    confirmation = relationship("AppointmentConfirmation", foreign_keys="AppointmentConfirmation.appointment_id", back_populates="appointment", uselist=False)
    brief = relationship("AppointmentBrief", back_populates="appointment", uselist=False)

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    source = Column(String(255))  # web, referral, social, etc.
    message = Column(Text)
    
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    
    # Seguimiento automático
    first_contact_date = Column(DateTime(timezone=True))
    last_contact_date = Column(DateTime(timezone=True))
    follow_up_1_sent = Column(Boolean, default=False)
    follow_up_1_date = Column(DateTime(timezone=True))
    follow_up_3_sent = Column(Boolean, default=False)
    follow_up_3_date = Column(DateTime(timezone=True))
    follow_up_7_sent = Column(Boolean, default=False)
    follow_up_7_date = Column(DateTime(timezone=True))
    
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="leads")
    professional = relationship("Professional")
    
    # Relaciones con agentes inteligentes
    followup_sequences = relationship("FollowupSequence", back_populates="lead")
    followup_actions = relationship("FollowupAction", back_populates="lead")
    insights = relationship("LeadInsight", back_populates="lead")

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    reminder_type = Column(String(50))  # 24h, 1h, post_appointment
    channel = Column(String(50))  # email, whatsapp, sms
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    status = Column(Enum(ReminderStatus), default=ReminderStatus.SCHEDULED)
    error_message = Column(Text)
    
    appointment = relationship("Appointment", back_populates="reminders")

class ClientNote(Base):
    __tablename__ = "client_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    client_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    next_steps = Column(Text)
    follow_up_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class StatsDaily(Base):
    __tablename__ = "stats_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    date = Column(Date)
    
    new_leads = Column(Integer, default=0)
    converted_leads = Column(Integer, default=0)
    appointments_booked = Column(Integer, default=0)
    appointments_completed = Column(Integer, default=0)
    appointments_cancelled = Column(Integer, default=0)
    no_shows = Column(Integer, default=0)
    revenue = Column(Float, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# AGENTES INTELIGENTES - NUEVAS TABLAS
# ============================================================================

class ConfirmationStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DECLINED = "declined"
    NO_RESPONSE = "no_response"

class FollowupStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    OPENED = "opened"
    REPLIED = "replied"
    CONVERTED = "converted"
    FAILED = "failed"

class BriefStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATED = "generated"
    DELIVERED = "delivered"
    VIEWED = "viewed"

# AGENTE 1: ANTI NO-SHOW (Remindy)
class AppointmentConfirmation(Base):
    """Seguimiento de confirmaciones de citas (Agente Remindy)"""
    __tablename__ = "appointment_confirmations"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), unique=True)
    
    # Estado de confirmación
    status = Column(Enum(ConfirmationStatus), default=ConfirmationStatus.PENDING)
    
    # Recordatorios enviados
    reminder_24h_sent = Column(DateTime(timezone=True))
    reminder_1h_sent = Column(DateTime(timezone=True))
    
    # Respuesta del cliente
    client_response = Column(Text)  # "Sí, confirmo", "No puedo", etc.
    responded_at = Column(DateTime(timezone=True))
    
    # Acción automática tomada
    auto_rescheduled = Column(Boolean, default=False)
    original_appointment_id = Column(Integer, ForeignKey("appointments.id"))
    
    # Métricas
    no_show_risk_score = Column(Integer, default=0)  # 0-100
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    appointment = relationship("Appointment", foreign_keys=[appointment_id], back_populates="confirmation")

class NoShowPattern(Base):
    """Patrones de no-show por cliente (para predicción)"""
    __tablename__ = "noshow_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    
    total_appointments = Column(Integer, default=0)
    no_shows = Column(Integer, default=0)
    cancellations = Column(Integer, default=0)
    late_reschedules = Column(Integer, default=0)
    
    # Score calculado
    reliability_score = Column(Integer, default=100)  # 0-100, menor = más riesgo
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

# AGENTE 2: CRM FOLLOWUP AUTOMÁTICO (Followup)
class FollowupSequence(Base):
    """Secuencias de follow-up automático (Agente Followup)"""
    __tablename__ = "followup_sequences"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    
    # Configuración de la secuencia
    sequence_name = Column(String(100))  # "Nurture 7 días", "Cierre rápido", etc.
    is_active = Column(Boolean, default=True)
    
    # Paso actual
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=3)
    
    # Estado general
    status = Column(Enum(FollowupStatus), default=FollowupStatus.SCHEDULED)
    
    # Resultado
    converted_to_appointment = Column(Boolean, default=False)
    converted_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    lead = relationship("Lead", back_populates="followup_sequences")
    actions = relationship("FollowupAction", back_populates="sequence")

class FollowupAction(Base):
    """Acciones individuales de follow-up ejecutadas"""
    __tablename__ = "followup_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    sequence_id = Column(Integer, ForeignKey("followup_sequences.id"))
    lead_id = Column(Integer, ForeignKey("leads.id"))
    
    # Paso en la secuencia
    step_number = Column(Integer)
    
    # Contenido generado por IA
    channel = Column(String(50))  # email, whatsapp
    subject = Column(String(255))
    content = Column(Text)  # Mensaje generado por OpenAI
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    
    # Engagement
    opened_at = Column(DateTime(timezone=True))
    replied_at = Column(DateTime(timezone=True))
    client_reply = Column(Text)
    
    # Estado
    status = Column(Enum(FollowupStatus), default=FollowupStatus.SCHEDULED)
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    sequence = relationship("FollowupSequence", back_populates="actions")
    lead = relationship("Lead", back_populates="followup_actions")

class LeadInsight(Base):
    """Insights automáticos sobre leads (generados por IA)"""
    __tablename__ = "lead_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    
    # Análisis de sentimiento
    sentiment = Column(String(50))  # positive, neutral, negative
    urgency_level = Column(Integer, default=5)  # 1-10
    
    # Insights
    key_pain_points = Column(Text)  # JSON array
    budget_indication = Column(String(50))  # low, medium, high
    decision_timeline = Column(String(50))  # immediate, short, medium, long
    
    # Recomendación
    recommended_approach = Column(Text)
    best_contact_time = Column(String(50))
    
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    lead = relationship("Lead", back_populates="insights")

# AGENTE 3: INTELIGENCIA PRE-CITA (Brief)
class AppointmentBrief(Base):
    """Briefings generados antes de cada cita (Agente Brief)"""
    __tablename__ = "appointment_briefs"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), unique=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    client_id = Column(Integer, ForeignKey("users.id"))
    
    # Estado
    status = Column(Enum(BriefStatus), default=BriefStatus.PENDING)
    
    # Contenido generado por IA
    executive_summary = Column(Text)  # Resumen ejecutivo
    
    # Historial contextual
    previous_interactions = Column(Text)  # JSON: fechas y temas
    previous_appointments_summary = Column(Text)
    
    # Temas pendientes
    open_topics = Column(Text)  # JSON array
    follow_up_items = Column(Text)  # JSON array
    
    # Insights del cliente
    client_preferences = Column(Text)  # JSON
    communication_style = Column(String(50))  # formal, casual, direct
    
    # Preparación sugerida
    suggested_questions = Column(Text)  # JSON array
    materials_to_prepare = Column(Text)  # JSON array
    
    # Engagement
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    viewed_at = Column(DateTime(timezone=True))
    
    appointment = relationship("Appointment", back_populates="brief")
    
    # Relaciones adicionales
    professional = relationship("Professional")
    client = relationship("User")

class ClientInsight(Base):
    """Perfil acumulado de insights del cliente"""
    __tablename__ = "client_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    
    # Perfil comportamental
    communication_preferences = Column(Text)  # JSON
    decision_making_style = Column(String(100))
    
    # Historial de interacciones
    total_appointments = Column(Integer, default=0)
    total_emails_exchanged = Column(Integer, default=0)
    
    # Temas recurrentes
    common_topics = Column(Text)  # JSON array
    pain_points_history = Column(Text)  # JSON array
    
    # Preferencias
    preferred_contact_method = Column(String(50))
    preferred_appointment_times = Column(Text)  # JSON
    
    # Insights de IA
    personality_notes = Column(Text)
    buying_signals = Column(Text)  # JSON array
    objections_history = Column(Text)  # JSON array
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# MÓDULO GROWTH - AGENTES DE MARKETING AUTOMÁTICO
# ============================================================================

class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class ReviewStatus(str, enum.Enum):
    REQUESTED = "requested"
    RECEIVED = "received"
    PUBLISHED = "published"
    REWARDED = "rewarded"

class ReferralStatus(str, enum.Enum):
    INVITED = "invited"
    CLICKED = "clicked"
    SIGNED_UP = "signed_up"
    COMPLETED_APPOINTMENT = "completed_appointment"
    REWARDED = "rewarded"

# AGENTE GROWTH 1: ContentGenerator
class GeneratedContent(Base):
    """Contenido generado automáticamente para redes sociales"""
    __tablename__ = "generated_content"
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    
    # Plataforma y formato
    platform = Column(String(50))  # instagram, linkedin, twitter
    content_type = Column(String(50))  # post, story, carousel, reel_script
    
    # Contenido generado por IA
    title = Column(String(255))
    content = Column(Text)  # Texto completo del post
    hashtags = Column(Text)  # JSON array
    cta_text = Column(String(255))  # Call to action específico
    link_to_include = Column(String(500))  # Link de reserva
    
    # Estado
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    
    # Engagement estimado por IA
    predicted_engagement_score = Column(Integer, default=5)  # 1-10
    target_audience = Column(String(255))  # Descripción del público objetivo
    
    # Métricas reales (si se publica)
    actual_likes = Column(Integer, default=0)
    actual_comments = Column(Integer, default=0)
    actual_clicks = Column(Integer, default=0)  # Clicks al link de reserva
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ContentStrategy(Base):
    """Estrategia de contenido del profesional"""
    __tablename__ = "content_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"), unique=True)
    
    # Configuración
    tone_of_voice = Column(String(50), default="professional")  # professional, casual, inspirational
    posting_frequency = Column(Integer, default=3)  # posts por semana
    preferred_platforms = Column(Text)  # JSON: ["instagram", "linkedin"]
    
    # Temas y pilares de contenido
    content_pillars = Column(Text)  # JSON: ["tips", "case_studies", "behind_scenes"]
    target_audience_description = Column(Text)
    
    # Links
    booking_link = Column(String(500))
    website_link = Column(String(500))
    
    # Horarios óptimos (aprendidos por IA)
    optimal_posting_times = Column(Text)  # JSON: {"instagram": "14:00", "linkedin": "09:00"}
    
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# AGENTE GROWTH 2: ReviewBooster
class ReviewRequest(Base):
    """Solicitudes de review automáticas"""
    __tablename__ = "review_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    client_id = Column(Integer, ForeignKey("users.id"))
    
    # Estado
    status = Column(Enum(ReviewStatus), default=ReviewStatus.REQUESTED)
    
    # Contenido
    request_message = Column(Text)  # Mensaje personalizado enviado
    sent_at = Column(DateTime(timezone=True))
    
    # Respuesta del cliente
    client_rating = Column(Integer)  # 1-5 estrellas
    client_review_text = Column(Text)
    received_at = Column(DateTime(timezone=True))
    
    # Publicación
    published_on_website = Column(Boolean, default=False)
    published_on_google = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True))
    
    # Recompensa (opcional)
    reward_given = Column(Boolean, default=False)
    reward_type = Column(String(50))  # discount, free_session, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PublicReview(Base):
    """Reviews publicadas en página pública del profesional"""
    __tablename__ = "public_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    review_request_id = Column(Integer, ForeignKey("review_requests.id"))
    
    # Contenido publicado
    client_name = Column(String(255))  # Puede ser "Carlos R." para privacidad
    client_photo_url = Column(String(500))
    rating = Column(Integer)
    review_text = Column(Text)
    service_received = Column(String(255))
    
    # SEO y display
    keywords = Column(Text)  # JSON: para SEO
    is_featured = Column(Boolean, default=False)  # Mostrar en homepage
    display_order = Column(Integer, default=0)
    
    # Métricas
    views_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    
    published_at = Column(DateTime(timezone=True), server_default=func.now())

# AGENTE GROWTH 3: ReferralEngine
class ReferralCampaign(Base):
    """Campañas de referidos"""
    __tablename__ = "referral_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    
    # Configuración
    name = Column(String(255))  # "Trae un amigo", "Doble recompensa", etc.
    description = Column(Text)
    
    # Recompensas
    referrer_reward = Column(String(255))  # "20% descuento próxima sesión"
    referred_reward = Column(String(255))  # "Primera sesión gratis"
    
    # Límites
    max_referrals_per_person = Column(Integer, default=5)
    campaign_starts_at = Column(DateTime(timezone=True))
    campaign_ends_at = Column(DateTime(timezone=True))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Referral(Base):
    """Tracking individual de referidos"""
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("referral_campaigns.id"))
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    
    # Quién refiere
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referrer_email = Column(String(255))
    
    # Quien es referido
    referred_email = Column(String(255))
    referred_name = Column(String(255))
    
    # Tracking
    referral_code = Column(String(50), unique=True, index=True)
    referral_link = Column(String(500))
    
    # Estado del funnel
    status = Column(Enum(ReferralStatus), default=ReferralStatus.INVITED)
    
    # Timestamps del funnel
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    clicked_at = Column(DateTime(timezone=True))
    signed_up_at = Column(DateTime(timezone=True))
    completed_appointment_at = Column(DateTime(timezone=True))
    
    # Recompensas
    referrer_reward_given = Column(Boolean, default=False)
    referrer_reward_given_at = Column(DateTime(timezone=True))
    referred_reward_given = Column(Boolean, default=False)
    referred_reward_given_at = Column(DateTime(timezone=True))
    
    # Métricas
    clicks_count = Column(Integer, default=0)

class ReferralInvitation(Base):
    """Invitaciones específicas enviadas"""
    __tablename__ = "referral_invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    referral_id = Column(Integer, ForeignKey("referrals.id"))
    
    # Contenido generado por IA
    invitation_message = Column(Text)
    personalization_notes = Column(Text)  # Por qué IA pensó que este amigo encaja
    
    # Envío
    channel = Column(String(50))  # email, whatsapp
    sent_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    
    # Respuesta
    recipient_replied = Column(Boolean, default=False)
    recipient_reply = Column(Text)

# Métricas de Growth
class GrowthMetrics(Base):
    """Métricas acumuladas del módulo growth"""
    __tablename__ = "growth_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    date = Column(Date)
    
    # Contenido
    posts_generated = Column(Integer, default=0)
    posts_published = Column(Integer, default=0)
    clicks_from_content = Column(Integer, default=0)
    
    # Reviews
    reviews_requested = Column(Integer, default=0)
    reviews_received = Column(Integer, default=0)
    average_rating = Column(Float, default=0)
    
    # Referidos
    referrals_sent = Column(Integer, default=0)
    referrals_converted = Column(Integer, default=0)
    revenue_from_referrals = Column(Float, default=0)
    
    # Totales
    new_leads_from_content = Column(Integer, default=0)
    new_leads_from_reviews = Column(Integer, default=0)
    new_leads_from_referrals = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
