from pymongo import MongoClient
from pymongo.collection import Collection

from app.config import settings  # or however you load env vars

_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
    return _client


def get_contacts_collection() -> Collection:
    client = get_mongo_client()
    db = client[settings.MONGO_DB_NAME]
    return db["contacts"]
