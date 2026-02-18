from fastapi import Request
from pymongo.database import Database

def get_db(request: Request) -> Database:
    """
    Retrieve the shared database instance from the application state.

    This dependency function provides access to the pre-configured MongoDB database
    instance that is attached to the FastAPI application on startup. It is designed
    to be used with FastAPI's dependency injection system and should be injected
    into route handlers that require database access.

    Args:
        request (Request): The incoming FastAPI request, used to access the app state.

    Returns:
        Database: The shared MongoDB database instance.
    """
    return request.app.state.db