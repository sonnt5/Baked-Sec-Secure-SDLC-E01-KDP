# app/core/error_handlers.py — FIXED version
# Lab 7.5: Safe Error Handling (ASVS V16.5)
#
# Two separate channels — never mix them:
#   External (client): error_code + user-friendly message + short correlation ref.
#                      No stack traces, DB details, file paths, or framework info.
#   Internal (log):    full technical context for debugging.
#                      No raw secrets, passwords, tokens, or PII.

import logging
import uuid
from enum import Enum

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Error code vocabulary
# ---------------------------------------------------------------------------
# AUTH_INVALID covers BOTH wrong password AND user not found.
# Distinct codes for each would enable user enumeration.
class ErrorCode(str, Enum):
    AUTH_REQUIRED       = "AUTH_REQUIRED"
    AUTH_INVALID        = "AUTH_INVALID"        # wrong password or user not found — same code
    AUTH_LOCKED         = "AUTH_LOCKED"
    AUTH_EXPIRED        = "AUTH_EXPIRED"
    PERMISSION_DENIED   = "PERMISSION_DENIED"
    VALIDATION_ERROR    = "VALIDATION_ERROR"
    RATE_LIMIT          = "RATE_LIMIT_EXCEEDED"
    NOT_FOUND           = "NOT_FOUND"
    INTERNAL_ERROR      = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


# ---------------------------------------------------------------------------
# External response model — fixed field list, no internals allowed
# ---------------------------------------------------------------------------
class ErrorResponse(BaseModel):
    error_code:  ErrorCode
    message:     str                 # user-facing — no technical details
    error_ref:   str | None = None   # short correlation ID for support lookup
    retry_after: int | None = None   # seconds, used for 429 / 503


# ---------------------------------------------------------------------------
# Last-resort exception handler (ASVS V16.5.4)
# ---------------------------------------------------------------------------
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler that never exposes internals to the client.

    Generates a short correlation ID (error_ref) that appears in both
    the internal log and the external response — linking them for support
    without exposing any technical detail to the client.

    Internal log:  exc type + path + error_ref. NOT exc.args, str(exc), traceback.
    External body: INTERNAL_ERROR + generic message + error_ref only.
    ASVS V16.5.1 compliant.
    """
    error_ref = str(uuid.uuid4())[:8]

    # Internal: technical context — no sensitive values
    logger.error(
        "Unhandled exception",
        extra={
            "error_ref":  error_ref,
            "request_id": getattr(request.state, "request_id", None),
            "path":       request.url.path,    # path only — not query params (may hold tokens)
            "exc_type":   type(exc).__name__,
            # NOT: str(exc), exc.args, traceback — may contain DB schema, passwords, paths
        },
    )
    logger.debug("Full traceback:", exc_info=True)  # debug sink only

    # External: generic — no technical detail
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred. Please try again.",
            error_ref=error_ref,
        ).model_dump(),
    )


# ---------------------------------------------------------------------------
# Login: uniform error for both wrong password AND missing user
# ---------------------------------------------------------------------------
# A placeholder for the real DB lookup — demonstrates the enumeration guard.
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$placeholder"


async def login(email: str, password: str, db=None) -> dict:
    """Authenticate a user by email and password.

    Returns the same error code and message whether the email does not
    exist or the password is wrong. This prevents user enumeration.

    Timing note: always runs _verify_password() even when the user does
    not exist (using DUMMY_HASH), so response time does not differ between
    the two cases. A timing difference would re-enable enumeration even
    with identical response bodies.
    ASVS V6.3.3 + V16.5.1 compliant.
    """
    user = None  # placeholder: await db.query(User).filter_by(email=email).first()

    # Always run password check — even for non-existent users.
    # This keeps response time constant regardless of whether the email exists.
    hash_to_check = user.hashed_password if user else DUMMY_HASH
    password_ok = _verify_password(password, hash_to_check)

    if user is None or not password_ok:
        # Same error code and message for both cases — no enumeration signal
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(
                error_code=ErrorCode.AUTH_INVALID,
                message="Invalid email or password.",
            ).model_dump(),
        )

    return {"token": "..."}   # real implementation issues a JWT here


def _verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its stored Argon2id hash."""
    # Placeholder — real implementation uses argon2-cffi or passlib[argon2]
    from passlib.hash import argon2
    return argon2.verify(plain, hashed)
