from celery import Celery
from celery.schedules import crontab
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "supplier_sync",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configure scheduled tasks
celery_app.conf.beat_schedule = {
    "sync-suppliers-daily": {
        "task": "app.tasks.sync_all_suppliers",
        "schedule": crontab.parse(settings.SYNC_SCHEDULE),
        "options": {
            "expires": 3600  # Task expires after 1 hour
        }
    }
}

# Import tasks to ensure they're registered
from app.tasks import sync_supplier, sync_all_suppliers
