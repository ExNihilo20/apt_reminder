from datetime import datetime
from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection


class MessageRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    def _to_public(self, doc: dict) -> dict:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        return doc

    def create(self, data: dict) -> dict:
        now = datetime.utcnow()

        data["status"] = "pending"
        data["provider"] = None
        data["provider_message_sid"] = None
        data["rendered_body"] = None
        data["created_at"] = now
        data["updated_at"] = now

        result = self.collection.insert_one(data)
        doc = self.collection.find_one({"_id": result.inserted_id})
        return self._to_public(doc)

    def get_by_id(self, message_id: str) -> Optional[dict]:
        doc = self.collection.find_one({"_id": ObjectId(message_id)})
        return self._to_public(doc) if doc else None

    def list(self, skip: int = 0, limit: int = 20):
        cursor = self.collection.find().skip(skip).limit(limit)
        items = [self._to_public(doc) for doc in cursor]
        total = self.collection.count_documents({})
        return items, total