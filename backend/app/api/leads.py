from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.schemas.schemas import LeadCreate, LeadResponse, LeadUpdate, LeadStatus
from app.services.lead_service import (
    create_lead,
    get_lead_by_id,
    get_leads_by_professional,
    get_recent_leads,
    update_lead,
    mark_lead_contacted
)
from app.services.professional_service import get_professional_by_user_id
from app.models.models import User, UserRole

router = APIRouter()

@router.get("/", response_model=List[LeadResponse])
async def list_leads(
    status: Optional[LeadStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar leads"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can access leads"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    
    leads = get_leads_by_professional(db, professional.id, status, skip, limit)
    return leads

@router.get("/recent", response_model=List[LeadResponse])
async def get_recent(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener leads recientes"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can access leads"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    
    leads = get_recent_leads(db, professional.id, limit)
    return leads

@router.post("/", response_model=LeadResponse)
async def create_lead_endpoint(
    lead_data: LeadCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo lead (público)"""
    lead = create_lead(db, lead_data)
    return lead

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener detalle de un lead"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can access leads"
        )
    
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if professional and lead.professional_id != professional.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return lead

@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead_endpoint(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar lead"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can update leads"
        )
    
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if professional and lead.professional_id != professional.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated = update_lead(db, lead_id, lead_update)
    return updated

@router.post("/{lead_id}/contact")
async def mark_lead_as_contacted(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Marcar lead como contactado"""
    if current_user.role != UserRole.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professionals can update leads"
        )
    
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    professional = get_professional_by_user_id(db, current_user.id)
    if professional and lead.professional_id != professional.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    mark_lead_contacted(db, lead_id)
    return {"message": "Lead marked as contacted"}
