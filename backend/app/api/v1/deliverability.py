from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.services.deliverability.dns_service import DNSService
from app.repositories.deliverability import DNSCheckRepository

router = APIRouter(prefix="/deliverability", tags=["Deliverability"])


@router.get("/dns-check")
async def check_dns(domain: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = DNSService(db)
    return await service.full_dns_check(domain, str(workspace.id))


@router.get("/checks")
async def list_checks(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = DNSCheckRepository(db)
    checks = await repo.get_all(workspace_id=workspace.id)
    return [
        {
            "id": str(c.id),
            "domain": c.domain,
            "overall_health": c.overall_health,
            "spf_status": c.spf_status,
            "dkim_status": c.dkim_status,
            "dmarc_status": c.dmarc_status,
            "mx_status": c.mx_status,
            "checked_at": c.checked_at.isoformat() if c.checked_at else None,
        }
        for c in checks
    ]


@router.get("/scores")
async def get_deliverability_scores(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    from app.repositories.deliverability import DeliverabilityScoreRepository
    repo = DeliverabilityScoreRepository(db)
    scores = await repo.get_all(workspace_id=workspace.id)
    return [
        {
            "id": str(s.id),
            "score_type": s.score_type,
            "score": s.score,
            "calculated_at": s.calculated_at.isoformat() if s.calculated_at else None,
        }
        for s in scores
    ]
