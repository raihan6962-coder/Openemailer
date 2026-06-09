from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.services.billing.billing_service import BillingService
from app.repositories.billing import BillingPlanRepository

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/plans")
async def list_plans(db: AsyncSession = Depends(get_db)):
    repo = BillingPlanRepository(db)
    plans = await repo.get_all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "code": p.code,
            "price_monthly": p.price_monthly,
            "price_yearly": p.price_yearly,
            "max_users": p.max_users,
            "max_leads": p.max_leads,
            "max_campaigns": p.max_campaigns,
            "max_mailboxes": p.max_mailboxes,
        }
        for p in plans
    ]


@router.post("/subscribe/{plan_id}")
async def subscribe(plan_id: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = BillingService(db)
    return await service.create_subscription(workspace.id, plan_id)


@router.get("/subscription")
async def get_subscription(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    from app.repositories.billing import SubscriptionRepository
    repo = SubscriptionRepository(db)
    subs = await repo.get_all(workspace_id=workspace.id)
    for sub in subs:
        if sub.is_active:
            return {
                "id": str(sub.id),
                "status": sub.status,
                "billing_cycle": sub.billing_cycle,
                "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
                "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            }
    return {"message": "No active subscription"}


@router.get("/usage")
async def get_usage(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = BillingService(db)
    return await service.get_usage(workspace.id)
