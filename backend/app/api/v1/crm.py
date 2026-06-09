from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.services.crm.crm_service import CRMService
from app.repositories.crm import CRMContactRepository, CRMDealRepository

router = APIRouter(prefix="/crm", tags=["CRM"])


class PipelineCreateRequest(BaseModel):
    name: str
    stages: list = None


class DealCreateRequest(BaseModel):
    pipeline_id: str
    contact_id: str
    name: str
    value: float = 0


@router.get("/contacts")
async def list_contacts(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = CRMContactRepository(db)
    contacts = await repo.get_all(workspace_id=workspace.id)
    return [
        {
            "id": str(c.id),
            "email": c.email,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "company": c.company,
            "job_title": c.job_title,
            "lead_score": c.lead_score,
            "lead_status": c.lead_status,
        }
        for c in contacts
    ]


@router.get("/pipelines")
async def list_pipelines(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    service = CRMService(db)
    return await service.get_pipelines(workspace.id)


@router.post("/pipelines")
async def create_pipeline(request: PipelineCreateRequest, workspace=Depends(get_current_workspace),
                          db: AsyncSession = Depends(get_db)):
    service = CRMService(db)
    return await service.create_pipeline(workspace.id, request.name, request.stages)


@router.get("/deals")
async def list_deals(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = CRMDealRepository(db)
    deals = await repo.get_all(workspace_id=workspace.id)
    return [
        {
            "id": str(d.id),
            "name": d.name,
            "value": d.value,
            "probability": d.probability,
            "status": d.status,
            "stage_id": str(d.stage_id) if d.stage_id else None,
        }
        for d in deals
    ]


@router.post("/deals")
async def create_deal(request: DealCreateRequest, workspace=Depends(get_current_workspace),
                      db: AsyncSession = Depends(get_db)):
    service = CRMService(db)
    return await service.create_deal(
        workspace_id=workspace.id,
        pipeline_id=request.pipeline_id,
        contact_id=request.contact_id,
        name=request.name,
        value=request.value,
    )


@router.post("/deals/{deal_id}/move/{stage_id}")
async def move_deal(deal_id: str, stage_id: str, workspace=Depends(get_current_workspace),
                    db: AsyncSession = Depends(get_db)):
    service = CRMService(db)
    return await service.move_deal_stage(deal_id, stage_id, workspace.id)
