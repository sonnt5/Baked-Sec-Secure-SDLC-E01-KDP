"""
Global Error Handler
Equivalent to: backend/src/middleware/errorHandler.ts
SDRD: REQ-1.3, REQ-1.4, REQ-17.1–17.7 (structured error responses)
"""

from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("error_handler")


class AppError(Exception):
    """
    Custom application error.
    Equivalent to: AppError class in errorHandler.ts
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict | list | None = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


def _error_response(
    status_code: int,
    code: str,
    message: str,
    request: Request,
    details: dict | list | None = None,
    error_ref: str | None = None,
) -> JSONResponse:
    """Build a standardized error response."""
    request_id = getattr(request.state, "request_id", "unknown")
    content = {
        "code": code,
        "message": message,
        "details": details,
        "requestId": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if error_ref:
        content["errorRef"] = error_ref
    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(
            "AppError",
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            request_id=request_id,
            path=request.url.path,
            method=request.method,
        )
        return _error_response(
            exc.status_code, exc.code, exc.message, request, exc.details
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        details = [
            {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return _error_response(422, "VALIDATION_ERROR", "Invalid input data", request, details)

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        logger.error("Database integrity error", error=str(exc.orig), path=request.url.path)
        if "unique" in str(exc.orig).lower() or "duplicate" in str(exc.orig).lower():
            return _error_response(409, "CONFLICT", "Resource already exists", request)
        if "foreign key" in str(exc.orig).lower():
            return _error_response(
                400, "BAD_REQUEST", "Invalid reference to related resource", request
            )
        return _error_response(400, "BAD_REQUEST", "Invalid data provided", request)

    @app.exception_handler(NoResultFound)
    async def not_found_handler(request: Request, exc: NoResultFound) -> JSONResponse:
        return _error_response(404, "NOT_FOUND", "Resource not found", request)

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")

        # Log full error with stack trace
        logger.error(
            "Unhandled exception",
            error=str(exc),
            error_type=type(exc).__name__,
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            exc_info=True,
        )

        # Don't expose internal error details in production
        message = (
            "An unexpected error occurred"
            if settings.environment == "production"
            else str(exc)
        )
        return _error_response(500, "INTERNAL_SERVER_ERROR", message, request)
