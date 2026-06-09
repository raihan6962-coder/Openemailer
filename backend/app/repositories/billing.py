from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import BillingPlan, Subscription, UsageRecord, Invoice
from app.repositories.base import BaseRepository


class BillingPlanRepository(BaseRepository[BillingPlan]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, BillingPlan)


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Subscription)


class UsageRecordRepository(BaseRepository[UsageRecord]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, UsageRecord)


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Invoice)
