from fastapi import APIRouter, Depends, HTTPException, Path, Request
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from typing import List

from app.models.contact import ContactCreate, ContactOut
from app.repositories.contact_repository import ContactRepository

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"]
)


@router.post("", response_model=ContactOut, status_code=201)

def get_repo(request: Request) -> ContactRepository:
    db = request.app.state.db
    return ContactRepository(db.contacts)

def create_contact(
        contact: ContactCreate,
        request: Request,
):
    repo = get_repo(request)

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
def get_contacts(request: Request,):
    repo = get_repo(request)
    contacts = repo.get_all_contacts()
    return contacts

@router.get("/{contact_id}", response_model=ContactOut)
def get_contact_by_id(
    request: Request,
    contact_id: str = Path(..., description="Contact ID"),
):
    repo = get_repo(request)
    contact = repo.get_by_id(contact_id)

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return contact
