from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.crm import (
    CRMContactRepository, CRMCompanyRepository, CRMDealRepository,
    CRMPipelineRepository, CRMPipelineStageRepository, CRMTaskRepository,
    CRMNoteRepository, CRMCommentRepository,
)
from app.repositories.lead import LeadRepository


class CRMService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.contact_repo = CRMContactRepository(db)
        self.company_repo = CRMCompanyRepository(db)
        self.deal_repo = CRMDealRepository(db)
        self.pipeline_repo = CRMPipelineRepository(db)
        self.stage_repo = CRMPipelineStageRepository(db)
        self.task_repo = CRMTaskRepository(db)
        self.note_repo = CRMNoteRepository(db)
        self.activity_repo = CRMCommentRepository(db)
        self.lead_repo = LeadRepository(db)

    async def get_pipelines(self, workspace_id: UUID) -> list:
        return await self.pipeline_repo.get_all(workspace_id=workspace_id)

    async def create_pipeline(self, workspace_id: UUID, name: str, stages: list = None) -> dict:
        pipeline = await self.pipeline_repo.create(workspace_id=workspace_id, name=name)
        if stages:
            for order, stage in enumerate(stages):
                await self.stage_repo.create(
                    pipeline_id=pipeline.id,
                    name=stage.get("name", f"Stage {order + 1}"),
                    order=order,
                    probability=stage.get("probability", 0),
                )
        return {"id": str(pipeline.id), "name": pipeline.name}

    async def create_deal(self, workspace_id: UUID, pipeline_id: UUID, contact_id: UUID,
                           name: str, value: float = 0, **kwargs) -> dict:
        pipeline = await self.pipeline_repo.get_by_id(pipeline_id)
        if not pipeline:
            raise NotFoundException("Pipeline not found")
        stages = await self.stage_repo.get_all(workspace_id=workspace_id)
        first_stage = stages[0] if stages else None

        deal = await self.deal_repo.create(
            workspace_id=workspace_id,
            pipeline_id=pipeline_id,
            contact_id=contact_id,
            stage_id=first_stage.id if first_stage else None,
            name=name,
            value=value,
            **kwargs
        )
        return {"id": str(deal.id), "name": deal.name}

    async def move_deal_stage(self, deal_id: UUID, stage_id: UUID, workspace_id: UUID) -> dict:
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.workspace_id != workspace_id:
            raise NotFoundException("Deal not found")
        stage = await self.stage_repo.get_by_id(stage_id)
        if not stage:
            raise NotFoundException("Stage not found")
        await self.deal_repo.update(deal_id, stage_id=stage_id)
        return {"id": str(deal.id), "stage": stage.name}

    async def create_contact_from_lead(self, workspace_id: UUID, lead_id: UUID) -> dict:
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundException("Lead not found")
        contact = await self.contact_repo.create(
            workspace_id=workspace_id,
            lead_id=lead_id,
            email=lead.email,
            first_name=lead.first_name,
            last_name=lead.last_name,
            company=lead.company,
            website=lead.website,
            country=lead.country,
            phone=lead.phone,
        )
        return {"id": str(contact.id), "email": contact.email}
