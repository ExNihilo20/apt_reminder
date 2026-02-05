from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "Appointment Reminder API"
    environment: str = Field(default="dev")

    # mongo
    mongo_uri: str = Field(..., description="MongoDB connection string")
    mongo_db_name: str = Field(default="reminder")

    # logging
    log_level: str = Field(default="INFO")

    # reading env configs
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()