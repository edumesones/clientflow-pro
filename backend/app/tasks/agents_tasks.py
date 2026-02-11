"""
Celery tasks for running AI Agents automatically
"""
from celery import shared_task
from app.core.database import SessionLocal
from app.agents import RemindyAgent, FollowupAgent, BriefAgent
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def run_remindy(self):
    """
    Task to run Remindy Agent (Anti No-Show)
    Runs every hour to check appointments and send reminders
    """
    db = SessionLocal()
    try:
        agent = RemindyAgent(db)
        result = agent.run()
        logger.info(f"RemindyAgent completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"RemindyAgent failed: {exc}")
        raise self.retry(exc=exc, countdown=300)  # Retry in 5 minutes
    finally:
        db.close()

@shared_task(bind=True, max_retries=3)
def run_followup(self):
    """
    Task to run Followup Agent (CRM Automation)
    Runs every 2 hours to process leads and send follow-ups
    """
    db = SessionLocal()
    try:
        agent = FollowupAgent(db)
        result = agent.run()
        logger.info(f"FollowupAgent completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"FollowupAgent failed: {exc}")
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()

@shared_task(bind=True, max_retries=3)
def run_brief(self):
    """
    Task to run Brief Agent (Pre-meeting Intelligence)
    Runs every 30 minutes to generate briefs for upcoming appointments
    """
    db = SessionLocal()
    try:
        agent = BriefAgent(db)
        result = agent.run()
        logger.info(f"BriefAgent completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"BriefAgent failed: {exc}")
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()

@shared_task
def process_new_lead(lead_id: int, sequence_type: str = "nurture_7"):
    """
    Task to process a new lead immediately
    Called when a new lead is created
    """
    db = SessionLocal()
    try:
        agent = FollowupAgent(db)
        success = agent.process_new_lead(lead_id, sequence_type)
        if success:
            logger.info(f"Lead {lead_id} processed successfully")
        else:
            logger.warning(f"Failed to process lead {lead_id}")
        return {"lead_id": lead_id, "success": success}
    except Exception as exc:
        logger.error(f"Error processing lead {lead_id}: {exc}")
        raise
    finally:
        db.close()

@shared_task
def generate_appointment_brief(appointment_id: int):
    """
    Task to generate a brief for a specific appointment
    Called 30 minutes before appointment or on demand
    """
    db = SessionLocal()
    try:
        agent = BriefAgent(db)
        brief = agent.generate_brief_for_appointment(appointment_id)
        if brief:
            logger.info(f"Brief generated for appointment {appointment_id}")
            return {"appointment_id": appointment_id, "brief_id": brief.id}
        else:
            logger.warning(f"Failed to generate brief for appointment {appointment_id}")
            return {"appointment_id": appointment_id, "brief_id": None}
    except Exception as exc:
        logger.error(f"Error generating brief for appointment {appointment_id}: {exc}")
        raise
    finally:
        db.close()

@shared_task
def run_all_agents():
    """
    Task to run all agents at once
    Useful for manual execution or testing
    """
    db = SessionLocal()
    results = {}
    try:
        # Run Remindy
        remindy = RemindyAgent(db)
        results["remindy"] = remindy.run()
        
        # Run Followup
        followup = FollowupAgent(db)
        results["followup"] = followup.run()
        
        # Run Brief
        brief = BriefAgent(db)
        results["brief"] = brief.run()
        
        logger.info(f"All agents completed: {results}")
        return results
    except Exception as exc:
        logger.error(f"Error running all agents: {exc}")
        raise
    finally:
        db.close()
