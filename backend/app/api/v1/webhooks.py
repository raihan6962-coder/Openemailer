from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.repositories.webhook import WebhookRepository

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


class WebhookCreateRequest(BaseModel):
    name: str
    url: str
    events: str = None


@router.get("/")
async def list_webhooks(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = WebhookRepository(db)
    webhooks = await repo.get_all(workspace_id=workspace.id)
    return [
        {
            "id": str(w.id),
            "name": w.name,
            "url": w.url,
            "events": w.events,
            "is_active": w.is_active,
        }
        for w in webhooks
    ]


@router.post("/")
async def create_webhook(request: WebhookCreateRequest, workspace=Depends(get_current_workspace),
                         db: AsyncSession = Depends(get_db)):
    repo = WebhookRepository(db)
    webhook = await repo.create(
        workspace_id=workspace.id,
        name=request.name,
        url=request.url,
        events=request.events,
    )
    return {"id": str(webhook.id), "name": webhook.name}


@router.delete("/{webhook_id}")
async def delete_webhook(webhook_id: str, workspace=Depends(get_current_workspace),
                         db: AsyncSession = Depends(get_db)):
    repo = WebhookRepository(db)
    await repo.delete(webhook_id)
    return {"message": "Webhook deleted"}
