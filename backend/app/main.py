from fastapi import FastAPI
import os
from pymongo import MongoClient
import logging
import time

from app.logging_config import setup_logging
from app.middleware.request_logging import request_logging_middleware

APP_START_TIME = time.time()

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Appointment Reminder API")

app.middleware("http")(request_logging_middleware)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database()

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

