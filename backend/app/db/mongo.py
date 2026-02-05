
from pymongo import MongoClient
from app.core.config import get_settings

_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """
    Lazily create and return a MongoDB client.
    This ensures settings are loaded only when needed.
    """
    global _client

    if _client is None:
        settings = get_settings()
        _client = MongoClient(settings.mongo_uri)

    return _client


def get_database():
    settings = get_settings()
    client = get_mongo_client()
    return client[settings.mongo_db_name]

