from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.services.email.email_account_service import EmailAccountService

router = APIRouter(prefix="/mailboxes", tags=["Mailboxes"])


class SMTPAccountRequest(BaseModel):
    email: str
    smtp_host: str
    smtp_port: int = 587
    smtp_username: str = None
    smtp_password: str
    imap_host: str = None
    imap_port: int = 993
    imap_username: str = None
    imap_password: str = None
    provider: str = "custom"
    is_primary: bool = False
    daily_send_limit: int = 50


@router.get("/")
async def list_mailboxes(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = EmailAccountService(db)
    return await service.list_accounts(workspace.id)


@router.post("/connect")
async def connect_smtp(request: SMTPAccountRequest, current_user=Depends(get_current_user),
                       workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = EmailAccountService(db)
    return await service.create_smtp_account(
        workspace_id=workspace.id,
        user_id=current_user.id,
        email=request.email,
        smtp_host=request.smtp_host,
        smtp_port=request.smtp_port,
        smtp_username=request.smtp_username or request.email,
        smtp_password=request.smtp_password,
        imap_host=request.imap_host,
        imap_port=request.imap_port,
        imap_username=request.imap_username or request.email,
        imap_password=request.imap_password,
        provider=request.provider,
        is_primary=request.is_primary,
        daily_send_limit=request.daily_send_limit,
    )


@router.get("/{account_id}")
async def get_mailbox(account_id: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = EmailAccountService(db)
    return await service.get_account(account_id, workspace.id)


@router.post("/{account_id}/test")
async def test_connection(account_id: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = EmailAccountService(db)
    return await service.test_connection(account_id, workspace.id)


@router.delete("/{account_id}")
async def delete_mailbox(account_id: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = EmailAccountService(db)
    await service.delete_account(account_id, workspace.id)
    return {"message": "Mailbox deleted"}
