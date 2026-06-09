from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.services.analytics.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    return await service.get_dashboard_data(workspace.id)


@router.get("/campaigns/{campaign_id}")
async def get_campaign_analytics(campaign_id: str, workspace=Depends(get_current_workspace),
                                 db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    return await service.get_campaign_summary(workspace.id, campaign_id)


@router.get("/overview")
async def get_overview(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = AnalyticsService(db)
    return await service.get_campaign_summary(workspace.id)
