import asyncio
import re
from datetime import datetime, timezone
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app
from app.core.database import async_session_factory

logger = get_task_logger(__name__)

INTERESTED_PATTERNS = [
    r"(interested|intrested)", r"(yes|yeah|sure|okay|ok)\s*(please|let's|go)",
    r"schedule|booking|book\s+a\s*call|let's\s*talk", r"great|perfect|awesome",
    r"tell\s*me\s*more", r"how\s*does\s*this\s*work", r"pricing|price|cost",
    r"demo|meeting|call",
]

NOT_INTERESTED_PATTERNS = [
    r"(not\s*interested|uninterested)", r"(no\s*thanks|no\s*thank\s*you)",
    r"remove|unsubscribe", r"stop|quit|cancel",
    r"(don't|do\s*not)\s*contact", r"spam",
]

MEETING_REQUEST_PATTERNS = [
    r"schedule|calendly|cal\.com", r"book\s*a\s*(call|meeting|demo)",
    r"available\s*(next|this|tomorrow)", r"let's\s*(talk|chat|meet)",
    r"google\s*meet|zoom|teams|whereby",
]

OOO_PATTERNS = [
    r"out\s*of\s*office", r"vacation|holiday|away",
    r"will\s*be\s*back", r"not\s*in\s*the\s*office",
    r"unavailable",
]


def classify_reply(subject: str, body: str) -> str:
    text = f"{subject} {body}".lower()

    for pattern in OOO_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return "out_of_office"

    for pattern in MEETING_REQUEST_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return "meeting_request"

    for pattern in INTERESTED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return "interested"

    for pattern in NOT_INTERESTED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return "not_interested"

    return "positive_reply"


@celery_app.task
def detect_reply_type(subject: str, body: str) -> str:
    return classify_reply(subject, body)


@celery_app.task
def process_reply_detection():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_process_reply_detection())


async def _process_reply_detection():
    from app.repositories.inbox import InboxEmailRepository
    from app.repositories.campaign import CampaignRepository

    async with async_session_factory() as db:
        try:
            inbox_repo = InboxEmailRepository(db)
            campaign_repo = CampaignRepository(db)

            logger.info("Reply detection processed")

        except Exception as e:
            logger.error(f"Reply detection error: {str(e)}")
