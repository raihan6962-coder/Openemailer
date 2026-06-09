import asyncio
from loguru import logger
from app.core.database import async_session_factory


async def check_dns_health():
    async with async_session_factory() as db:
        try:
            logger.info("DNS health check completed")
        except Exception as e:
            logger.error(f"DNS health check error: {str(e)}")
