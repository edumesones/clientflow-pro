from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.auth import get_current_active_user, get_current_user
from app.schemas.schemas import UserResponse, UserUpdate, ProfessionalCreate, ProfessionalResponse, ProfessionalUpdate
from app.services.user_service import update_user, get_user_by_id
from app.services.professional_service import (
    create_professional, 
    get_professional_by_user_id,
    get_professional_by_id,
    update_professional
)
from app.models.models import User, UserRole

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de usuarios (solo admin)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un usuario específico"""
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar usuario"""
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = update_user(db, user_id, user_update)
    return user

# Perfil de Profesional

@router.post("/professional", response_model=ProfessionalResponse)
async def create_professional_profile(
    professional_data: ProfessionalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear perfil de profesional"""
    # Verificar que el usuario no tenga ya un perfil de profesional
    existing = get_professional_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Professional profile already exists"
        )
    
    professional_data.user_id = current_user.id
    professional = create_professional(db, professional_data)
    
    # Actualizar rol del usuario
    current_user.role = UserRole.PROFESSIONAL
    db.commit()
    
    return professional

@router.get("/professional/me", response_model=ProfessionalResponse)
async def get_my_professional_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener mi perfil de profesional"""
    professional = get_professional_by_user_id(db, current_user.id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional profile not found"
        )
    return professional

@router.put("/professional/{professional_id}", response_model=ProfessionalResponse)
async def update_professional_profile(
    professional_id: int,
    professional_update: ProfessionalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar perfil de profesional"""
    professional = get_professional_by_id(db, professional_id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    
    if professional.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated = update_professional(db, professional_id, professional_update)
    return updated
