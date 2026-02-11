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
