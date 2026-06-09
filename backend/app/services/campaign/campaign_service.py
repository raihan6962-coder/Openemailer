from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.repositories.campaign import CampaignRepository, CampaignEmailRepository, CampaignSequenceRepository, CampaignRecipientRepository
from app.repositories.lead import LeadRepository
from app.repositories.template import TemplateRepository


class CampaignService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CampaignRepository(db)
        self.email_repo = CampaignEmailRepository(db)
        self.sequence_repo = CampaignSequenceRepository(db)
        self.recipient_repo = CampaignRecipientRepository(db)
        self.lead_repo = LeadRepository(db)
        self.template_repo = TemplateRepository(db)

    async def create_campaign(self, workspace_id: UUID, user_id: UUID, name: str,
                               campaign_type: str = "one_time", daily_limit: int = 100,
                               description: str = None, **kwargs) -> dict:
        campaign = await self.repo.create(
            workspace_id=workspace_id,
            name=name,
            description=description,
            campaign_type=campaign_type,
            daily_limit=daily_limit,
            **kwargs
        )
        return {"id": str(campaign.id), "name": campaign.name, "type": campaign.campaign_type}

    async def add_recipients(self, campaign_id: UUID, workspace_id: UUID, lead_ids: List[UUID]) -> int:
        campaign = await self.repo.get_by_id(campaign_id)
        if not campaign or campaign.workspace_id != workspace_id:
            raise NotFoundException("Campaign not found")

        count = 0
        for lead_id in lead_ids:
            lead = await self.lead_repo.get_by_id(lead_id)
            if lead and lead.is_valid:
                existing = await self.recipient_repo.get_by_campaign_and_lead(campaign_id, lead_id)
                if not existing:
                    await self.recipient_repo.create(
                        campaign_id=campaign_id,
                        lead_id=lead_id,
                        email=lead.email,
                    )
                    count += 1
        return count

    async def start_campaign(self, campaign_id: UUID, workspace_id: UUID) -> dict:
        campaign = await self.repo.get_by_id(campaign_id)
        if not campaign or campaign.workspace_id != workspace_id:
            raise NotFoundException("Campaign not found")
        if campaign.status != "draft":
            raise ValidationException("Campaign must be in draft status to start")

        await self.repo.update(campaign_id, status="active", started_at=datetime.now(timezone.utc))

        from app.workers.send_email import send_email_task
        recipients = await self.recipient_repo.get_pending_recipients(campaign_id)
        for recipient in recipients[:campaign.daily_limit]:
            emails = await self.email_repo.get_all(workspace_id=workspace_id)
            if emails:
                send_email_task.delay(str(emails[0].id), str(recipient.id))

        return {
            "id": str(campaign.id),
            "status": "active",
            "recipients_count": len(recipients),
        }

    async def pause_campaign(self, campaign_id: UUID, workspace_id: UUID) -> dict:
        campaign = await self.repo.get_by_id(campaign_id)
        if not campaign or campaign.workspace_id != workspace_id:
            raise NotFoundException("Campaign not found")
        await self.repo.update(campaign_id, status="paused")
        return {"id": str(campaign.id), "status": "paused"}
