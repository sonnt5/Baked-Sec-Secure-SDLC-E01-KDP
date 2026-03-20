# app/core/error_handlers.py — VULNERABLE version
# Lab 7.5: Information Leakage via Error Responses (ASVS V16.5)
# DO NOT USE IN PRODUCTION — educational purposes only
#
# Bugs demonstrated:
#   Bug 1: generic_exception_handler() exposes full stack traces in HTTP responses.
#          An attacker can read server file paths, library versions, and DB schema
#          details from any unhandled exception.
#
#   Bug 2: login() returns different error messages for valid vs invalid emails,
#          enabling an attacker to enumerate which email addresses exist in the system.

import traceback

from fastapi import Request
from fastapi.responses import JSONResponse


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last-resort handler for unhandled exceptions.

    BUG (ASVS V16.5.1 violation):
      The full Python traceback is included in the HTTP response body.
      This exposes to any client:
        - Server-side file paths  (/app/repositories/submission_repo.py:147)
        - Library versions        (sqlalchemy 2.0.27 from the import path)
        - Database schema details (table and column names from SQLAlchemy errors)
        - Internal code logic     (which branch was executing when it failed)

      A real consequence: an attacker who can trigger a DB error on
      POST /api/v1/auth/login learns the exact SQL query structure from the
      traceback, making subsequent SQL injection attempts more targeted.
    """
    tb = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error":     str(exc),            # BUG: may contain DB error details
            "traceback": tb,                  # BUG: full stack trace exposed
            "path":      str(request.url),    # BUG: full URL may contain tokens
            "type":      type(exc).__name__,  # BUG: exposes internal exception type
        },
    )


async def login(email: str, password: str) -> dict:
    """Authenticate a user by email and password.

    BUG (ASVS V16.5.1 + ASVS V6.3.3 violation):
      Two distinct error codes are returned — one for a missing user, one for
      a wrong password. An attacker sends a large list of email addresses and
      observes which error code is returned. Emails that return USER_NOT_FOUND
      are discarded; emails that return WRONG_PASSWORD are added to the target
      list for credential stuffing. This dramatically increases attack efficiency.
    """
    user = None  # placeholder: db.query(User).filter_by(email=email).first()

    if user is None:
        # BUG: reveals that this email address does not exist
        return {
            "error":   "USER_NOT_FOUND",
            "message": f"No account found for {email}",
        }

    if not _verify_password(password, user.hashed_password):
        # Different error = attacker knows the email IS valid
        return {
            "error":   "WRONG_PASSWORD",
            "message": "Incorrect password",
        }

    return {"token": "..."}


def _verify_password(plain: str, hashed: str) -> bool:
    # Placeholder — real implementation uses Argon2id
    return plain == hashed
