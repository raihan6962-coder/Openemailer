from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent
from app.models.campaign import Campaign
from app.models.lead import Lead
from app.repositories.analytics import AnalyticsEventRepository, AnalyticsDailyRepository


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_repo = AnalyticsEventRepository(db)
        self.daily_repo = AnalyticsDailyRepository(db)

    async def track_event(self, workspace_id: UUID, event_type: str, entity_type: str = None,
                           entity_id: UUID = None, campaign_id: UUID = None,
                           lead_id: UUID = None, metadata: dict = None) -> None:
        await self.event_repo.create(
            workspace_id=workspace_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            campaign_id=campaign_id,
            lead_id=lead_id,
            metadata=metadata,
        )

    async def get_campaign_summary(self, workspace_id: UUID, campaign_id: UUID = None) -> dict:
        query = select(
            func.count(Campaign.id).label("total_campaigns"),
            func.sum(Campaign.sent_count).label("total_sent"),
            func.sum(Campaign.open_count).label("total_opens"),
            func.sum(Campaign.click_count).label("total_clicks"),
            func.sum(Campaign.reply_count).label("total_replies"),
            func.sum(Campaign.bounce_count).label("total_bounces"),
            func.sum(Campaign.spam_count).label("total_spam"),
        ).where(Campaign.workspace_id == workspace_id)

        if campaign_id:
            query = query.where(Campaign.id == campaign_id)

        result = await self.db.execute(query)
        row = result.one()

        total_sent = row.total_sent or 0
        return {
            "total_campaigns": row.total_campaigns or 0,
            "total_sent": total_sent,
            "total_opens": row.total_opens or 0,
            "total_clicks": row.total_clicks or 0,
            "total_replies": row.total_replies or 0,
            "total_bounces": row.total_bounces or 0,
            "total_spam": row.total_spam or 0,
            "open_rate": round((row.total_opens or 0) / total_sent * 100, 2) if total_sent > 0 else 0,
            "click_rate": round((row.total_clicks or 0) / total_sent * 100, 2) if total_sent > 0 else 0,
            "reply_rate": round((row.total_replies or 0) / total_sent * 100, 2) if total_sent > 0 else 0,
            "bounce_rate": round((row.total_bounces or 0) / total_sent * 100, 2) if total_sent > 0 else 0,
        }

    async def get_lead_count(self, workspace_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(Lead.id)).where(
                and_(Lead.workspace_id == workspace_id, Lead.is_active == True)
            )
        )
        return result.scalar() or 0

    async def get_dashboard_data(self, workspace_id: UUID) -> dict:
        campaign_summary = await self.get_campaign_summary(workspace_id)
        lead_count = await self.get_lead_count(workspace_id)

        return {
            "total_leads": lead_count,
            "total_campaigns": campaign_summary["total_campaigns"],
            "total_sent": campaign_summary["total_sent"],
            "total_opens": campaign_summary["total_opens"],
            "total_replies": campaign_summary["total_replies"],
            "open_rate": campaign_summary["open_rate"],
            "click_rate": campaign_summary["click_rate"],
            "reply_rate": campaign_summary["reply_rate"],
            "bounce_rate": campaign_summary["bounce_rate"],
        }
