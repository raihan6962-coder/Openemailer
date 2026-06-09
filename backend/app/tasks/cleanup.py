import asyncio
from datetime import datetime, timezone, timedelta
from loguru import logger
from app.core.database import async_session_factory
from sqlalchemy import delete
from app.models.user import Session, PasswordReset


async def cleanup_expired_sessions():
    async with async_session_factory() as db:
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            result = await db.execute(
                delete(Session).where(Session.created_at < cutoff)
            )
            await db.commit()
            logger.info(f"Cleaned up {result.rowcount} expired sessions")

            result2 = await db.execute(
                delete(PasswordReset).where(PasswordReset.expires_at < datetime.now(timezone.utc))
            )
            await db.commit()
            logger.info(f"Cleaned up {result2.rowcount} expired password resets")

        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
