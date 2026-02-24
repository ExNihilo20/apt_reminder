from fastapi import Depends
from app.db.dependencies import get_db
from app.repositories.contact_repository import ContactRepository
from app.repositories.message_template_repository import MessageTemplateRepository

def get_contact_repository(
    db=Depends(get_db),
) -> ContactRepository:
    return ContactRepository(db.contacts)

def get_message_template_repository(
    db=Depends(get_db)
) -> MessageTemplateRepository:
    return MessageTemplateRepository(db.message_templates) 