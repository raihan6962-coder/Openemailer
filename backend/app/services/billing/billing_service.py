from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.repositories.billing import BillingPlanRepository, SubscriptionRepository, UsageRecordRepository


class BillingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.plan_repo = BillingPlanRepository(db)
        self.subscription_repo = SubscriptionRepository(db)
        self.usage_repo = UsageRecordRepository(db)

    async def get_plans(self) -> list:
        return await self.plan_repo.get_all()

    async def create_subscription(self, workspace_id: UUID, plan_id: UUID, billing_cycle: str = "monthly") -> dict:
        plan = await self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise NotFoundException("Plan not found")

        existing = await self.subscription_repo.get_all(workspace_id=workspace_id)
        for sub in existing:
            if sub.is_active:
                raise ValidationException("Workspace already has an active subscription")

        subscription = await self.subscription_repo.create(
            workspace_id=workspace_id,
            plan_id=plan_id,
            billing_cycle=billing_cycle,
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc).replace(month=datetime.now(timezone.utc).month + 1),
        )

        return {
            "id": str(subscription.id),
            "plan": plan.name,
            "status": subscription.status,
        }

    async def get_usage(self, workspace_id: UUID) -> dict:
        records = await self.usage_repo.get_all(workspace_id=workspace_id)
        usage = {}
        for record in records:
            usage[record.metric] = record.value
        return usage

    async def track_usage(self, workspace_id: UUID, metric: str, value: int = 1) -> None:
        await self.usage_repo.create(
            workspace_id=workspace_id,
            metric=metric,
            value=value,
        )
