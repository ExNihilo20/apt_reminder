from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.message import (
    MessageCreate,
    MessageOut,
    PaginatedMessages,
)
from app.repositories.dependencies import (
    get_message_repository,
    get_contact_repository,
)
from app.services.messaging.template_renderer import (
    TemplateRenderer,
    TemplateRenderingError,
)
from app.repositories.message_template_repository import MessageTemplateRepository
from app.repositories.dependencies import get_message_template_repository
from app.repositories.message_repository import MessageRepository
from app.repositories.contact_repository import ContactRepository
from app.services.messaging.providers.twilio_provider import TwilioProvider
from app.services.messaging.providers.base import MessageProviderError


router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("", response_model=MessageOut)
def create_message(
    payload: MessageCreate,
    message_repo: MessageRepository = Depends(get_message_repository),
    contact_repo: ContactRepository = Depends(get_contact_repository),
    template_repo: MessageTemplateRepository = Depends(get_message_template_repository),
):
    # Validate contact
    contact = contact_repo.get_by_id(payload.contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    rendered_body = None

    # If using template
    if payload.template_id:
        template = template_repo.get_by_id(payload.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        try:
            rendered_body = TemplateRenderer.render(
                template["body"],
                payload.variables,
            )
        except TemplateRenderingError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # If raw body provided
    elif payload.body:
        rendered_body = payload.body

    else:
        raise HTTPException(
            status_code=400,
            detail="Either template_id or body must be provided"
        )

    message_data = payload.dict()
    message_data["rendered_body"] = rendered_body

    return message_repo.create(message_data)


@router.get("", response_model=PaginatedMessages)
def list_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    repo: MessageRepository = Depends(get_message_repository),
):
    items, total = repo.list(skip, limit)
    return {"items": items, "total": total}


@router.get("/{message_id}", response_model=MessageOut)
def get_message(
    message_id: str,
    repo: MessageRepository = Depends(get_message_repository),
):
    message = repo.get_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.post("/{message_id}/send", response_model=MessageOut)
def send_message(
    message_id: str,
    message_repo: MessageRepository = Depends(get_message_repository),
    contact_repo: ContactRepository = Depends(get_contact_repository),
):
    message = message_repo.get_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message["status"] != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending messages can be sent",
        )

    contact = contact_repo.get_by_id(message["contact_id"])
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if not message.get("rendered_body"):
        raise HTTPException(
            status_code=400,
            detail="Message has no rendered body",
        )

    provider = TwilioProvider()

    try:
        result = provider.send(
            to=contact["phone_number"],
            body=message["rendered_body"],
        )
    except MessageProviderError as e:
        message_repo.update_status(
            message_id,
            status="failed",
        )
        raise HTTPException(status_code=500, detail=str(e))

    return message_repo.update_status(
        message_id,
        status="sent",
        provider=result["provider"],
        provider_message_sid=result["provider_message_sid"],
    )