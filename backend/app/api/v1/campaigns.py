from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.services.campaign.campaign_service import CampaignService
from app.repositories.campaign import CampaignRepository

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


class CampaignCreateRequest(BaseModel):
    name: str
    description: str = None
    campaign_type: str = "one_time"
    daily_limit: int = 100


class AddRecipientsRequest(BaseModel):
    lead_ids: List[str]


@router.get("/")
async def list_campaigns(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = CampaignRepository(db)
    campaigns = await repo.get_all(workspace_id=workspace.id)
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "type": c.campaign_type,
            "status": c.status,
            "sent_count": c.sent_count,
            "open_count": c.open_count,
            "reply_count": c.reply_count,
            "bounce_count": c.bounce_count,
            "daily_limit": c.daily_limit,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in campaigns
    ]


@router.post("/")
async def create_campaign(request: CampaignCreateRequest, current_user=Depends(get_current_user),
                          workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = CampaignService(db)
    return await service.create_campaign(
        workspace_id=workspace.id,
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        campaign_type=request.campaign_type,
        daily_limit=request.daily_limit,
    )


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = CampaignRepository(db)
    campaign = await repo.get_by_id(campaign_id)
    if not campaign or campaign.workspace_id != workspace.id:
        return {"error": "Campaign not found"}
    return {
        "id": str(campaign.id),
        "name": campaign.name,
        "type": campaign.campaign_type,
        "status": campaign.status,
        "daily_limit": campaign.daily_limit,
        "sending_window": f"{campaign.sending_window_start} - {campaign.sending_window_end}",
        "timezone": campaign.timezone,
        "sent_count": campaign.sent_count,
        "open_count": campaign.open_count,
        "click_count": campaign.click_count,
        "reply_count": campaign.reply_count,
        "bounce_count": campaign.bounce_count,
        "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
    }


@router.post("/{campaign_id}/recipients")
async def add_recipients(campaign_id: str, request: AddRecipientsRequest,
                         workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = CampaignService(db)
    count = await service.add_recipients(campaign_id, workspace.id, request.lead_ids)
    return {"added": count}


@router.post("/{campaign_id}/start")
async def start_campaign(campaign_id: str, workspace=Depends(get_current_workspace),
                         db: AsyncSession = Depends(get_db)):
    service = CampaignService(db)
    return await service.start_campaign(campaign_id, workspace.id)


@router.post("/{campaign_id}/pause")
async def pause_campaign(campaign_id: str, workspace=Depends(get_current_workspace),
                         db: AsyncSession = Depends(get_db)):
    service = CampaignService(db)
    return await service.pause_campaign(campaign_id, workspace.id)
