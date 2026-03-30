"""
User Service
Equivalent to: backend/src/services/userService.ts
"""

import uuid
import math

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.error_handler import AppError
from app.models.user import User
from app.models.submission import Submission
from app.models.enums import SubmissionStatus
from app.utils.logger import get_logger

logger = get_logger("user_service")


async def get_user_profile(db: AsyncSession, user_id: str) -> dict:
    """Get user profile with statistics."""
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise AppError(404, "USER_NOT_FOUND", "User not found")

    # Count statistics
    total_submissions = await db.execute(
        select(func.count(Submission.id)).where(Submission.user_id == uuid.UUID(user_id))
    )
    accepted_submissions = await db.execute(
        select(func.count(Submission.id)).where(
            Submission.user_id == uuid.UUID(user_id),
            Submission.status == SubmissionStatus.ACCEPTED,
        )
    )
    unique_problems_solved = await db.execute(
        select(func.count(func.distinct(Submission.problem_id))).where(
            Submission.user_id == uuid.UUID(user_id),
            Submission.status == SubmissionStatus.ACCEPTED,
        )
    )

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "isEmailVerified": user.is_email_verified,
        "createdAt": user.created_at.isoformat(),
        "statistics": {
            "totalSubmissions": total_submissions.scalar() or 0,
            "acceptedSubmissions": accepted_submissions.scalar() or 0,
            "uniqueProblemsSolved": unique_problems_solved.scalar() or 0,
        },
    }


async def update_user_profile(
    db: AsyncSession, user_id: str, requesting_user_id: str, **data
) -> dict:
    """Update profile, enforcing ownership (ADR-007)."""
    if user_id != requesting_user_id:
        raise AppError(403, "ACCESS_DENIED", "You can only update your own profile")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "User not found")

    if "username" in data and data["username"] is not None:
        existing = await db.execute(
            select(User).where(User.username == data["username"], User.id != uuid.UUID(user_id))
        )
        if existing.scalar_one_or_none():
            raise AppError(409, "USERNAME_TAKEN", "Username already taken")
        user.username = data["username"]

    await db.flush()
    return await get_user_profile(db, user_id)
