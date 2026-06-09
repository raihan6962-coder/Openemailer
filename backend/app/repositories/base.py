from typing import Optional, TypeVar, Generic, Any, List, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: AsyncSession, model: type[ModelType]):
        self.db = db
        self.model = model

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100, workspace_id: Optional[UUID] = None) -> List[ModelType]:
        query = select(self.model)
        if workspace_id and hasattr(self.model, "workspace_id"):
            query = query.where(self.model.workspace_id == workspace_id)
        query = query.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        kwargs["updated_at"] = func.now()
        query = update(self.model).where(self.model.id == id).values(**kwargs).returning(self.model)
        result = await self.db.execute(query)
        await self.db.flush()
        return result.scalar_one_or_none()

    async def delete(self, id: UUID, soft: bool = True) -> bool:
        if soft and hasattr(self.model, "is_active"):
            query = update(self.model).where(self.model.id == id).values(is_active=False, updated_at=func.now())
        else:
            query = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        await self.db.flush()
        return result.rowcount > 0

    async def count(self, workspace_id: Optional[UUID] = None) -> int:
        query = select(func.count(self.model.id))
        if workspace_id and hasattr(self.model, "workspace_id"):
            query = query.where(self.model.workspace_id == workspace_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def bulk_create(self, items: List[Dict[str, Any]]) -> List[ModelType]:
        instances = [self.model(**item) for item in items]
        self.db.add_all(instances)
        await self.db.flush()
        for instance in instances:
            await self.db.refresh(instance)
        return instances
