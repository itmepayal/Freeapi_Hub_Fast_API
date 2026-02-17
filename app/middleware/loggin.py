import time
import uuid
from fastapi import Request
from app.core.logger.logging import logger

async def loggin_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.time()

    logger.info(f"[{request_id}] Request started")

    try:
        response = await call_next(request)

    except Exception as e:
        logger.error(f"[{request_id}] Request failed -> {e}")
        raise

    duration = round((time.time() - start) * 1000, 2)

    logger.info(f"[{request_id}] Request completed in {duration}ms")

    return response
