from pymongo import MongoClient
from app.core.settings import Settings


def create_mongo_client(settings: Settings) -> MongoClient:
    """
    Create a MongoDB client using the provided settings.

    This function initializes a MongoClient instance with the MongoDB URI from settings.
    The client is designed to be reused across the application (e.g., via FastAPI dependency injection)
    and should be closed during application shutdown using close_mongo_client.

    Args:
        settings (Settings): Application settings containing the mongo_uri.

    Returns:
        MongoClient: An instance of PyMongo's MongoClient connected to the specified URI.
    """
    return MongoClient(settings.mongo_uri)


def close_mongo_client(client: MongoClient) -> None:
    """
    Close the given MongoDB client.

    Safely closes all connections associated with the MongoClient instance.
    This should be called once when the application shuts down.

    Args:
        client (MongoClient): The MongoClient instance to close.
    """
    client.close()
