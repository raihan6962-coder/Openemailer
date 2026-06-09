from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.repositories.warmup import WarmupAccountRepository, WarmupNetworkMemberRepository

router = APIRouter(prefix="/warmup", tags=["Warmup"])


@router.get("/accounts")
async def list_warmup_accounts(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = WarmupAccountRepository(db)
    accounts = await repo.get_all(workspace_id=workspace.id)
    return [
        {
            "id": str(a.id),
            "email_account_id": str(a.email_account_id),
            "status": a.status,
            "daily_target": a.daily_target,
            "daily_sent": a.daily_sent,
            "health_score": a.health_score,
            "inbox_placement_rate": a.inbox_placement_rate,
            "total_sent": a.total_sent,
        }
        for a in accounts
    ]


@router.post("/accounts")
async def enable_warmup(email_account_id: str, workspace=Depends(get_current_workspace),
                        db: AsyncSession = Depends(get_db)):
    repo = WarmupAccountRepository(db)
    account = await repo.create(
        workspace_id=workspace.id,
        email_account_id=email_account_id,
    )
    return {"id": str(account.id), "status": account.status}


@router.get("/network")
async def get_network_status(db: AsyncSession = Depends(get_db)):
    repo = WarmupNetworkMemberRepository(db)
    members = await repo.get_active_members()
    return {
        "total_members": len(members),
        "members": [
            {
                "id": str(m.id),
                "email": m.email,
                "trust_score": m.trust_score,
                "reputation_score": m.reputation_score,
                "total_exchanges": m.total_exchanges,
            }
            for m in members
        ],
    }


@router.post("/network/join")
async def join_network(email_account_id: str, workspace=Depends(get_current_workspace),
                       db: AsyncSession = Depends(get_db)):
    repo = WarmupNetworkMemberRepository(db)
    member = await repo.create(
        workspace_id=workspace.id,
        email_account_id=email_account_id,
    )
    return {"id": str(member.id), "status": "joined"}
