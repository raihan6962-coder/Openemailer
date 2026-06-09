import asyncio
from datetime import datetime, timezone, timedelta
from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app
from app.core.database import async_session_factory

logger = get_task_logger(__name__)


@celery_app.task
def aggregate_daily_analytics():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_aggregate_daily_analytics())


async def _aggregate_daily_analytics():
    from app.repositories.analytics import AnalyticsEventRepository, AnalyticsDailyRepository
    from sqlalchemy import select, func
    from app.models.analytics import AnalyticsEvent

    async with async_session_factory() as db:
        try:
            event_repo = AnalyticsEventRepository(db)
            daily_repo = AnalyticsDailyRepository(db)

            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday = today - timedelta(days=1)

            result = await db.execute(
                select(
                    AnalyticsEvent.workspace_id,
                    AnalyticsEvent.event_type,
                    func.count(AnalyticsEvent.id).label("count"),
                ).where(
                    AnalyticsEvent.occurred_at >= yesterday,
                    AnalyticsEvent.occurred_at < today,
                ).group_by(
                    AnalyticsEvent.workspace_id,
                    AnalyticsEvent.event_type,
                )
            )

            rows = result.all()
            for row in rows:
                await daily_repo.create(
                    workspace_id=row.workspace_id,
                    date=yesterday,
                    metric_type=row.event_type,
                    metric_value=row.count,
                )

            logger.info(f"Aggregated {len(rows)} daily analytics records")

        except Exception as e:
            logger.error(f"Analytics aggregation error: {str(e)}")
