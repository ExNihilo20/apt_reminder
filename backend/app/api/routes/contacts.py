from fastapi import APIRouter, Depends, HTTPException, Path
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from typing import List

from app.models.contact import ContactCreate, ContactOut
from app.repositories.contact_repository import ContactRepository
from app.repositories.dependencies import get_contact_repository

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"]
)

@router.post("", response_model=ContactOut, status_code=201)
def create_contact(
        contact: ContactCreate,
        repo: ContactRepository = Depends(get_contact_repository),
):
    contact_doc = contact.model_dump()
    contact_doc["created_at"] = datetime.utcnow()

    try:
        created = repo.create_contact(contact_doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="A contact with this phone_number already exists"
        )

    if not created:
        raise HTTPException(
            status_code=500,
            detail="Failed to create contact"
        )

    return created



@router.get("", response_model=List[ContactOut])
def get_contacts(repo: ContactRepository = Depends(get_contact_repository),):
    contacts = repo.get_all_contacts()
    return contacts

@router.get("/{contact_id}", response_model=ContactOut)
def get_contact_by_id(
    contact_id: str = Path(..., description="Contact ID"),
    repo: ContactRepository = Depends(get_contact_repository),
):
    contact = repo.get_by_id(contact_id)

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return contact

@router.put("/{contact_id}", response_model=ContactOut)
def update_contact(
    contact_id: str,
    contact: ContactCreate,
    repo: ContactRepository = Depends(get_contact_repository),
    ):
    updated = repo.update_contact(contact_id, contact.model_dump())

    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")

    return updated

@router.delete("/{contact_id}", status_code=204)
def delete_contact(
    contact_id: str,
    repo: ContactRepository = Depends(get_contact_repository),
    ):
    deleted = repo.soft_delete_contact(contact_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
