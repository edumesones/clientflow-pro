from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date, time
from enum import Enum

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    PROFESSIONAL = "professional"
    CLIENT = "client"

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    FOLLOWED_UP = "followed_up"
    CONVERTED = "converted"
    LOST = "lost"

# ========== USER SCHEMAS ==========

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.CLIENT

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== AUTH SCHEMAS ==========

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ========== PROFESSIONAL SCHEMAS ==========

class ProfessionalBase(BaseModel):
    slug: str = Field(..., min_length=3, max_length=100)
    bio: Optional[str] = None
    specialty: Optional[str] = Field(None, max_length=255)
    timezone: str = "America/Mexico_City"
    appointment_duration: int = 60
    buffer_time: int = 15
    advance_booking_days: int = 30
    is_accepting_appointments: bool = True

class ProfessionalCreate(ProfessionalBase):
    user_id: int

class ProfessionalUpdate(BaseModel):
    slug: Optional[str] = Field(None, min_length=3, max_length=100)
    bio: Optional[str] = None
    specialty: Optional[str] = None
    timezone: Optional[str] = None
    appointment_duration: Optional[int] = None
    buffer_time: Optional[int] = None
    advance_booking_days: Optional[int] = None
    is_accepting_appointments: Optional[bool] = None

class ProfessionalResponse(ProfessionalBase):
    id: int
    user_id: int
    created_at: datetime
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

# ========== AVAILABILITY SCHEMAS ==========

class AvailabilitySlotBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time
    is_active: bool = True

class AvailabilitySlotCreate(AvailabilitySlotBase):
    professional_id: int

class AvailabilitySlotResponse(AvailabilitySlotBase):
    id: int
    professional_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AvailabilitySchedule(BaseModel):
    professional_id: int
    slots: List[AvailabilitySlotCreate]

# ========== APPOINTMENT SCHEMAS ==========

class AppointmentBase(BaseModel):
    appointment_date: date
    start_time: time
    service_type: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    price: Optional[float] = None

class AppointmentCreate(AppointmentBase):
    professional_id: int
    client_id: Optional[int] = None
    lead_name: Optional[str] = None
    lead_email: Optional[EmailStr] = None
    lead_phone: Optional[str] = None

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    appointment_date: Optional[date] = None
    start_time: Optional[time] = None

class AppointmentResponse(AppointmentBase):
    id: int
    professional_id: int
    client_id: Optional[int]
    lead_name: Optional[str]
    lead_email: Optional[str]
    lead_phone: Optional[str]
    end_time: time
    status: AppointmentStatus
    reminder_24h_sent: bool
    reminder_1h_sent: bool
    review_requested: bool
    created_at: datetime
    professional: Optional[ProfessionalResponse] = None
    client: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

# ========== LEAD SCHEMAS ==========

class LeadBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=255)
    message: Optional[str] = None
    professional_id: int

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None

class LeadResponse(LeadBase):
    id: int
    user_id: Optional[int]
    status: LeadStatus
    first_contact_date: Optional[datetime]
    last_contact_date: Optional[datetime]
    follow_up_1_sent: bool
    follow_up_1_date: Optional[datetime]
    follow_up_3_sent: bool
    follow_up_3_date: Optional[datetime]
    follow_up_7_sent: bool
    follow_up_7_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    professional: Optional[ProfessionalResponse] = None
    
    class Config:
        from_attributes = True

# ========== DASHBOARD SCHEMAS ==========

class DashboardStats(BaseModel):
    total_leads: int
    new_leads_today: int
    total_appointments: int
    upcoming_appointments: int
    conversion_rate: float
    no_show_rate: float
    revenue_this_month: float
    revenue_last_month: float

class UpcomingAppointment(BaseModel):
    id: int
    client_name: str
    client_email: Optional[str]
    client_phone: Optional[str]
    appointment_date: date
    start_time: time
    service_type: Optional[str]
    status: str

class RecentLead(BaseModel):
    id: int
    name: str
    email: Optional[str]
    status: str
    created_at: datetime

class DashboardData(BaseModel):
    stats: DashboardStats
    upcoming_appointments: List[UpcomingAppointment]
    recent_leads: List[RecentLead]

# ========== PUBLIC BOOKING SCHEMAS ==========

class PublicProfessional(BaseModel):
    id: int
    slug: str
    full_name: str
    bio: Optional[str]
    specialty: Optional[str]
    appointment_duration: int

class AvailableSlot(BaseModel):
    date: date
    time: time
    available: bool

class PublicBookingRequest(BaseModel):
    professional_slug: str
    appointment_date: date
    start_time: time
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    service_type: Optional[str] = None
    notes: Optional[str] = None

class PublicBookingResponse(BaseModel):
    success: bool
    message: str
    appointment_id: Optional[int] = None
