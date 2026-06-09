from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automation import Automation, AutomationTrigger, AutomationAction, AutomationRun, AutomationRunLog
from app.repositories.base import BaseRepository


class AutomationRepository(BaseRepository[Automation]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Automation)


class AutomationTriggerRepository(BaseRepository[AutomationTrigger]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AutomationTrigger)


class AutomationActionRepository(BaseRepository[AutomationAction]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AutomationAction)


class AutomationRunRepository(BaseRepository[AutomationRun]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AutomationRun)


class AutomationRunLogRepository(BaseRepository[AutomationRunLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AutomationRunLog)
