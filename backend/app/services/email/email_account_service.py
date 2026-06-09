from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encrypt_value, decrypt_value
from app.core.exceptions import ConflictException, NotFoundException
from app.repositories.email_account import EmailAccountRepository, EmailPermissionRepository, OAuthTokenRepository
from app.repositories.workspace import WorkspaceRepository


class EmailAccountService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EmailAccountRepository(db)
        self.permission_repo = EmailPermissionRepository(db)
        self.oauth_repo = OAuthTokenRepository(db)

    async def create_smtp_account(self, workspace_id: UUID, user_id: UUID, email: str, smtp_host: str,
                                   smtp_port: int, smtp_username: str, smtp_password: str,
                                   imap_host: str = None, imap_port: int = None,
                                   imap_username: str = None, imap_password: str = None,
                                   provider: str = "custom", is_primary: bool = False,
                                   daily_send_limit: int = 50) -> dict:
        existing = await self.repo.get_by_email(email, workspace_id)
        if existing:
            raise ConflictException("Email account already exists")

        account = await self.repo.create(
            workspace_id=workspace_id,
            user_id=user_id,
            email=email,
            provider=provider,
            provider_type="smtp",
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password_encrypted=encrypt_value(smtp_password) if smtp_password else None,
            imap_host=imap_host,
            imap_port=imap_port or 993,
            imap_username=imap_username,
            imap_password_encrypted=encrypt_value(imap_password) if imap_password else None,
            is_primary=is_primary,
            daily_send_limit=daily_send_limit,
        )

        return {
            "id": str(account.id),
            "email": account.email,
            "provider": account.provider,
            "status": account.status,
        }

    async def get_account(self, account_id: UUID, workspace_id: UUID) -> Optional[dict]:
        account = await self.repo.get_by_id(account_id)
        if not account or account.workspace_id != workspace_id:
            raise NotFoundException("Email account not found")
        return {
            "id": str(account.id),
            "email": account.email,
            "provider": account.provider,
            "provider_type": account.provider_type,
            "is_verified": account.is_verified,
            "is_primary": account.is_primary,
            "status": account.status,
            "health_score": account.health_score,
            "daily_send_limit": account.daily_send_limit,
            "daily_sent_count": account.daily_sent_count,
        }

    async def list_accounts(self, workspace_id: UUID) -> list:
        accounts = await self.repo.get_all(workspace_id=workspace_id)
        return [
            {
                "id": str(a.id),
                "email": a.email,
                "provider": a.provider,
                "provider_type": a.provider_type,
                "is_verified": a.is_verified,
                "is_primary": a.is_primary,
                "status": a.status,
                "health_score": a.health_score,
            }
            for a in accounts
        ]

    async def delete_account(self, account_id: UUID, workspace_id: UUID) -> bool:
        account = await self.repo.get_by_id(account_id)
        if not account or account.workspace_id != workspace_id:
            raise NotFoundException("Email account not found")
        return await self.repo.delete(account_id)

    async def test_connection(self, account_id: UUID, workspace_id: UUID) -> dict:
        account = await self.repo.get_by_id(account_id)
        if not account or account.workspace_id != workspace_id:
            raise NotFoundException("Email account not found")

        smtp_password = decrypt_value(account.smtp_password_encrypted) if account.smtp_password_encrypted else ""

        import aiosmtplib
        try:
            await aiosmtplib.test(
                hostname=account.smtp_host or "smtp.gmail.com",
                port=account.smtp_port or 587,
                username=account.smtp_username or account.email,
                password=smtp_password,
                start_tls=True,
            )
            return {"status": "success", "message": "SMTP connection successful"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
