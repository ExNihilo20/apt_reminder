from datetime import datetime
from pymongo.collection import Collection
from bson import ObjectId
from bson.errors import InvalidId

class ContactRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    
    def _to_public(self, doc: dict) -> dict:
        doc["id"] = str(doc.pop("_id"))
        return doc


    def create_contact(self, contact_data: dict) -> dict:
        result = self.collection.insert_one(contact_data)
        doc = self.collection.find_one({"_id": result.inserted_id})
        return self._to_public(doc)

    
    def get_all_contacts(self) ->list[dict]:
        docs = list(self.collection.find({}))
        return [self._to_public(doc) for doc in docs]
    
    def get_by_id(self, contact_id: str) -> dict | None:
        try:
            oid = ObjectId(contact_id)
        except InvalidId:
            return None

        doc = self.collection.find_one({"_id": oid})
        if doc:
            return self._to_public(doc)
        return None

    
    def get_by_phone_number(self, phone_number: str) -> dict | None:
        doc = self.collection.find_one({"phone_number": phone_number})
        if doc:
            return self._to_public(doc)
        return None

    
    def get_by_name(self, firstname: str, lastname:str) -> list[dict]:
        docs = list(
            self.collection.find(
                {"firstname": firstname, "lastname": lastname}
            )
        )
        return [self._to_public(doc) for doc in docs]
    
    def update_contact(self, contact_id: str, updates: dict):
        try:
            oid = ObjectId(contact_id)
        except InvalidId:
            return None

        # Never allow these to be updated
        updates.pop("id", None)
        updates.pop("_id", None)

        result = self.collection.find_one_and_update(
            {"_id": oid, "is_active": True},
            {"$set": updates},
            return_document=True,
        )

        if not result:
            return None

        result["id"] = str(result["_id"])
        return result

    def soft_delete_contact(self, contact_id: str) -> bool:
        try:
            oid = ObjectId(contact_id)
        except InvalidId:
            return False

        result = self.collection.update_one(
            {"_id": oid, "is_active": True},
            {"$set": {"is_active": False}},
        )

        return result.modified_count == 1
