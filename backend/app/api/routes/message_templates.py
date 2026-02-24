from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.message_template import (
    MessageTemplateCreate,
    MessageTemplateOut,
    MessageTemplateUpdate,
    PaginatedMessageTemplates,
)
from app.repositories.dependencies import get_message_template_repository
from app.repositories.message_template_repository import MessageTemplateRepository


router = APIRouter(prefix="/message-templates", tags=["Message Templates"])


@router.post("", response_model=MessageTemplateOut)
def create_template(
    payload: MessageTemplateCreate,
    repo: MessageTemplateRepository = Depends(get_message_template_repository),
):
    existing = repo.get_by_name(payload.name)
    if existing:
        raise HTTPException(status_code=400, detail="Template name already exists")

    return repo.create(payload.dict())


@router.get("", response_model=PaginatedMessageTemplates)
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    repo: MessageTemplateRepository = Depends(get_message_template_repository),
):
    items, total = repo.list(skip, limit)
    return {"items": items, "total": total}


@router.get("/{template_id}", response_model=MessageTemplateOut)
def get_template(
    template_id: str,
    repo: MessageTemplateRepository = Depends(get_message_template_repository),
):
    template = repo.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.patch("/{template_id}", response_model=MessageTemplateOut)
def update_template(
    template_id: str,
    payload: MessageTemplateUpdate,
    repo: MessageTemplateRepository = Depends(get_message_template_repository),
):
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    updated = repo.update(template_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Template not found")
    return updated