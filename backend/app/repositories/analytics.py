from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent, AnalyticsDaily, CampaignReportData, DeliverabilityReport
from app.repositories.base import BaseRepository


class AnalyticsEventRepository(BaseRepository[AnalyticsEvent]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AnalyticsEvent)


class AnalyticsDailyRepository(BaseRepository[AnalyticsDaily]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AnalyticsDaily)


class CampaignReportDataRepository(BaseRepository[CampaignReportData]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CampaignReportData)


class DeliverabilityReportRepository(BaseRepository[DeliverabilityReport]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DeliverabilityReport)
