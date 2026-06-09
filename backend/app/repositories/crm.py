from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import CRMContact, CRMCompany, CRMDeal, CRMPipeline, CRMPipelineStage, CRMTask, CRMNote, CRMComment, CRMLeadScore
from app.repositories.base import BaseRepository


class CRMContactRepository(BaseRepository[CRMContact]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CRMContact)


class CRMCompanyRepository(BaseRepository[CRMCompany]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CRMCompany)


class CRMDealRepository(BaseRepository[CRMDeal]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CRMDeal)


class CRMPipelineRepository(BaseRepository[CRMPipeline]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CRMPipeline)


class CRMPipelineStageRepository(BaseRepository[CRMPipelineStage]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CRMPipelineStage)


class CRMTaskRepository(BaseRepository[CRMTask]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CRMTask)


class CRMNoteRepository(BaseRepository[CRMNote]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CRMNote)


class CRMCommentRepository(BaseRepository[CRMComment]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CRMComment)


class CRMLeadScoreRepository(BaseRepository[CRMLeadScore]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CRMLeadScore)
