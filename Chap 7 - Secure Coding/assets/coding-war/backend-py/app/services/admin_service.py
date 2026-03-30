"""
Admin Service
Equivalent to: backend/src/services/adminService.ts
"""

import uuid
import math

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.error_handler import AppError
from app.models.user import User
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.contest import Contest
from app.models.enums import Role
from app.utils.logger import get_logger

logger = get_logger("admin_service")


async def list_all_users(
    db: AsyncSession,
    *,
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
) -> dict:
    """List all users with optional search."""
    query = select(User)
    count_query = select(func.count(User.id))

    if search:
        pattern = f"%{search}%"
        cond = or_(
            User.username.ilike(pattern),
            User.email.ilike(pattern),
        )
        query = query.where(cond)
        count_query = count_query.where(cond)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * limit
    query = query.order_by(User.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    formatted = [
        {
            "id": str(u.id),
            "username": u.username,
            "email": u.email,
            "role": u.role.value,
            "isEmailVerified": u.is_email_verified,
            "createdAt": u.created_at.isoformat(),
        }
        for u in users
    ]

    return {
        "users": formatted,
        "total": total,
        "page": page,
        "totalPages": math.ceil(total / limit) if limit > 0 else 0,
    }


async def update_user_role(
    db: AsyncSession, user_id: str, new_role: str
) -> dict:
    """Update a user's role."""
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise AppError(404, "USER_NOT_FOUND", "User not found")

    user.role = Role(new_role)
    await db.flush()

    logger.info("User role updated", user_id=user_id, new_role=new_role)
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
    }


async def get_system_statistics(db: AsyncSession) -> dict:
    """Get system-wide statistics."""
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_problems = (await db.execute(select(func.count(Problem.id)))).scalar() or 0
    total_submissions = (await db.execute(select(func.count(Submission.id)))).scalar() or 0
    total_contests = (await db.execute(select(func.count(Contest.id)))).scalar() or 0

    return {
        "totalUsers": total_users,
        "totalProblems": total_problems,
        "totalSubmissions": total_submissions,
        "totalContests": total_contests,
    }
