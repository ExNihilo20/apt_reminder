from fastapi import Depends
from app.db.dependencies import get_db
from app.repositories.contact_repository import ContactRepository

def get_contact_repository(
    db=Depends(get_db),
) -> ContactRepository:
    return ContactRepository(db.contacts)