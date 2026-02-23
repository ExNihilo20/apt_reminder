from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from typing import List

from app.models.contact import ContactCreate, ContactOut, PaginatedContacts, ContactUpdate
from app.repositories.contact_repository import ContactRepository
from app.repositories.dependencies import get_contact_repository
from app.core.exceptions import *

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"]
)

@router.post("", response_model=ContactOut, status_code=201)
def create_contact(
        contact: ContactCreate,
        repo: ContactRepository = Depends(get_contact_repository),
):
    now = datetime.utcnow()
    contact_doc = contact.model_dump()
    contact_doc["created_at"] = now
    contact_doc["updated_at"] = now

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

@router.get("", response_model=PaginatedContacts)
def get_contacts(
     skip: int = Query(0, ge=0),
     limit: int = Query(20, ge=1, le=100),
     is_active: bool = Query(True),
     repo: ContactRepository = Depends(get_contact_repository)   
):
    contacts = repo.get_contacts(
        skip=skip,
        limit=limit,
        is_active=is_active
    )
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

@router.delete("/deactivate/{contact_id}", status_code=204)
def deactivate_contact(
    contact_id: str,
    repo: ContactRepository = Depends(get_contact_repository),
    ):
    deleted = repo.soft_delete_contact(contact_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found or contact not deactivated")

@router.delete("/delete/{contact_id}", status_code=204)
def delete_contact(
    contact_id: str,
    repo: ContactRepository = Depends(get_contact_repository),
    ) -> None:
    try:
        repo.hard_delete_contact(contact_id)
    except InvalidContactId:
        raise HTTPException(status_code=404, detail="Invalid contact Id")
    except ContactNotFound:
        raise HTTPException(status_code=404, detail="Contact not found")
    except ContactDeleteFailed:
        raise HTTPException(status_code=500, detail="Failed to delete contact")

    return None

@router.patch("/{contact_id}", response_model=ContactOut)
def patch_contact(
    contact_id: str,
    updates: ContactUpdate,
    repo: ContactRepository = Depends(get_contact_repository)
    ):
    update_data = updates.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided")
    
    updated = repo.update_contact(contact_id, update_data)

    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return updated