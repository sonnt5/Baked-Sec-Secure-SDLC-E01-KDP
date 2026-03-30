"""
Authentication Dependency
Equivalent to: backend/src/middleware/auth.ts
JWT Bearer token validation via FastAPI Depends().
"""

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.middleware.error_handler import AppError
from app.services.auth_service import verify_access_token
from app.utils.logger import get_logger

logger = get_logger("auth")

# FastAPI security scheme — auto-documents Bearer auth in OpenAPI
_bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser:
    """Authenticated user context attached to the request."""

    def __init__(self, user_id: str, role: str):
        self.user_id = user_id
        self.role = role


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    """
    Validate JWT Bearer token and return the current user.
    Equivalent to authenticate() middleware in auth.ts.
    """
    if credentials is None:
        raise AppError(401, "AUTH_TOKEN_MISSING", "Authorization header is required")

    token = credentials.credentials
    payload = verify_access_token(token)

    if payload is None:
        raise AppError(401, "AUTH_TOKEN_INVALID", "Invalid or expired token")

    return CurrentUser(user_id=payload["userId"], role=payload["role"])


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser | None:
    """
    Optionally validate JWT Bearer token.
    Returns None if no token or invalid token.
    Equivalent to optionalAuth() in auth.ts.
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = verify_access_token(token)

    if payload is None:
        return None

    return CurrentUser(user_id=payload["userId"], role=payload["role"])
