"""Celery app (Phase 1: defined, no scheduled tasks yet — jobs arrive in Phase 3+)."""

from celery import Celery

from app.core.config import settings

celery_app = Celery("blood_bank", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_track_started=True, timezone="UTC", enable_utc=True)
