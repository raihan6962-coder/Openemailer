from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.spam_recovery import SpamRecoveryJob, SpamRecoveryLog
from app.repositories.base import BaseRepository


class SpamRecoveryJobRepository(BaseRepository[SpamRecoveryJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SpamRecoveryJob)

    async def get_active_jobs(self) -> List[SpamRecoveryJob]:
        result = await self.db.execute(
            select(SpamRecoveryJob).where(and_(SpamRecoveryJob.is_active == True, SpamRecoveryJob.status == "active"))
        )
        return list(result.scalars().all())

    async def update_stats(self, job_id: UUID, detected: int = 0, recovered: int = 0) -> None:
        await self.db.execute(
            update(SpamRecoveryJob).where(SpamRecoveryJob.id == job_id).values(
                total_detected=SpamRecoveryJob.total_detected + detected,
                total_recovered=SpamRecoveryJob.total_recovered + (recovered if recovered else detected),
                recovery_rate=((SpamRecoveryJob.total_recovered + (recovered if recovered else detected)) * 100 /
                               (SpamRecoveryJob.total_detected + detected)) if (SpamRecoveryJob.total_detected + detected) > 0 else 0,
                last_run_at=datetime.utcnow(),
            )
        )
        await self.db.flush()

    async def add_log(self, job_id: UUID, email_id: str, action: str, status: str, subject: str = None, from_email: str = None, details: str = None) -> SpamRecoveryLog:
        log = SpamRecoveryLog(
            job_id=job_id,
            email_id=email_id,
            action=action,
            status=status,
            subject=subject,
            from_email=from_email,
            details=details,
        )
        self.db.add(log)
        await self.db.flush()
        return log


class SpamRecoveryLogRepository(BaseRepository[SpamRecoveryLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SpamRecoveryLog)
