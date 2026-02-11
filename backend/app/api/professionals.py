from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.schemas.schemas import ProfessionalResponse
from app.services.professional_service import get_professionals, get_professional_by_slug
from app.models.models import User, UserRole

router = APIRouter()

@router.get("/", response_model=List[ProfessionalResponse])
async def list_professionals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar todos los profesionales"""
    professionals = get_professionals(db, skip=skip, limit=limit)
    return professionals

@router.get("/{slug}", response_model=ProfessionalResponse)
async def get_professional_by_slug_endpoint(
    slug: str,
    db: Session = Depends(get_db)
):
    """Obtener profesional por slug (público)"""
    professional = get_professional_by_slug(db, slug)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    return professional
