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

        # Only set defaults if not already provided
        data.setdefault("status", "pending")
        data.setdefault("provider", None)
        data.setdefault("provider_message_sid", None)
        data.setdefault("created_at", now)
        data.setdefault("updated_at", now)

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
    
    def update_status(
        self,
        message_id: str,
        *,
        status: str,
        provider: str | None = None,
        provider_message_sid: str | None = None,
    ):
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow(),
        }

        if provider:
            update_data["provider"] = provider

        if provider_message_sid:
            update_data["provider_message_sid"] = provider_message_sid

        self.collection.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": update_data},
        )

        return self.get_by_id(message_id)