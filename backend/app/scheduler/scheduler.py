from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from app.core.config import settings

scheduler = AsyncIOScheduler()


async def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")


async def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")


def setup_jobs():
    from app.workers.warmup_engine import schedule_warmup_emails
    from app.workers.spam_recovery import process_spam_recovery
    from app.workers.analytics_processor import aggregate_daily_analytics
    from app.tasks.deliverability import check_dns_health
    from app.tasks.cleanup import cleanup_expired_sessions

    scheduler.add_job(
        schedule_warmup_emails,
        IntervalTrigger(minutes=15),
        id="schedule_warmup_emails",
        replace_existing=True,
    )

    scheduler.add_job(
        process_spam_recovery,
        IntervalTrigger(minutes=5),
        id="process_spam_recovery",
        replace_existing=True,
    )

    scheduler.add_job(
        aggregate_daily_analytics,
        CronTrigger(hour=0, minute=0),
        id="aggregate_daily_analytics",
        replace_existing=True,
    )

    scheduler.add_job(
        check_dns_health,
        IntervalTrigger(hours=6),
        id="check_dns_health",
        replace_existing=True,
    )

    scheduler.add_job(
        cleanup_expired_sessions,
        IntervalTrigger(hours=24),
        id="cleanup_expired_sessions",
        replace_existing=True,
    )

    logger.info("Scheduled jobs configured")
