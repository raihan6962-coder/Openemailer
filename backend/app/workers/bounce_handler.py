import asyncio
from datetime import datetime, timezone
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app
from app.core.database import async_session_factory

logger = get_task_logger(__name__)


@celery_app.task
def process_bounce_queue():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_process_bounce_queue())


async def _process_bounce_queue():
    from app.repositories.campaign import CampaignRepository
    from app.repositories.lead import LeadRepository
    import imapclient

    async with async_session_factory() as db:
        try:
            campaign_repo = CampaignRepository(db)
            lead_repo = LeadRepository(db)

            logger.info("Bounce queue processed")

        except Exception as e:
            logger.error(f"Bounce processing error: {str(e)}")


@celery_app.task(bind=True, max_retries=2)
def handle_bounce(self, recipient_id: str, bounce_type: str, details: dict = None):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_handle_bounce(recipient_id, bounce_type, details))


async def _handle_bounce(recipient_id: str, bounce_type: str, details: dict = None):
    from app.repositories.campaign import CampaignRepository

    async with async_session_factory() as db:
        try:
            campaign_repo = CampaignRepository(db)

            if bounce_type in ("hard_bounce", "permanent_failure"):
                await campaign_repo.update_recipient(recipient_id, status="bounced", is_active=False)
            elif bounce_type in ("soft_bounce", "temporary_failure"):
                await campaign_repo.update_recipient(recipient_id, status="soft_bounce")

            logger.info(f"Bounce handled: {recipient_id} type={bounce_type}")

        except Exception as e:
            logger.error(f"Bounce handler error: {str(e)}")
