from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_account import EmailAccount, EmailPermission, OAuthToken
from app.repositories.base import BaseRepository


class EmailAccountRepository(BaseRepository[EmailAccount]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, EmailAccount)

    async def get_by_email(self, email: str, workspace_id: UUID) -> Optional[EmailAccount]:
        result = await self.db.execute(
            select(EmailAccount).where(
                and_(
                    EmailAccount.email == email,
                    EmailAccount.workspace_id == workspace_id,
                    EmailAccount.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_active_accounts(self, workspace_id: UUID) -> List[EmailAccount]:
        result = await self.db.execute(
            select(EmailAccount).where(
                and_(
                    EmailAccount.workspace_id == workspace_id,
                    EmailAccount.is_active == True,
                    EmailAccount.status == "active",
                )
            )
        )
        return list(result.scalars().all())

    async def get_primary_account(self, workspace_id: UUID) -> Optional[EmailAccount]:
        result = await self.db.execute(
            select(EmailAccount).where(
                and_(
                    EmailAccount.workspace_id == workspace_id,
                    EmailAccount.is_primary == True,
                    EmailAccount.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()


class EmailPermissionRepository(BaseRepository[EmailPermission]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, EmailPermission)


class OAuthTokenRepository(BaseRepository[OAuthToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, OAuthToken)

    async def get_by_account(self, email_account_id: UUID) -> Optional[OAuthToken]:
        result = await self.db.execute(
            select(OAuthToken).where(OAuthToken.email_account_id == email_account_id)
        )
        return result.scalar_one_or_none()
