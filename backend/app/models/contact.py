# app/models/contact.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    firstname: str = Field(..., min_length=1)
    lastname: str = Field(..., min_length=1)
    phone_number: str = Field(
        ...,
        pattern=r"^\d{10}$",
        description="10-digit phone number, digits only"
    )
    email_address: Optional[EmailStr] = None
    
class ContactOut(ContactCreate):
    id: str
    created_at: datetime