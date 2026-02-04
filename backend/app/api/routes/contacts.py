from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from app.models.contact import ContactCreate, ContactOut
from app.api.dependencies.contacts import get_contact_repository
from app.repositories.contact_repository import ContactRepository

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"]
)


@router.post("", response_model=ContactOut, status_code=201)
def create_contact(
    contact: ContactCreate,
    repo: ContactRepository = Depends(get_contact_repository),
):
    # Build Mongo document from validated Pydantic model
    contact_doc = contact.model_dump()
    contact_doc["created_at"] = datetime.utcnow()

    # Persist
    created = repo.create_contact(contact_doc)

    if not created:
        raise HTTPException(
            status_code=500,
            detail="Failed to create contact"
        )

    # Repository returns a dict shaped like ContactOut
    return created

@router.get("", response_model=List[ContactOut])
def get_contacts(
    repo: ContactRepository = Depends(get_contact_repository),
):
    contacts = repo.get_all_contacts()
    return contacts