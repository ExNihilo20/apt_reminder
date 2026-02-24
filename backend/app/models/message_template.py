from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class MessageTemplateBase(BaseModel):
    name: str = Field(..., description="Unique template name")
    channel: str = Field(default="sms", description="Channel type (sms for now)")
    language: str = Field(default="en")
    body: str = Field(..., description="Template body using ${var} syntax")
    is_active: bool = True

class MessageTemplateCreate(MessageTemplateBase):
    pass

class MessageTemplateUpdate(BaseModel):
    body: Optional[str] = None
    is_active: Optional[bool] = None

class MessageTemplateOut(MessageTemplateBase):
    id: str
    created_at: datetime
    updated_at: datetime

class PaginatedMessageTemplates(BaseModel):
    items: list[MessageTemplateOut]
    total: int