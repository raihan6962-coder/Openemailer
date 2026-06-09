import asyncio
from datetime import datetime, timezone
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app
from app.core.database import async_session_factory

logger = get_task_logger(__name__)


@celery_app.task
def process_spam_recovery():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_process_spam_recovery())


async def _process_spam_recovery():
    from app.repositories.spam_recovery import SpamRecoveryJobRepository
    from app.repositories.email_account import EmailAccountRepository
    from app.core.security import decrypt_value
    import imapclient
    import pyzmail

    async with async_session_factory() as db:
        try:
            job_repo = SpamRecoveryJobRepository(db)
            email_repo = EmailAccountRepository(db)

            active_jobs = await job_repo.get_active_jobs()
            for job in active_jobs:
                account = await email_repo.get_by_id(job.email_account_id)
                if not account:
                    continue

                imap_password = decrypt_value(account.imap_password_encrypted) if account.imap_password_encrypted else None
                if not imap_password:
                    continue

                try:
                    imap_host = account.imap_host or "imap.gmail.com"
                    imap_port = account.imap_port or 993

                    server = imapclient.IMAPClient(imap_host, port=imap_port, ssl=True)
                    server.login(account.imap_username or account.email, imap_password)

                    server.select_folder("[Gmail]/Spam" if "gmail" in imap_host.lower() else "SPAM")
                    messages = server.search(["ALL"])
                    detected = len(messages)

                    for msg_id in messages:
                        raw_message = server.fetch([msg_id], ["FLAGS", "INTERNALDATE"])
                        server.add_flags(msg_id, [imapclient.SEEN])
                        server.move([msg_id], "INBOX")

                        await job_repo.add_log(
                            job_id=job.id,
                            email_id=str(msg_id),
                            action="move_to_inbox",
                            status="success",
                        )

                    if detected > 0:
                        await job_repo.update_stats(job.id, detected=detected)
                        logger.info(f"Recovered {detected} emails from spam for {account.email}")

                    server.logout()

                except Exception as e:
                    logger.error(f"Spam recovery failed for {account.email}: {str(e)}")

        except Exception as e:
            logger.error(f"Spam recovery processing error: {str(e)}")
