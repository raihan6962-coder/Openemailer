from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inbox import InboxEmail, InboxLabel, InboxFolder
from app.repositories.base import BaseRepository


class InboxEmailRepository(BaseRepository[InboxEmail]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, InboxEmail)


class InboxLabelRepository(BaseRepository[InboxLabel]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, InboxLabel)


class InboxFolderRepository(BaseRepository[InboxFolder]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, InboxFolder)
