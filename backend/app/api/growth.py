"""
API endpoints para el Módulo Growth (Marketing Automático)
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.core.database import get_db
from app.agents import ContentAgent, ReviewAgent, ReferralAgent
from app.models.models import (
    GeneratedContent, ContentStrategy, ReviewRequest,
    Referral, ReferralCampaign
)

router = APIRouter()

# ============================================================================
# CONTENT AGENT ENDPOINTS
# ============================================================================

@router.post("/content/generate/{professional_id}", tags=["Growth"])
async def generate_content(
    professional_id: int,
    platform: str = "instagram",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Genera contenido para redes sociales"""
    agent = ContentAgent(db)
    content = agent.generate_content_for_professional(professional_id, platform)
    
    if content:
        return {
            "status": "success",
            "content_id": content.id,
            "title": content.title,
            "platform": content.platform,
            "engagement_score": content.predicted_engagement_score
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to generate content")

@router.get("/content/calendar/{professional_id}", tags=["Growth"])
async def get_content_calendar(
    professional_id: int,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Obtiene calendario de contenido"""
    agent = ContentAgent(db)
    return agent.get_content_calendar(professional_id)

@router.post("/content/run", tags=["Growth"])
async def run_content_agent(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ejecuta agente Content manualmente"""
    def run():
        agent = ContentAgent(db)
        return agent.run()
    
    background_tasks.add_task(run)
    return {"status": "running", "agent": "content"}

# ============================================================================
# REVIEW AGENT ENDPOINTS
# ============================================================================

@router.post("/review/request/{appointment_id}", tags=["Growth"])
async def request_review(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Solicita review para una cita específica"""
    agent = ReviewAgent(db)
    success = agent.request_review_for_appointment(appointment_id)
    
    if success:
        return {
            "status": "success",
            "message": f"Review requested for appointment {appointment_id}"
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to request review")

@router.post("/review/submit/{review_request_id}", tags=["Growth"])
async def submit_review(
    review_request_id: int,
    rating: int,
    review_text: str,
    client_name: str = None,
    db: Session = Depends(get_db)
):
    """Procesa una review enviada por cliente"""
    agent = ReviewAgent(db)
    success = agent.submit_review(review_request_id, rating, review_text, client_name)
    
    if success:
        return {
            "status": "success",
            "message": "Review submitted and published"
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to submit review")

@router.get("/review/public/{professional_id}", tags=["Growth"])
async def get_public_reviews(
    professional_id: int,
    featured_only: bool = False,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Obtiene reviews públicas de un profesional"""
    agent = ReviewAgent(db)
    return agent.get_public_reviews(professional_id, featured_only)

@router.post("/review/run", tags=["Growth"])
async def run_review_agent(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ejecuta agente Review manualmente"""
    def run():
        agent = ReviewAgent(db)
        return agent.run()
    
    background_tasks.add_task(run)
    return {"status": "running", "agent": "review"}

# ============================================================================
# REFERRAL AGENT ENDPOINTS
# ============================================================================

@router.post("/referral/invite", tags=["Growth"])
async def create_referral(
    referrer_id: int,
    referred_email: str,
    referred_name: str = None,
    db: Session = Depends(get_db)
):
    """Crea invitación de referido"""
    agent = ReferralAgent(db)
    referral = agent.create_referral_invitation(
        referrer_id=referrer_id,
        referred_email=referred_email,
        referred_name=referred_name
    )
    
    if referral:
        return {
            "status": "success",
            "referral_id": referral.id,
            "referral_code": referral.referral_code,
            "referral_link": referral.referral_link
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to create referral")

@router.get("/referral/stats/{professional_id}", tags=["Growth"])
async def get_referral_stats(
    professional_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Obtiene estadísticas de referidos"""
    agent = ReferralAgent(db)
    return agent.get_referral_stats(professional_id)

@router.post("/referral/campaign", tags=["Growth"])
async def create_campaign(
    professional_id: int,
    name: str,
    referrer_reward: str,
    referred_reward: str,
    db: Session = Depends(get_db)
):
    """Crea campaña de referidos"""
    campaign = ReferralCampaign(
        professional_id=professional_id,
        name=name,
        referrer_reward=referrer_reward,
        referred_reward=referred_reward,
        is_active=True
    )
    
    db.add(campaign)
    db.commit()
    
    return {
        "status": "success",
        "campaign_id": campaign.id,
        "name": campaign.name
    }

@router.post("/referral/run", tags=["Growth"])
async def run_referral_agent(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ejecuta agente Referral manualmente"""
    def run():
        agent = ReferralAgent(db)
        return agent.run()
    
    background_tasks.add_task(run)
    return {"status": "running", "agent": "referral"}

# ============================================================================
# GROWTH MODULE - ALL AGENTS
# ============================================================================

@router.post("/run-all", tags=["Growth"])
async def run_all_growth_agents(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ejecuta todos los agentes de Growth"""
    def run():
        from app.tasks.agents_tasks import run_all_growth_agents
        return run_all_growth_agents()
    
    background_tasks.add_task(run)
    return {"status": "running", "agents": ["content", "review", "referral"]}

@router.get("/dashboard/{professional_id}", tags=["Growth"])
async def get_growth_dashboard(
    professional_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Obtiene métricas completas del módulo Growth"""
    
    # Content stats
    content_count = db.query(GeneratedContent).filter(
        GeneratedContent.professional_id == professional_id
    ).count()
    
    # Review stats
    review_count = db.query(ReviewRequest).filter(
        ReviewRequest.professional_id == professional_id
    ).count()
    
    # Referral stats
    referral_agent = ReferralAgent(db)
    referral_stats = referral_agent.get_referral_stats(professional_id)
    
    return {
        "professional_id": professional_id,
        "content": {
            "total_generated": content_count,
            "status": "active"
        },
        "reviews": {
            "total_requested": review_count,
            "status": "active"
        },
        "referrals": referral_stats,
        "agents_status": {
            "content": "scheduled_daily",
            "review": "scheduled_daily",
            "referral": "scheduled_daily"
        }
    }
