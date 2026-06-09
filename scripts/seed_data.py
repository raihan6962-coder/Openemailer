"""
Seed script to populate default billing plans and initial data.
Run: python -m scripts.seed_data
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.base import Base
from app.models.billing import BillingPlan
from app.models.user import User


async def seed():
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        plans = [
            BillingPlan(
                name="Free",
                code="free",
                description="For individuals getting started",
                price_monthly=0,
                price_yearly=0,
                max_users=1,
                max_leads=500,
                max_campaigns=5,
                max_mailboxes=2,
                max_domains=1,
                features={
                    "email_validation": True,
                    "basic_analytics": True,
                    "csv_import": True,
                },
            ),
            BillingPlan(
                name="Starter",
                code="starter",
                description="For growing businesses",
                price_monthly=29,
                price_yearly=290,
                max_users=3,
                max_leads=5000,
                max_campaigns=20,
                max_mailboxes=5,
                max_domains=3,
                features={
                    "email_validation": True,
                    "advanced_analytics": True,
                    "api_access": True,
                    "warmup": True,
                    "spam_recovery": True,
                },
            ),
            BillingPlan(
                name="Growth",
                code="growth",
                description="For scaling teams",
                price_monthly=79,
                price_yearly=790,
                max_users=10,
                max_leads=50000,
                max_campaigns=100,
                max_mailboxes=20,
                max_domains=10,
                features={
                    "email_validation": True,
                    "advanced_analytics": True,
                    "api_access": True,
                    "warmup": True,
                    "spam_recovery": True,
                    "crm": True,
                    "automation": True,
                    "team_collaboration": True,
                },
            ),
            BillingPlan(
                name="Agency",
                code="agency",
                description="For agencies and enterprises",
                price_monthly=199,
                price_yearly=1990,
                max_users=50,
                max_leads=500000,
                max_campaigns=500,
                max_mailboxes=100,
                max_domains=50,
                features={
                    "email_validation": True,
                    "advanced_analytics": True,
                    "api_access": True,
                    "warmup": True,
                    "spam_recovery": True,
                    "crm": True,
                    "automation": True,
                    "team_collaboration": True,
                    "white_label": True,
                    "dedicated_support": True,
                },
            ),
        ]

        for plan in plans:
            session.add(plan)

        await session.commit()
        print("Default billing plans seeded successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
