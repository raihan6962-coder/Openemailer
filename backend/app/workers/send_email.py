import asyncio
from datetime import datetime, timezone
from typing import Optional
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app
from app.core.database import async_session_factory
from app.core.config import settings

logger = get_task_logger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, campaign_email_id: str, recipient_id: str):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_send_email(campaign_email_id, recipient_id))


async def _send_email(campaign_email_id: str, recipient_id: str):
    from app.repositories.email_account import EmailAccountRepository
    from app.repositories.campaign import CampaignRepository
    from app.models.campaign import CampaignEmail, CampaignRecipient
    from app.core.security import decrypt_value
    import aiosmtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    async with async_session_factory() as db:
        try:
            campaign_repo = CampaignRepository(db)
            email_repo = EmailAccountRepository(db)

            email = await db.get(CampaignEmail, campaign_email_id)
            recipient = await db.get(CampaignRecipient, recipient_id)

            if not email or not recipient:
                logger.error(f"Email or recipient not found: {campaign_email_id}, {recipient_id}")
                return

            account = await email_repo.get_by_id(email.sender_email)
            if not account:
                logger.error(f"Sender account not found: {email.sender_email}")
                return

            smtp_password = decrypt_value(account.smtp_password_encrypted) if account.smtp_password_encrypted else None

            msg = MIMEMultipart("alternative")
            msg["From"] = f"{account.email}"
            msg["To"] = recipient.email
            msg["Subject"] = email.subject

            if email.body_text:
                msg.attach(MIMEText(email.body_text, "plain"))
            if email.body_html:
                msg.attach(MIMEText(email.body_html, "html"))

            smtp_host = account.smtp_host or "smtp.gmail.com"
            smtp_port = account.smtp_port or 587

            await aiosmtplib.send(
                msg,
                hostname=smtp_host,
                port=smtp_port,
                username=account.smtp_username or account.email,
                password=smtp_password or "",
                start_tls=True,
            )

            current_step = recipient.current_step
            await campaign_repo.update_recipient(
                recipient.id,
                status="sent",
                current_step=current_step + 1,
            )

            logger.info(f"Email sent to {recipient.email}")

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise
