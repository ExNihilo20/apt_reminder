from fastapi import FastAPI
import logging
import time

from app.logging_config import setup_logging
from app.middleware.request_logging import request_logging_middleware
from app.api.routes.contacts import router as contacts_router
from app.db.mongo import get_mongo_client
from app.db.indexes import ensure_contact_indexes
from app.db.mongo import get_contacts_collection
from app.config import settings

APP_START_TIME = time.time()

# -------------------------------------------------
# Logging
# -------------------------------------------------
setup_logging()
logger = logging.getLogger(__name__)

# -------------------------------------------------
# App
# -------------------------------------------------
app = FastAPI(title="Appointment Reminder API")

app.middleware("http")(request_logging_middleware)

# -------------------------------------------------
# Routers
# -------------------------------------------------
app.include_router(contacts_router)

# -------------------------------------------------
# Startup
# -------------------------------------------------
@app.on_event("startup")
def startup_event():
    logger.info("Application startup")

    collection = get_contacts_collection()
    ensure_contact_indexes(collection)

    logger.info(
        "Connected to MongoDB database: %s",
        collection.database.name
    )

# -------------------------------------------------
# Health checks
# -------------------------------------------------
def check_mongo_health():
    start = time.time()
    try:
        client = get_mongo_client()
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


@app.get("/health")
def health_check():
    return {
        "status": "ok"
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
