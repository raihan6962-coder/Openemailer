from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import require_admin
from app.repositories.user import UserRepository
from app.repositories.audit_log import AuditLogRepository

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
async def admin_list_users(db: AsyncSession = Depends(get_db), admin=Depends(require_admin)):
    repo = UserRepository(db)
    users = await repo.get_all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_verified": u.is_verified,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.get("/audit-logs")
async def admin_audit_logs(limit: int = 50, db: AsyncSession = Depends(get_db), admin=Depends(require_admin)):
    repo = AuditLogRepository(db)
    logs = await repo.get_all(limit=limit)
    return [
        {
            "id": str(l.id),
            "user_id": str(l.user_id) if l.user_id else None,
            "action": l.action,
            "entity_type": l.entity_type,
            "details": l.details,
            "severity": l.severity,
            "occurred_at": l.occurred_at.isoformat() if l.occurred_at else None,
        }
        for l in logs
    ]


@router.get("/stats")
async def admin_stats(db: AsyncSession = Depends(get_db), admin=Depends(require_admin)):
    from sqlalchemy import select, func
    from app.models.user import User
    from app.models.workspace import Workspace
    from app.models.lead import Lead
    from app.models.campaign import Campaign

    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    workspace_count = (await db.execute(select(func.count(Workspace.id)))).scalar() or 0
    lead_count = (await db.execute(select(func.count(Lead.id)))).scalar() or 0
    campaign_count = (await db.execute(select(func.count(Campaign.id)))).scalar() or 0

    return {
        "total_users": user_count,
        "total_workspaces": workspace_count,
        "total_leads": lead_count,
        "total_campaigns": campaign_count,
    }
