"""
Problem Service
Equivalent to: backend/src/services/problemService.ts
"""

import math
import re
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.error_handler import AppError
from app.models.problem import Problem
from app.models.enums import Difficulty, Visibility
from app.utils.logger import get_logger

logger = get_logger("problem_service")


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from a title."""
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:255]


async def ensure_unique_slug(db: AsyncSession, base_slug: str) -> str:
    """Ensure slug is unique by appending a number if necessary."""
    slug = base_slug
    counter = 1
    while True:
        result = await db.execute(select(Problem).where(Problem.slug == slug))
        if result.scalar_one_or_none() is None:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


async def create_problem(
    db: AsyncSession,
    *,
    title: str,
    description: str,
    difficulty: str,
    time_limit: int,
    memory_limit: int,
    tags: list[str],
    visibility: str,
) -> Problem:
    """Create a new problem."""
    slug = await ensure_unique_slug(db, generate_slug(title))

    problem = Problem(
        title=title,
        slug=slug,
        description=description,
        difficulty=Difficulty(difficulty),
        time_limit=time_limit,
        memory_limit=memory_limit,
        tags=tags,
        visibility=Visibility(visibility),
    )
    db.add(problem)
    await db.flush()
    await db.refresh(problem)

    logger.info("Problem created", problem_id=str(problem.id), title=title)
    return problem


async def get_problem_by_id(db: AsyncSession, problem_id: str) -> Problem:
    """Get a problem by ID."""
    result = await db.execute(select(Problem).where(Problem.id == uuid.UUID(problem_id)))
    problem = result.scalar_one_or_none()
    if not problem:
        raise AppError(404, "PROBLEM_NOT_FOUND", "Problem not found")
    return problem


async def list_problems(
    db: AsyncSession,
    *,
    page: int = 1,
    limit: int = 20,
    difficulty: str | None = None,
    visibility: str | None = None,
) -> dict:
    """List problems with filtering and pagination."""
    query = select(Problem)
    count_query = select(func.count(Problem.id))

    if difficulty:
        query = query.where(Problem.difficulty == Difficulty(difficulty))
        count_query = count_query.where(Problem.difficulty == Difficulty(difficulty))

    if visibility is not None:
        query = query.where(Problem.visibility == Visibility(visibility))
        count_query = count_query.where(Problem.visibility == Visibility(visibility))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * limit
    query = query.order_by(Problem.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    problems = result.scalars().all()

    return {
        "problems": problems,
        "total": total,
        "page": page,
        "total_pages": math.ceil(total / limit) if limit > 0 else 0,
    }


async def update_problem(db: AsyncSession, problem_id: str, **data) -> Problem:
    """Update a problem."""
    problem = await get_problem_by_id(db, problem_id)

    for key, value in data.items():
        if value is not None:
            if key == "title":
                problem.slug = await ensure_unique_slug(db, generate_slug(value))
            if key == "difficulty":
                value = Difficulty(value)
            if key == "visibility":
                value = Visibility(value)
            setattr(problem, key, value)

    await db.flush()
    await db.refresh(problem)
    return problem


async def delete_problem(db: AsyncSession, problem_id: str) -> None:
    """Delete a problem (cascade deletes test cases)."""
    problem = await get_problem_by_id(db, problem_id)
    await db.delete(problem)
    logger.info("Problem deleted", problem_id=problem_id)
