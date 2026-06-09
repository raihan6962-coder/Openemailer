from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.repositories.template import TemplateRepository

router = APIRouter(prefix="/templates", tags=["Templates"])


class TemplateCreateRequest(BaseModel):
    name: str
    subject: str = None
    body_html: str = None
    body_text: str = None
    template_type: str = "custom"
    category: str = None


@router.get("/")
async def list_templates(workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = TemplateRepository(db)
    templates = await repo.get_all(workspace_id=workspace.id)
    return [
        {
            "id": str(t.id),
            "name": t.name,
            "subject": t.subject,
            "category": t.category,
            "template_type": t.template_type,
            "version": t.version,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in templates
    ]


@router.post("/")
async def create_template(request: TemplateCreateRequest, current_user=Depends(get_current_user),
                          workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = TemplateRepository(db)
    template = await repo.create(
        workspace_id=workspace.id,
        name=request.name,
        subject=request.subject,
        body_html=request.body_html,
        body_text=request.body_text,
        template_type=request.template_type,
        category=request.category,
    )
    return {"id": str(template.id), "name": template.name}


@router.get("/{template_id}")
async def get_template(template_id: str, workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = TemplateRepository(db)
    template = await repo.get_by_id(template_id)
    if not template or template.workspace_id != workspace.id:
        return {"error": "Template not found"}
    return {
        "id": str(template.id),
        "name": template.name,
        "subject": template.subject,
        "body_html": template.body_html,
        "body_text": template.body_text,
        "template_type": template.template_type,
        "category": template.category,
    }


@router.put("/{template_id}")
async def update_template(template_id: str, request: TemplateCreateRequest,
                          workspace=Depends(get_current_workspace), db: AsyncSession = Depends(get_db)):
    repo = TemplateRepository(db)
    template = await repo.update(template_id, **request.dict(exclude_none=True))
    return {"id": str(template.id), "name": template.name}
