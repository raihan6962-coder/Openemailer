from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    decode_token, generate_password_reset_token, generate_verification_token,
    encrypt_value, decrypt_value,
)
from app.core.config import settings
from app.repositories.user import UserRepository, SessionRepository, DeviceRepository, PasswordResetRepository
from app.repositories.workspace import WorkspaceRepository, WorkspaceMemberRepository
from app.models.user import User, Session
from app.models.workspace import Workspace
from app.core.exceptions import (
    UnauthorizedException, ConflictException, NotFoundException, ValidationException,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
        self.device_repo = DeviceRepository(db)
        self.password_reset_repo = PasswordResetRepository(db)
        self.workspace_repo = WorkspaceRepository(db)
        self.workspace_member_repo = WorkspaceMemberRepository(db)

    async def register(self, email: str, password: str, full_name: str, workspace_name: str = None) -> dict:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictException("Email already registered")

        password_hash = get_password_hash(password)
        verification_token = generate_verification_token()

        user = await self.user_repo.create(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            verification_token=verification_token,
            role="owner",
        )

        ws_name = workspace_name or f"{full_name}'s Workspace"
        slug = ws_name.lower().replace(" ", "-").replace("'", "")[:200]

        workspace = await self.workspace_repo.create(
            name=ws_name,
            slug=slug,
        )

        await self.workspace_member_repo.create(
            workspace_id=workspace.id,
            user_id=user.id,
            role="owner",
        )

        return {
            "user_id": str(user.id),
            "workspace_id": str(workspace.id),
            "email": user.email,
            "verification_token": verification_token,
        }

    async def login(self, email: str, password: str, ip_address: str = None, user_agent: str = None) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user or not user.password_hash:
            raise UnauthorizedException("Invalid email or password")
        if not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_verified:
            raise UnauthorizedException("Email not verified")
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        workspace = await self.workspace_repo.get_active_workspace(user.id)
        workspace_id = str(workspace.id) if workspace else None

        access_token = create_access_token(str(user.id), workspace_id=workspace_id)
        refresh_token = create_refresh_token(str(user.id))

        await self.session_repo.create(
            user_id=user.id,
            token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes),
        )

        await self.user_repo.update_last_login(user.id, ip_address)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "workspace_id": workspace_id,
            },
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        workspace = await self.workspace_repo.get_active_workspace(user.id)
        workspace_id = str(workspace.id) if workspace else None

        access_token = create_access_token(str(user.id), workspace_id=workspace_id)
        new_refresh_token = create_refresh_token(str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    async def verify_email(self, token: str) -> bool:
        user = await self.user_repo.get_by_verification_token(token)
        if not user:
            raise NotFoundException("Invalid verification token")
        await self.user_repo.verify_email(user.id)
        return True

    async def forgot_password(self, email: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return {"message": "If the email exists, a reset link has been sent"}

        token = generate_password_reset_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        await self.password_reset_repo.create(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )

        return {"message": "If the email exists, a reset link has been sent", "reset_token": token}

    async def reset_password(self, token: str, new_password: str) -> bool:
        reset = await self.password_reset_repo.get_by_token(token)
        if not reset or reset.used_at or reset.expires_at < datetime.now(timezone.utc):
            raise ValidationException("Invalid or expired reset token")

        password_hash = get_password_hash(new_password)
        await self.user_repo.update(reset.user_id, password_hash=password_hash)
        await self.password_reset_repo.update(reset.id, used_at=datetime.now(timezone.utc))
        return True

    async def logout(self, user_id: UUID) -> bool:
        await self.session_repo.invalidate_user_sessions(user_id)
        return True
