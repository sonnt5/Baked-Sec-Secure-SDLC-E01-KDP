"""
Users Router — Fully Implemented
Equivalent to: backend/src/routes/user.routes.ts
3 endpoints: get-profile, update-profile, get-submissions
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import CurrentUser, get_current_user, get_optional_user
from app.dependencies.database import get_db
from app.services.user_service import get_user_profile, update_user_profile
from app.services.submission_service import list_submissions

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=20)


@router.get("/{user_id}")
async def get_user_profile_endpoint(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_optional_user),
):
    """Get user profile with statistics."""
    return await get_user_profile(db, user_id)


@router.put("/{user_id}")
async def update_user_profile_endpoint(
    user_id: str,
    data: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update user profile. Users can only update own profile."""
    return await update_user_profile(
        db, user_id, current_user.user_id, **data.model_dump(exclude_none=True)
    )


@router.get("/{user_id}/submissions")
async def get_user_submissions_endpoint(
    user_id: str,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get user submission history."""
    return await list_submissions(
        db,
        page=page,
        limit=limit,
        user_id=user_id,
        requesting_user_id=current_user.user_id,
        requesting_user_role=current_user.role,
    )
