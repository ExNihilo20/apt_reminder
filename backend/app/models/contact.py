# app/models/contact.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    """
    Schema for creating a new contact.

    This model defines the required and optional fields for creating a contact
    in the system. All fields are validated according to their type and constraints.

    Attributes:
        firstname (str): The contact's first name. Must be at least 1 character long.
        lastname (str): The contact's last name. Must be at least 1 character long.
        phone_number (str): A 10-digit phone number (digits only). Validated via regex pattern.
        email_address (Optional[EmailStr]): The contact's email address. Must be a valid email format if provided.
        is_active (bool): Indicates whether the contact is active. Defaults to True.
    """
    firstname: str = Field(..., min_length=1)
    lastname: str = Field(..., min_length=1)
    phone_number: str = Field(
        ...,
        pattern=r"^\d{10}$",
        description="10-digit phone number, digits only"
    )
    email_address: Optional[EmailStr] = Field(None, alias="email")
    is_active: bool = True

    class Config:
        populate_by_name = True
    
class ContactOut(ContactCreate):
    id: str
    created_at: datetime