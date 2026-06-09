from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, Session, Device, PasswordReset
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_verification_token(self, token: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.verification_token == token))
        return result.scalar_one_or_none()

    async def verify_email(self, user_id: UUID) -> Optional[User]:
        from sqlalchemy.sql import func
        from datetime import datetime, timezone
        return await self.update(user_id, is_verified=True, verified_at=datetime.now(timezone.utc), verification_token=None)

    async def update_last_login(self, user_id: UUID, ip_address: str) -> Optional[User]:
        from sqlalchemy.sql import func
        from datetime import datetime, timezone
        return await self.update(user_id, last_login_at=datetime.now(timezone.utc), last_login_ip=ip_address)


class SessionRepository(BaseRepository[Session]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Session)

    async def get_by_token(self, token: str) -> Optional[Session]:
        result = await self.db.execute(select(Session).where(Session.token == token))
        return result.scalar_one_or_none()

    async def get_active_sessions(self, user_id: UUID) -> list[Session]:
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id, Session.is_active == True)
        )
        return list(result.scalars().all())

    async def invalidate_user_sessions(self, user_id: UUID) -> None:
        from sqlalchemy import update
        await self.db.execute(
            update(Session).where(Session.user_id == user_id).values(is_active=False)
        )
        await self.db.flush()


class DeviceRepository(BaseRepository[Device]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Device)


class PasswordResetRepository(BaseRepository[PasswordReset]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, PasswordReset)

    async def get_by_token(self, token: str) -> Optional[PasswordReset]:
        result = await self.db.execute(select(PasswordReset).where(PasswordReset.token == token))
        return result.scalar_one_or_none()
