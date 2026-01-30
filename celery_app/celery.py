"""
Coffee Shop API - Celery Configuration

Celery application setup with Redis broker and periodic task scheduling.
"""

import os
from celery import Celery
from celery.schedules import crontab


# Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery = Celery(
    "coffee_shop",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["celery_app.tasks"],
)

# Celery configuration
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Periodic task schedule
    beat_schedule={
        "cleanup-unverified-users": {
            "task": "celery_app.tasks.cleanup_unverified_users",
            # Run every hour
            "schedule": crontab(minute=0),
        },
    },
)
