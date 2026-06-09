from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "openmailer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.send_email",
        "app.workers.warmup_engine",
        "app.workers.spam_recovery",
        "app.workers.email_validation",
        "app.workers.bounce_handler",
        "app.workers.reply_detection",
        "app.workers.analytics_processor",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_max_tasks_per_child=200,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    beat_schedule={
        "process-warmup-queue": {
            "task": "app.workers.warmup_engine.process_warmup_queue",
            "schedule": 60.0,
        },
        "process-spam-recovery": {
            "task": "app.workers.spam_recovery.process_spam_recovery",
            "schedule": 300.0,
        },
        "process-bounce-handling": {
            "task": "app.workers.bounce_handler.process_bounce_queue",
            "schedule": 180.0,
        },
        "process-analytics-aggregation": {
            "task": "app.workers.analytics_processor.aggregate_daily_analytics",
            "schedule": 3600.0,
        },
    },
)


@celery_app.task(bind=True, max_retries=3)
def debug_task(self):
    print(f"Request: {self.request!r}")
