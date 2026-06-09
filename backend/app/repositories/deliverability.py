from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deliverability import DNSCheck, DeliverabilityScore, ReputationScore, BlacklistCheck
from app.repositories.base import BaseRepository


class DNSCheckRepository(BaseRepository[DNSCheck]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DNSCheck)


class DeliverabilityScoreRepository(BaseRepository[DeliverabilityScore]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DeliverabilityScore)


class ReputationScoreRepository(BaseRepository[ReputationScore]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ReputationScore)


class BlacklistCheckRepository(BaseRepository[BlacklistCheck]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, BlacklistCheck)
