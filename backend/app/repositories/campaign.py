from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign, CampaignEmail, CampaignSequence, CampaignRecipient, CampaignReport
from app.repositories.base import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Campaign)

    async def get_active_campaigns(self, workspace_id: UUID) -> List[Campaign]:
        result = await self.db.execute(
            select(Campaign).where(
                and_(Campaign.workspace_id == workspace_id, Campaign.is_active == True, Campaign.status == "active")
            )
        )
        return list(result.scalars().all())

    async def update_status(self, campaign_id: UUID, status: str) -> Optional[Campaign]:
        return await self.update(campaign_id, status=status)


class CampaignEmailRepository(BaseRepository[CampaignEmail]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CampaignEmail)


class CampaignSequenceRepository(BaseRepository[CampaignSequence]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CampaignSequence)


class CampaignRecipientRepository(BaseRepository[CampaignRecipient]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CampaignRecipient)

    async def get_by_campaign_and_lead(self, campaign_id: UUID, lead_id: UUID) -> Optional[CampaignRecipient]:
        result = await self.db.execute(
            select(CampaignRecipient).where(
                and_(CampaignRecipient.campaign_id == campaign_id, CampaignRecipient.lead_id == lead_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_pending_recipients(self, campaign_id: UUID) -> List[CampaignRecipient]:
        result = await self.db.execute(
            select(CampaignRecipient).where(
                and_(CampaignRecipient.campaign_id == campaign_id, CampaignRecipient.status == "pending", CampaignRecipient.is_active == True)
            )
        )
        return list(result.scalars().all())


class CampaignReportRepository(BaseRepository[CampaignReport]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CampaignReport)
