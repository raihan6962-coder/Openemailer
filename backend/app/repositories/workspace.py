from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace, WorkspaceMember, WorkspaceInvitation
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Workspace)

    async def get_by_slug(self, slug: str) -> Optional[Workspace]:
        result = await self.db.execute(select(Workspace).where(Workspace.slug == slug))
        return result.scalar_one_or_none()

    async def get_active_workspace(self, user_id: UUID) -> Optional[Workspace]:
        result = await self.db.execute(
            select(Workspace).join(WorkspaceMember).where(
                and_(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.is_active == True,
                    Workspace.is_active == True,
                )
            ).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_user_workspaces(self, user_id: UUID) -> List[Workspace]:
        result = await self.db.execute(
            select(Workspace).join(WorkspaceMember).where(
                and_(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.is_active == True,
                    Workspace.is_active == True,
                )
            )
        )
        return list(result.scalars().all())


class WorkspaceMemberRepository(BaseRepository[WorkspaceMember]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, WorkspaceMember)

    async def get_member(self, workspace_id: UUID, user_id: UUID) -> Optional[WorkspaceMember]:
        result = await self.db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_workspace_members(self, workspace_id: UUID) -> List[WorkspaceMember]:
        result = await self.db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.is_active == True,
                )
            )
        )
        return list(result.scalars().all())


class WorkspaceInvitationRepository(BaseRepository[WorkspaceInvitation]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, WorkspaceInvitation)

    async def get_by_token(self, token: str) -> Optional[WorkspaceInvitation]:
        result = await self.db.execute(select(WorkspaceInvitation).where(WorkspaceInvitation.token == token))
        return result.scalar_one_or_none()
