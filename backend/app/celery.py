from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "clientflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.reminders", "app.tasks.leads", "app.tasks.stats"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.DEFAULT_TIMEZONE,
    enable_utc=True,
    beat_schedule={
        "send-appointment-reminders": {
            "task": "app.tasks.reminders.check_and_send_reminders",
            "schedule": 300.0,  # Cada 5 minutos
        },
        "process-lead-follow-ups": {
            "task": "app.tasks.leads.process_follow_ups",
            "schedule": 3600.0,  # Cada hora
        },
        "update-daily-stats": {
            "task": "app.tasks.stats.update_daily_stats",
            "schedule": 86400.0,  # Una vez al día
        },
    },
)
