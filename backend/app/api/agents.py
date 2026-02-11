"""
API endpoints para los Agentes Inteligentes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.agents import RemindyAgent, FollowupAgent, BriefAgent
from app.models.models import AppointmentBrief, Lead

router = APIRouter()

@router.post("/run-all", tags=["Agentes"])
async def run_all_agents(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Ejecuta todos los agentes en segundo plano.
    Útil para pruebas o ejecución manual.
    """
    def run_agents():
        # Remindy
        remindy = RemindyAgent(db)
        remindy.run()
        
        # Followup
        followup = FollowupAgent(db)
        followup.run()
        
        # Brief
        brief = BriefAgent(db)
        brief.run()
    
    background_tasks.add_task(run_agents)
    
    return {
        "status": "running",
        "message": "All agents started in background"
    }

@router.post("/remindy/run", tags=["Agentes"])
async def run_remindy(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ejecuta agente Remindy (anti no-show)"""
    def run():
        agent = RemindyAgent(db)
        return agent.run()
    
    background_tasks.add_task(run)
    return {"status": "running", "agent": "remindy"}

@router.post("/followup/process-lead/{lead_id}", tags=["Agentes"])
async def process_lead(
    lead_id: int,
    sequence_type: str = "nurture_7",
    db: Session = Depends(get_db)
):
    """Procesa un lead nuevo con el agente Followup"""
    agent = FollowupAgent(db)
    success = agent.process_new_lead(lead_id, sequence_type)
    
    if success:
        return {
            "status": "success",
            "message": f"Lead {lead_id} processed with sequence {sequence_type}"
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to process lead")

@router.post("/followup/run", tags=["Agentes"])
async def run_followup(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ejecuta agente Followup (CRM automático)"""
    def run():
        agent = FollowupAgent(db)
        return agent.run()
    
    background_tasks.add_task(run)
    return {"status": "running", "agent": "followup"}

@router.post("/brief/generate/{appointment_id}", tags=["Agentes"])
async def generate_brief(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Genera brief para una cita específica"""
    agent = BriefAgent(db)
    brief = agent.generate_brief_for_appointment(appointment_id)
    
    if brief:
        return {
            "status": "success",
            "brief_id": brief.id,
            "message": "Brief generated successfully"
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to generate brief")

@router.get("/brief/{appointment_id}", tags=["Agentes"])
async def get_brief(
    appointment_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Obtiene el brief de una cita"""
    agent = BriefAgent(db)
    brief_data = agent.get_brief_for_dashboard(appointment_id)
    
    if "error" in brief_data:
        raise HTTPException(status_code=404, detail=brief_data["error"])
    
    return brief_data

@router.post("/brief/run", tags=["Agentes"])
async def run_brief(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ejecuta agente Brief (inteligencia pre-cita)"""
    def run():
        agent = BriefAgent(db)
        return agent.run()
    
    background_tasks.add_task(run)
    return {"status": "running", "agent": "brief"}

@router.get("/hot-leads", tags=["Agentes"])
async def get_hot_leads(
    db: Session = Depends(get_db)
):
    """Obtiene leads que necesitan atención humana"""
    # Leads con urgencia alta o múltiples respuestas
    from sqlalchemy import func
    from app.models.models import FollowupAction, FollowupStatus, LeadInsight
    
    hot_leads = db.query(Lead).join(LeadInsight).filter(
        Lead.status.in_(["new", "contacted"]),
        LeadInsight.urgency_level >= 8
    ).all()
    
    return {
        "count": len(hot_leads),
        "leads": [
            {
                "id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "urgency": db.query(LeadInsight).filter(
                    LeadInsight.lead_id == lead.id
                ).first().urgency_level if db.query(LeadInsight).filter(
                    LeadInsight.lead_id == lead.id
                ).first() else 5
            }
            for lead in hot_leads
        ]
    }

@router.get("/no-show-risk/{client_id}", tags=["Agentes"])
async def get_no_show_risk(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene el riesgo de no-show de un cliente"""
    from app.models.models import NoShowPattern
    
    pattern = db.query(NoShowPattern).filter(
        NoShowPattern.client_id == client_id
    ).first()
    
    if not pattern:
        return {
            "client_id": client_id,
            "risk_score": 0,
            "reliability_score": 100,
            "message": "No data available"
        }
    
    return {
        "client_id": client_id,
        "risk_score": 100 - pattern.reliability_score,
        "reliability_score": pattern.reliability_score,
        "total_appointments": pattern.total_appointments,
        "no_shows": pattern.no_shows,
        "message": "Low risk" if pattern.reliability_score >= 80 else "Medium risk" if pattern.reliability_score >= 50 else "High risk"
    }
