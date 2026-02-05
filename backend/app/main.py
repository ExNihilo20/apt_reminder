from fastapi import FastAPI, Request
import logging
import time
from contextlib import asynccontextmanager
from app.core.settings import get_settings
from app.logging_config import setup_logging
from app.middleware.request_logging import request_logging_middleware
from app.api.routes.contacts import router as contacts_router
from app.db.mongo import create_mongo_client, close_mongo_client
from app.db.indexes import ensure_contact_indexes

APP_START_TIME = time.time()

# -------------------------------------------------
# Logging
# -------------------------------------------------
setup_logging()
logger = logging.getLogger(__name__)

# -------------------------------------------------
# App
# -------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # Startup
    client = create_mongo_client(settings)
    app.state.mongo_client = client
    app.state.db = client[settings.mongo_db_name]

    ensure_contact_indexes(app.state.db.contacts)

    yield

    # Shutdown
    close_mongo_client(client)

app = FastAPI(lifespan=lifespan, title="Appointment Reminder API")

app.middleware("http")(request_logging_middleware)

# -------------------------------------------------
# Routers
# -------------------------------------------------
app.include_router(contacts_router)

# -------------------------------------------------
# Health checks
# -------------------------------------------------
def check_mongo_health(request: Request):
    start = time.time()
    try:
        client = request.app.state.mongo_client
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
def detailed_health_check(request: Request):
    uptime_seconds = round(time.time() - APP_START_TIME, 2)

    mongo_health = check_mongo_health(request)
    overall_status = "ok" if mongo_health["status"] == "up" else "degraded"

    return {
        "status": overall_status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        "uptime_seconds": uptime_seconds,
        "dependencies": {
            "mongo": mongo_health
        }
    }

