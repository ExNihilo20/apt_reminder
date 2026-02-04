# This is part of a transition from dict-based model
# to a Pydantic model
from pydantic import BaseModel
from typing import Optional
from datetime import datetime



class ContactCreate(BaseModel):
    firstname: str
    lastname: str
    phone: Optional[str] = None
    email: Optional[str] = None

class ContactPublic(BaseModel):
    id: str
    firstname: str
    lastname: str
    phone: Optional[str]
    email: Optional[str]
    name: str
    is_active: bool
    created_at: datetime

