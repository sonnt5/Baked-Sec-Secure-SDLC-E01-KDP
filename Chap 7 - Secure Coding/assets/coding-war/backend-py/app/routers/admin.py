"""
Admin Router — Fully Implemented
Equivalent to: backend/src/routes/admin.routes.ts
3 endpoints: list-users, update-role, statistics
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import CurrentUser
from app.dependencies.authorize import require_admin
from app.dependencies.database import get_db
from app.services.admin_service import (
    get_system_statistics,
    list_all_users,
    update_user_role,
)

router = APIRouter()


class UpdateRoleRequest(BaseModel):
    role: str = Field(..., pattern=r"^(ADMIN|USER|GUEST)$")


@router.get("/users")
async def list_users_endpoint(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """List all users with search/filter (Admin only)."""
    return await list_all_users(db, page=page, limit=limit, search=search)


@router.put("/users/{user_id}/role")
async def update_user_role_endpoint(
    user_id: str,
    data: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """Update user role (Admin only)."""
    return await update_user_role(db, user_id, data.role)


@router.get("/statistics")
async def get_statistics_endpoint(
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """Get system statistics (Admin only)."""
    return await get_system_statistics(db)
