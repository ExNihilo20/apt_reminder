from fastapi import FastAPI, HTTPException
import os
from pymongo import MongoClient
import logging
import time
from typing import List
from app.logging_config import setup_logging
from app.middleware.request_logging import request_logging_middleware
from app.repositories.contact_repository import ContactRepository
from app.models.contact import CreateContact, ContactResponse

APP_START_TIME = time.time()

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Appointment Reminder API")

app.middleware("http")(request_logging_middleware)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database()
# wiring Mongo connection
contacts_collection = db["contacts"]
contact_repo = ContactRepository(contacts_collection)

def check_mongo_health():
    start = time.time()
    try:
        # lightweight health check for DB
        client.admin.command("ping")
        latency_ms = (time.time() - start) * 1000
        return {
            "status": "up",
            "latency_ms": round(latency_ms, 2)
        }
    except Exception as e:
        logger.exception("MongoDB health check failed")
        return {
            "status": "down",
            "error": str(e)
        }

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

@app.get("/health/detailed")
def detailed_health_check():
    uptime_seconds = round(time.time() - APP_START_TIME, 2)

    mongo_health = check_mongo_health()

    overall_status = "ok" if mongo_health["status"] == "up" else "degraded"

    logger.info(
        "Health check detailed status=%s mongo_status=%s uptime=%.2fs",
        overall_status,
        mongo_health["status"],
        uptime_seconds
    )

    return {
        "status": overall_status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        "uptime_seconds": uptime_seconds,
        "dependencies": {
            "mongo": mongo_health
        }
    }

@app.post("/contacts", response_model=ContactResponse, status_code=201)
def create_contact(contact: CreateContact):
    logger.info(
        "Creating contact firstname=%s lastname=%s phone=%s",
        contact.firstname,
        contact.lastname,
        contact.phone_number
    )

    contact_dict = contact.dict()

    # Normalize phone number
    contact_dict["phone_number"] = "".join(
        filter(str.isdigit, contact_dict["phone_number"])
    )

    created = contact_repo.create_contact(contact_dict)

    return created

@app.get("/contacts", response_model=List[ContactResponse])
def get_all_contacts():
    logger.info("Retrieving all contacts")

    contacts = contact_repo.get_all_contacts()
    return contacts