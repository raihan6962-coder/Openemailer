import asyncio
import random
from datetime import datetime, timezone, timedelta
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app
from app.core.database import async_session_factory
from app.core.config import settings

logger = get_task_logger(__name__)


@celery_app.task
def process_warmup_queue():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_process_warmup_queue())


async def _process_warmup_queue():
    from app.repositories.email_account import EmailAccountRepository
    from app.repositories.warmup import WarmupAccountRepository, WarmupScheduleRepository, WarmupNetworkMemberRepository
    from app.core.security import decrypt_value
    import aiosmtplib
    from email.mime.text import MIMEText

    async with async_session_factory() as db:
        try:
            warmup_repo = WarmupAccountRepository(db)
            schedule_repo = WarmupScheduleRepository(db)
            network_repo = WarmupNetworkMemberRepository(db)
            email_repo = EmailAccountRepository(db)

            schedules = await schedule_repo.get_pending_schedules()
            for schedule in schedules:
                warmup_account = await warmup_repo.get_by_id(schedule.warmup_account_id)
                if not warmup_account or not warmup_account.is_active:
                    continue

                account = await email_repo.get_by_id(warmup_account.email_account_id)
                if not account:
                    continue

                smtp_password = decrypt_value(account.smtp_password_encrypted) if account.smtp_password_encrypted else None

                msg = MIMEText(schedule.subject or "Warmup email", "plain")
                msg["From"] = account.email
                msg["To"] = schedule.target_email or "warmup@openmailer.local"
                msg["Subject"] = schedule.subject or f"Re: Fwd: Your message"

                try:
                    await aiosmtplib.send(
                        msg,
                        hostname=account.smtp_host or "smtp.gmail.com",
                        port=account.smtp_port or 587,
                        username=account.smtp_username or account.email,
                        password=smtp_password or "",
                        start_tls=True,
                    )
                    await schedule_repo.update(schedule.id, status="completed", executed_at=datetime.now(timezone.utc))
                    await warmup_repo.increment_sent(warmup_account.id)
                    logger.info(f"Warmup email sent from {account.email}")
                except Exception as e:
                    logger.error(f"Warmup send failed for {account.email}: {str(e)}")
                    await schedule_repo.update(schedule.id, status="failed")

        except Exception as e:
            logger.error(f"Warmup processing error: {str(e)}")


@celery_app.task
def schedule_warmup_emails():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_schedule_warmup_emails())


async def _schedule_warmup_emails():
    from app.repositories.warmup import WarmupAccountRepository, WarmupScheduleRepository, WarmupNetworkMemberRepository

    async with async_session_factory() as db:
        try:
            warmup_repo = WarmupAccountRepository(db)
            schedule_repo = WarmupScheduleRepository(db)
            network_repo = WarmupNetworkMemberRepository(db)

            active_accounts = await warmup_repo.get_active_accounts()
            network_members = await network_repo.get_active_members()

            for account in active_accounts:
                if account.daily_sent >= account.daily_target:
                    continue

                remaining = account.daily_target - account.daily_sent
                members = [m for m in network_members if m.email_account_id != account.email_account_id]
                if not members:
                    continue

                for _ in range(min(remaining, len(members))):
                    target = random.choice(members)
                    delay_minutes = random.randint(1, 30)
                    scheduled_at = datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)

                    subjects = [
                        "Quick question",
                        "Following up",
                        "Good morning",
                        "Hope this helps",
                        "Checking in",
                        "Thanks for the update",
                    ]

                    await schedule_repo.create(
                        warmup_account_id=account.id,
                        scheduled_at=scheduled_at,
                        action="send",
                        target_email=target.email,
                        subject=random.choice(subjects),
                    )
                    logger.info(f"Scheduled warmup for {account.id} -> {target.email}")

        except Exception as e:
            logger.error(f"Warmup scheduling error: {str(e)}")
