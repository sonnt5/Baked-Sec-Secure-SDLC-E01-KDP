"""
Authorization Dependency
Equivalent to: backend/src/middleware/authorize.ts
SDRD: REQ-4.2 through REQ-4.7 (Role-based access control)
Also applies pattern from assets/code/fixed/authz_middleware.py (ADR-007).
"""

from fastapi import Depends

from app.dependencies.auth import CurrentUser, get_current_user
from app.middleware.error_handler import AppError
from app.utils.logger import get_logger

logger = get_logger("authorize")

# Role hierarchy: ADMIN > USER > GUEST
ROLE_HIERARCHY: dict[str, int] = {
    "ADMIN": 3,
    "USER": 2,
    "GUEST": 1,
}


def require_role(*allowed_roles: str):
    """
    Factory that returns a FastAPI dependency requiring one of the given roles.

    Usage:
        @router.post("/", dependencies=[Depends(require_role("ADMIN"))])
        async def create_problem(...): ...
    """
    async def _check_role(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        user_level = ROLE_HIERARCHY.get(current_user.role, 0)

        has_permission = any(
            user_level >= ROLE_HIERARCHY.get(role, 0)
            for role in allowed_roles
        )

        if not has_permission:
            logger.warning(
                "Authorization failed",
                user_id=current_user.user_id,
                role=current_user.role,
                allowed_roles=list(allowed_roles),
            )
            raise AppError(
                403,
                "AUTH_INSUFFICIENT_PERMISSIONS",
                "You do not have permission to access this resource",
            )

        return current_user

    return _check_role


# Convenience dependencies
require_admin = require_role("ADMIN")
require_user = require_role("USER", "ADMIN")
require_authenticated = require_role("GUEST", "USER", "ADMIN")
