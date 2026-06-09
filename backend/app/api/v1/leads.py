from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.repositories.lead import LeadRepository, LeadListRepository
from app.services.lead.lead_import_service import LeadImportService

router = APIRouter(prefix="/leads", tags=["Leads"])


class LeadCreateRequest(BaseModel):
    email: str
    first_name: str = None
    last_name: str = None
    company: str = None
    website: str = None
    country: str = None
    list_id: str = None


@router.get("/")
async def list_leads(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db),
                     skip: int = 0, limit: int = 100):
    repo = LeadRepository(db)
    leads = await repo.get_all(workspace_id=workspace.id, skip=skip, limit=limit)
    return [
        {
            "id": str(l.id),
            "email": l.email,
            "first_name": l.first_name,
            "last_name": l.last_name,
            "company": l.company,
            "country": l.country,
            "status": l.status,
            "quality_score": l.quality_score,
            "validation_status": l.validation_status,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in leads
    ]


@router.post("/")
async def create_lead(request: LeadCreateRequest, workspace=Depends(get_current_workspace),
                      db: AsyncSession = Depends(get_db)):
    repo = LeadRepository(db)
    lead = await repo.create(
        workspace_id=workspace.id,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        company=request.company,
        website=request.website,
        country=request.country,
        list_id=request.list_id,
    )
    return {"id": str(lead.id), "email": lead.email}


@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...), workspace=Depends(get_current_workspace),
                     db: AsyncSession = Depends(get_db)):
    service = LeadImportService(db)
    return await service.import_csv(file, workspace.id)


@router.post("/import/manual")
async def import_manual(leads: List[LeadCreateRequest], workspace=Depends(get_current_workspace),
                        db: AsyncSession = Depends(get_db)):
    repo = LeadRepository(db)
    imported = []
    for lead in leads:
        existing = await repo.get_by_email(lead.email, workspace.id)
        if not existing:
            l = await repo.create(
                workspace_id=workspace.id,
                email=lead.email,
                first_name=lead.first_name,
                last_name=lead.last_name,
                company=lead.company,
                website=lead.website,
                country=lead.country,
                list_id=lead.list_id,
            )
            imported.append({"id": str(l.id), "email": l.email})
    return {"imported": len(imported), "leads": imported}


@router.get("/lists")
async def list_lists(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = LeadListRepository(db)
    lists = await repo.get_all(workspace_id=workspace.id)
    return [{"id": str(l.id), "name": l.name, "lead_count": l.lead_count} for l in lists]


@router.post("/lists")
async def create_list(name: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = LeadListRepository(db)
    lst = await repo.create(workspace_id=workspace.id, name=name)
    return {"id": str(lst.id), "name": lst.name}
