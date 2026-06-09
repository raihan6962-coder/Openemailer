from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warmup import WarmupAccount, WarmupSchedule, WarmupStat, WarmupNetworkMember, WarmupExchange
from app.repositories.base import BaseRepository


class WarmupAccountRepository(BaseRepository[WarmupAccount]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, WarmupAccount)

    async def get_active_accounts(self) -> List[WarmupAccount]:
        result = await self.db.execute(
            select(WarmupAccount).where(and_(WarmupAccount.is_active == True, WarmupAccount.status == "active"))
        )
        return list(result.scalars().all())

    async def increment_sent(self, account_id: UUID) -> None:
        from sqlalchemy.sql import func
        await self.db.execute(
            update(WarmupAccount).where(WarmupAccount.id == account_id).values(
                daily_sent=WarmupAccount.daily_sent + 1,
                total_sent=WarmupAccount.total_sent + 1,
            )
        )
        await self.db.flush()


class WarmupScheduleRepository(BaseRepository[WarmupSchedule]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, WarmupSchedule)

    async def get_pending_schedules(self) -> List[WarmupSchedule]:
        result = await self.db.execute(
            select(WarmupSchedule).where(
                and_(WarmupSchedule.status == "pending", WarmupSchedule.scheduled_at <= datetime.utcnow(), WarmupSchedule.is_active == True)
            )
        )
        return list(result.scalars().all())


class WarmupStatRepository(BaseRepository[WarmupStat]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, WarmupStat)


class WarmupNetworkMemberRepository(BaseRepository[WarmupNetworkMember]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, WarmupNetworkMember)

    async def get_active_members(self) -> List[WarmupNetworkMember]:
        result = await self.db.execute(
            select(WarmupNetworkMember).where(WarmupNetworkMember.is_active == True)
        )
        return list(result.scalars().all())


class WarmupExchangeRepository(BaseRepository[WarmupExchange]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, WarmupExchange)
