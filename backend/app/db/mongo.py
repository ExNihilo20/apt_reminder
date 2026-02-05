from pymongo import MongoClient
from app.core.settings import Settings


def create_mongo_client(settings: Settings) -> MongoClient:
    return MongoClient(settings.mongo_uri)


def close_mongo_client(client: MongoClient) -> None:
    client.close()
