from fastapi import FastAPI
import os
from pymongo import MongoClient
import logging

from app.logging_config import setup_logging
from app.middleware.request_logging import request_logging_middleware

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Appointment Reminder API")

app.middleware("http")(request_logging_middleware)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database()

@app.on_event("startup")
def startup_event():
    logger.info("Application startup")
    logger.info("Connected to MongoDB database: %s", db.name)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": db.name
    }

