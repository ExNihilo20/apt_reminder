from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    contact_id: str
    channel: str = Field(default="sms", description="sms | email")
    body: Optional[str] = None
    variables: Optional[Dict[str, str]] = None


class MessageCreate(MessageBase):
    pass


class MessageOut(MessageBase):
    id: str
    status: str
    provider: Optional[str] = None
    provider_message_sid: Optional[str] = None
    rendered_body: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PaginatedMessages(BaseModel):
    items: list[MessageOut]
    total: int