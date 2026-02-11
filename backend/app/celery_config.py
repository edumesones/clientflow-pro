"""
Celery configuration for ClientFlow Pro
"""
import os
from celery import Celery
from celery.schedules import crontab

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "clientflow",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.agents_tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=os.getenv("DEFAULT_TIMEZONE", "America/Mexico_City"),
    enable_utc=True,
    beat_schedule={
        # CORE MODULE
        # Remindy: Check appointments every hour
        "remindy-every-hour": {
            "task": "app.tasks.agents_tasks.run_remindy",
            "schedule": 3600.0,  # Every hour
        },
        # Followup: Process leads every 2 hours
        "followup-every-2-hours": {
            "task": "app.tasks.agents_tasks.run_followup",
            "schedule": 7200.0,  # Every 2 hours
        },
        # Brief: Generate briefs every 30 minutes
        "brief-every-30-min": {
            "task": "app.tasks.agents_tasks.run_brief",
            "schedule": 1800.0,  # Every 30 minutes
        },
        # GROWTH MODULE
        # ContentAgent: Generate content daily
        "content-daily": {
            "task": "app.tasks.agents_tasks.run_content_agent",
            "schedule": 86400.0,  # Every 24 hours
        },
        # ReviewAgent: Request reviews daily
        "review-daily": {
            "task": "app.tasks.agents_tasks.run_review_agent",
            "schedule": 86400.0,  # Every 24 hours
        },
        # ReferralAgent: Process referrals daily
        "referral-daily": {
            "task": "app.tasks.agents_tasks.run_referral_agent",
            "schedule": 86400.0,  # Every 24 hours
        },
    }
)
