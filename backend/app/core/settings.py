from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configuration settings for the application.

    Defines all environment-specific configuration values loaded from environment variables
    or a .env file. This class serves as the single source of truth for configuration
    across the application. It supports different environments (dev, uat, prod) and
    centralizes database, logging, and application settings.

    Attributes:
        app_name (str): The name of the application. Defaults to "Appointment Reminder API".
        environment (str): The current environment (e.g., dev, uat, prod). Defaults to "dev".
        mongo_uri (str): MongoDB connection string. Loaded from environment, required.
        mongo_db_name (str): Name of the MongoDB database. Defaults to "reminder".
        log_level (str): Logging verbosity level. Defaults to "INFO".
    """
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