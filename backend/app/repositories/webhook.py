from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook import Webhook, WebhookLog
from app.repositories.base import BaseRepository


class WebhookRepository(BaseRepository[Webhook]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Webhook)


class WebhookLogRepository(BaseRepository[WebhookLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, WebhookLog)
