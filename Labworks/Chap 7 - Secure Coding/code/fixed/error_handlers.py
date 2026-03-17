# app/core/error_handlers.py — FIXED version
# Lab 7.5: Safe Error Handler (ASVS V16.5)
#
# Two separate channels:
#   External (user-facing): error_code + user-friendly message + correlation ref.
#                           NO stack traces, NO DB details, NO framework info.
#   Internal (log sink):    full technical context for debugging.
#                           NO raw secrets, passwords, tokens, or PII.

import logging
import uuid
from enum import Enum

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Error code vocabulary (ASVS V16.5.1 — generic messages)
# ---------------------------------------------------------------------------
class ErrorCode(str, Enum):
    AUTH_REQUIRED       = "AUTH_REQUIRED"
    AUTH_INVALID        = "AUTH_INVALID"        # same for wrong password AND user not found
    AUTH_LOCKED         = "AUTH_LOCKED"
    AUTH_EXPIRED        = "AUTH_EXPIRED"
    PERMISSION_DENIED   = "PERMISSION_DENIED"   # same as NOT_FOUND for private resources
    VALIDATION_ERROR    = "VALIDATION_ERROR"
    RATE_LIMIT          = "RATE_LIMIT_EXCEEDED"
    NOT_FOUND           = "NOT_FOUND"           # only for public resources
    INTERNAL_ERROR      = "INTERNAL_ERROR"      # generic — never expose details
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


# ---------------------------------------------------------------------------
# External response model — strict field list (ASVS V16.5)
# ---------------------------------------------------------------------------
class ErrorResponse(BaseModel):
    error_code:  ErrorCode
    message:     str            # user-friendly — no internals
    error_ref:   str | None = None   # short correlation ID — not a debug string
    retry_after: int | None = None   # seconds, for 429/503

    # NEVER include: stack_trace, sql_error, file_path, framework_name, db_schema


# ---------------------------------------------------------------------------
# Last-resort exception handler (ASVS V16.5.4)
# ---------------------------------------------------------------------------
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler — ensures no unhandled exception leaks internals.

    Internal log: full technical context (exc type, path, correlation id).
    External response: generic error code + short correlation ref only.
    ASVS V16.5.1: generic message on unexpected/security-sensitive errors.
    ASVS V16.5.3: application fails gracefully and securely.
    ASVS V16.5.4: last-resort error handler defined.
    """
    error_ref = str(uuid.uuid4())[:8]   # 8-char correlation ID for support

    # Internal log: technical context, NO sensitive values
    logger.error(
        "Unhandled exception",
        extra={
            "error_ref":  error_ref,
            "request_id": getattr(request.state, "request_id", None),
            "path":       request.url.path,   # path is OK — query params may contain tokens
            "exc_type":   type(exc).__name__,
            # NO: exc.args, str(exc), traceback — may expose DB details, passwords, paths
        },
    )

    # Traceback only to the internal debug sink, not the main log stream
    logger.debug("Traceback:", exc_info=True)

    # External response: generic — no technical details
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred. Please try again.",
            error_ref=error_ref,   # lets support correlate without exposing details
        ).model_dump(),
    )


# ---------------------------------------------------------------------------
# Error handling decision table (Lab 7.5, Task 1 reference)
# ---------------------------------------------------------------------------
# | Scenario                | HTTP | error_code      | Log level | Key rule            |
# |-------------------------|------|-----------------|-----------|---------------------|
# | User not found at login | 401  | AUTH_INVALID    | WARN      | Same as wrong pwd   |
# | Wrong password at login | 401  | AUTH_INVALID    | WARN      | (enumeration guard) |
# | SQL constraint violation| 409  | VALIDATION_ERROR| ERROR     | No DB details       |
# | JWT expired             | 401  | AUTH_EXPIRED    | INFO      | No token value      |
# | DB connection failure   | 503  | SERVICE_UNAVAIL | ERROR     | No connection str   |
# | Pydantic validation     | 422  | VALIDATION_ERROR| DEBUG     | No raw input values |
