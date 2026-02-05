import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.settings import get_settings




def get_log_dir(settings):
    if settings.environment == "dev":
        return Path("./logs")
    return Path("/logs")


def setup_logging() -> None:
    """
    Configure application-wide logging.

    - Application logs respect LOG_LEVEL
    - Noisy third-party libraries are reduced
    - Safe to call multiple times
    """
    settings = get_settings()
    log_dir = get_log_dir(settings)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    log_level = settings.log_level.upper()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Prevent duplicate handlers (important with reload)
    if root_logger.handlers:
        return

    # -----------------------------
    # Handlers
    # -----------------------------
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=100 * 1024 * 1024,  # 100 MB
        backupCount=5,
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # -----------------------------
    # Quiet noisy libraries
    # -----------------------------
    logging.getLogger("pymongo").setLevel(logging.INFO)
    logging.getLogger("pymongo.serverSelection").setLevel(logging.WARNING)

    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    # -----------------------------
    # Explicit app loggers
    # -----------------------------
    logging.getLogger("api.request").setLevel(log_level)
