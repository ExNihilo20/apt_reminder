from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class CreateContact(BaseModel):
    firstname: str = Field(..., min_length=1)
    lastname: str = Field(..., min_length=1)
    phone_number: str = Field(..., min_length=7)
    email_address: Optional[EmailStr] = None

class ContactResponse(BaseModel):
    firstname:str
    lastname:str
    phone_number:str
    email_address: Optional[EmailStr]
    created_at: datetime
