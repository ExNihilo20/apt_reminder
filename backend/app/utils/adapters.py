from app.models.contact_transitional import ContactPublic

def contact_doc_to_public(doc: dict) -> ContactPublic:
    return ContactPublic(
         id=str(doc["_id"]),
        firstname=doc["firstname"],
        lastname=doc["lastname"],
        phone=doc.get("phone"),
        email=doc.get("email"),
        name=f'{doc["firstname"]} {doc["lastname"]}',
        is_active=doc.get("is_active", True),
        created_at=doc["created_at"],
    )