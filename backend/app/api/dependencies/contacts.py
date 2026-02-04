from app.db.mongo import get_contacts_collection
from app.repositories.contact_repository import ContactRepository


def get_contact_repository() -> ContactRepository:
    collection = get_contacts_collection()
    return ContactRepository(collection)
