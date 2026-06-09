import asyncio
import re
import dns.resolver
import smtplib
from email.utils import parseaddr
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app
from app.core.database import async_session_factory

logger = get_task_logger(__name__)

DISPOSABLE_DOMAINS = {
    "tempmail.com", "throwaway.com", "mailinator.com", "guerrillamail.com",
    "10minutemail.com", "yopmail.com", "sharklasers.com", "trashmail.com",
    "mailnator.com", "getnada.com", "tempinbox.com", "fakeinbox.com",
}

ROLE_PREFIXES = {
    "admin", "info", "support", "sales", "contact", "webmaster",
    "noreply", "no-reply", "help", "enquiries", "enquiry",
    "marketing", "team", "hello", "careers", "jobs", "billing",
}


def validate_syntax(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_disposable(domain: str) -> bool:
    return domain.lower() in DISPOSABLE_DOMAINS


def is_role_based(email: str) -> bool:
    local_part = email.split("@")[0].lower()
    return local_part in ROLE_PREFIXES


def check_mx(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return len(answers) > 0
    except Exception:
        return False


def check_domain(domain: str) -> bool:
    try:
        dns.resolver.resolve(domain, "A")
        return True
    except Exception:
        try:
            dns.resolver.resolve(domain, "AAAA")
            return True
        except Exception:
            return False


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def validate_email_task(self, lead_id: str, email: str, workspace_id: str):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_validate_email(lead_id, email, workspace_id))


async def _validate_email(lead_id: str, email: str, workspace_id: str):
    from app.repositories.validation import ValidationResultRepository
    from app.repositories.lead import LeadRepository

    async with async_session_factory() as db:
        try:
            validation_repo = ValidationResultRepository(db)
            lead_repo = LeadRepository(db)

            syntax_valid = validate_syntax(email)
            domain = email.split("@")[1] if "@" in email else ""
            domain_valid = check_domain(domain) if syntax_valid else False
            mx_valid = check_mx(domain) if domain_valid else False
            disposable = is_disposable(domain)
            role_based = is_role_based(email)

            quality_score = 0
            if syntax_valid:
                quality_score += 20
            if domain_valid:
                quality_score += 20
            if mx_valid:
                quality_score += 25
            if not disposable:
                quality_score += 15
            if not role_based:
                quality_score += 20

            risk_level = "low"
            if quality_score < 40:
                risk_level = "high"
            elif quality_score < 70:
                risk_level = "medium"

            await validation_repo.create(
                workspace_id=workspace_id,
                lead_id=lead_id,
                email=email,
                syntax_valid=syntax_valid,
                domain_valid=domain_valid,
                mx_valid=mx_valid,
                smtp_valid=False,
                is_catch_all=False,
                is_disposable=disposable,
                is_role_based=role_based,
                quality_score=quality_score,
                risk_level=risk_level,
            )

            await lead_repo.update(lead_id,
                is_valid=syntax_valid and domain_valid,
                is_disposable=disposable,
                is_role_based=role_based,
                quality_score=quality_score,
                validation_status="completed",
            )

            logger.info(f"Validated {email}: score={quality_score}, risk={risk_level}")

        except Exception as e:
            logger.error(f"Validation error for {email}: {str(e)}")
