from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.repositories.workspace import WorkspaceRepository, WorkspaceMemberRepository

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("/current")
async def get_current_ws(workspace=Depends(get_current_workspace)):
    return {
        "id": str(workspace.id),
        "name": workspace.name,
        "slug": workspace.slug,
        "plan": workspace.plan,
        "status": workspace.status,
        "max_users": workspace.max_users,
        "max_leads": workspace.max_leads,
        "max_campaigns": workspace.max_campaigns,
        "max_mailboxes": workspace.max_mailboxes,
    }


@router.get("/members")
async def get_members(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = WorkspaceMemberRepository(db)
    members = await repo.get_workspace_members(workspace.id)
    return [{"id": str(m.id), "user_id": str(m.user_id), "role": m.role} for m in members]
