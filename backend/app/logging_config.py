import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "/logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] "
        "%(name)s:%(lineno)d - %(message)s"
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=100 * 1024 * 1024, # 100MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Prevent duplicate logs on reload
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)