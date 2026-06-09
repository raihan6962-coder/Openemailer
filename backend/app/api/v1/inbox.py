from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.repositories.inbox import InboxEmailRepository, InboxFolderRepository

router = APIRouter(prefix="/inbox", tags=["Inbox"])


@router.get("/")
async def list_inbox(folder: str = "inbox", limit: int = 50,
                     workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = InboxEmailRepository(db)
    emails = await repo.get_all(workspace_id=workspace.id, limit=limit)
    return [
        {
            "id": str(e.id),
            "from_email": e.from_email,
            "from_name": e.from_name,
            "subject": e.subject,
            "folder": e.folder,
            "is_read": e.is_read,
            "is_starred": e.is_starred,
            "received_at": e.received_at.isoformat() if e.received_at else None,
        }
        for e in emails if e.folder == folder
    ]


@router.get("/{email_id}")
async def get_email(email_id: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = InboxEmailRepository(db)
    email = await repo.get_by_id(email_id)
    if not email or email.workspace_id != workspace.id:
        return {"error": "Email not found"}
    return {
        "id": str(email.id),
        "from_email": email.from_email,
        "from_name": email.from_name,
        "subject": email.subject,
        "body_text": email.body_text,
        "body_html": email.body_html,
        "folder": email.folder,
        "is_read": email.is_read,
        "is_starred": email.is_starred,
        "received_at": email.received_at.isoformat() if email.received_at else None,
    }


@router.post("/{email_id}/star")
async def star_email(email_id: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = InboxEmailRepository(db)
    email = await repo.get_by_id(email_id)
    if email and email.workspace_id == workspace.id:
        await repo.update(email_id, is_starred=not email.is_starred)
    return {"message": "Toggled star"}


@router.post("/{email_id}/archive")
async def archive_email(email_id: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = InboxEmailRepository(db)
    email = await repo.get_by_id(email_id)
    if email and email.workspace_id == workspace.id:
        await repo.update(email_id, is_archived=True, folder="archive")
    return {"message": "Archived"}
