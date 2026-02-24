from datetime import datetime
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection


class MessageTemplateRepository:
    def __init__(self, collection:Collection):
        self.collection = collection
    
    def _to_public(self, doc:dict) -> dict:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        return doc

    def create(self, data:dict) -> dict:
        now = datetime.utcnow()
        data["created_at"] = now
        data["updated_at"] = now

        result = self.collection.insert_one(data)
        doc = self.collection.find_one({"_id": result.inserted_id})
        return self._to_public(doc)

    def get_by_id(self, template_id:str) -> Optional[dict]:
        doc = self.collection.find_one({"_id": ObjectId(template_id)})
        return self._to_public(doc) if doc else None
    
    def get_by_name(self, name: str) -> Optional[dict]:
        doc = self.collection.find_one({"name": name})
        return self._to_public(doc) if doc else None

    def list(self, skip: int = 0, limit: int = 20):
        cursor = self.collection.find().skip(skip).limit(limit)
        items = [self._to_public(doc) for doc in cursor]
        total = self.collection.count_documents({})
        return items, total

    def update(self, template_id: str, updates: dict) -> Optional[dict]:
        updates["updated_at"] = datetime.utcnow()

        self.collection.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": updates}
        )

        return self.get_by_id(template_id)