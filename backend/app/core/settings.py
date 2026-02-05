from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "Appointment Reminder API"
    environment: str = Field(default="dev")

    mongo_uri: str = Field(..., description="MongoDB connection string")
    mongo_db_name: str = Field(default="reminder")

    log_level: str = Field(default="INFO")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"