from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead, LeadList, LeadSegment, LeadScore, LeadEnrichment
from app.repositories.base import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Lead)

    async def get_by_email(self, email: str, workspace_id: UUID) -> Optional[Lead]:
        result = await self.db.execute(
            select(Lead).where(and_(Lead.email == email, Lead.workspace_id == workspace_id, Lead.is_active == True))
        )
        return result.scalar_one_or_none()

    async def get_by_list(self, list_id: UUID) -> List[Lead]:
        result = await self.db.execute(
            select(Lead).where(and_(Lead.list_id == list_id, Lead.is_active == True))
        )
        return list(result.scalars().all())

    async def bulk_update_status(self, lead_ids: List[UUID], status: str) -> None:
        from sqlalchemy import update
        await self.db.execute(
            update(Lead).where(Lead.id.in_(lead_ids)).values(status=status)
        )
        await self.db.flush()


class LeadListRepository(BaseRepository[LeadList]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, LeadList)


class LeadSegmentRepository(BaseRepository[LeadSegment]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, LeadSegment)


class LeadScoreRepository(BaseRepository[LeadScore]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, LeadScore)


class LeadEnrichmentRepository(BaseRepository[LeadEnrichment]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, LeadEnrichment)
