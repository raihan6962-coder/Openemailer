from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.repositories.automation import AutomationRepository

router = APIRouter(prefix="/automation", tags=["Automation"])


class AutomationCreateRequest(BaseModel):
    name: str
    description: str = None
    trigger_type: str
    trigger_config: dict = None


@router.get("/")
async def list_automations(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = AutomationRepository(db)
    automations = await repo.get_all(workspace_id=workspace.id)
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "status": a.status,
            "trigger_type": a.trigger_type,
            "run_count": a.run_count,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in automations
    ]


@router.post("/")
async def create_automation(request: AutomationCreateRequest, workspace=Depends(get_current_workspace),
                            db: AsyncSession = Depends(get_db)):
    repo = AutomationRepository(db)
    automation = await repo.create(
        workspace_id=workspace.id,
        name=request.name,
        description=request.description,
        trigger_type=request.trigger_type,
        trigger_config=request.trigger_config,
    )
    return {"id": str(automation.id), "name": automation.name}


@router.post("/{automation_id}/activate")
async def activate_automation(automation_id: str, workspace=Depends(get_current_workspace),
                              db: AsyncSession = Depends(get_db)):
    repo = AutomationRepository(db)
    await repo.update(automation_id, status="active", is_active=True)
    return {"message": "Automation activated"}
