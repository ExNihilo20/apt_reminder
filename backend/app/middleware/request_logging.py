import logging
import time
import uuid
from fastapi import Request

logger = logging.getLogger("api.request")

async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    response = None
    try:
        response = await call_next(request)
        return response
    except Exception:
        logger.exception(
            "request_id=%s method=%s path=%s unhandled exception",
            request_id,
            request.method,
            request.url.path
        )
        raise
    finally:
        process_time = (time.time() - start_time) * 1000
        status_code = response.status_code if response else 500
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%.2f client_ip=%s",
            request_id,
            request.method,
            request.url.path,
            status_code,
            process_time,
            client_ip
        )

        if response:
            response.headers["X-Request-ID"] = request_id
