"""
Request ID Middleware
Equivalent to: backend/src/middleware/requestId.ts
"""

import uuid
from starlette.requests import Request
from starlette.responses import Response


class RequestIdMiddleware:
    """Attach a unique request ID to every request for tracing."""

    async def __call__(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response
