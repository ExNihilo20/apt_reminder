from pydantic import BaseModel
import os
from urllib.parse import urlparse


class Settings(BaseModel):
    MONGO_URI: str
    MONGO_DB_NAME: str


def load_settings() -> Settings:
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI is not set")

    parsed = urlparse(mongo_uri)

    # If DB name is included in the URI, use it
    db_name = parsed.path.lstrip("/") or os.getenv(
        "MONGO_DB_NAME", "reminder"
    )

    return Settings(
        MONGO_URI=mongo_uri,
        MONGO_DB_NAME=db_name,
    )


settings = load_settings()
