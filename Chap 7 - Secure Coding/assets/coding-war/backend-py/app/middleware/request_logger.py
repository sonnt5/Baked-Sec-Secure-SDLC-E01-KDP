"""
Request Logger Middleware
Equivalent to: backend/src/middleware/requestLogger.ts
"""

import time
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logger import get_logger

logger = get_logger("request")


class RequestLoggerMiddleware:
    """Log every request with method, path, status code, and duration."""

    async def __call__(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        request_id = getattr(request.state, "request_id", "unknown")

        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            request_id=request_id,
            ip=request.client.host if request.client else "unknown",
        )

        return response
