"""
Contest Service
Equivalent to: backend/src/services/contestService.ts
SDRD: ADR-008 — Server-side authoritative time for all business logic.
Pattern from: assets/code/fixed/contest_time.py
"""

import math
import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.middleware.error_handler import AppError
from app.models.contest import Contest, ContestParticipant, ContestProblem
from app.models.enums import ScoringRule, Visibility
from app.utils.logger import get_logger

logger = get_logger("contest_service")


def _utc_now() -> datetime:
    """ADR-008: Single authoritative UTC clock for all time comparisons."""
    return datetime.now(timezone.utc)


def _generate_slug(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:255]


async def _ensure_unique_slug(db: AsyncSession, base_slug: str) -> str:
    slug = base_slug
    counter = 1
    while True:
        result = await db.execute(select(Contest).where(Contest.slug == slug))
        if result.scalar_one_or_none() is None:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


async def create_contest(
    db: AsyncSession,
    *,
    title: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    freeze_time: int | None,
    scoring_rule: str,
    visibility: str,
) -> Contest:
    slug = await _ensure_unique_slug(db, _generate_slug(title))
    contest = Contest(
        title=title,
        slug=slug,
        description=description,
        start_time=start_time,
        end_time=end_time,
        freeze_time=freeze_time,
        scoring_rule=ScoringRule(scoring_rule),
        visibility=Visibility(visibility),
    )
    db.add(contest)
    await db.flush()
    await db.refresh(contest)
    logger.info("Contest created", contest_id=str(contest.id), title=title)
    return contest


async def update_contest(db: AsyncSession, contest_id: str, **data) -> Contest:
    contest = await get_contest_by_id(db, contest_id)
    for key, value in data.items():
        if value is not None:
            if key == "title":
                contest.slug = await _ensure_unique_slug(db, _generate_slug(value))
            if key == "scoring_rule":
                value = ScoringRule(value)
            if key == "visibility":
                value = Visibility(value)
            setattr(contest, key, value)
    await db.flush()
    await db.refresh(contest)
    return contest


async def delete_contest(db: AsyncSession, contest_id: str) -> None:
    contest = await get_contest_by_id(db, contest_id)
    await db.delete(contest)
    logger.info("Contest deleted", contest_id=contest_id)


async def get_contest_by_id(db: AsyncSession, contest_id: str) -> Contest:
    result = await db.execute(
        select(Contest)
        .options(selectinload(Contest.problems), selectinload(Contest.participants))
        .where(Contest.id == uuid.UUID(contest_id))
    )
    contest = result.scalar_one_or_none()
    if not contest:
        raise AppError(404, "CONTEST_NOT_FOUND", "Contest not found")
    return contest


async def list_contests(
    db: AsyncSession,
    *,
    status: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    now = _utc_now()
    query = select(Contest)
    count_query = select(func.count(Contest.id))

    if status == "upcoming":
        cond = Contest.start_time > now
        query = query.where(cond)
        count_query = count_query.where(cond)
    elif status == "ongoing":
        cond = and_(Contest.start_time <= now, Contest.end_time >= now)
        query = query.where(cond)
        count_query = count_query.where(cond)
    elif status == "ended":
        cond = Contest.end_time < now
        query = query.where(cond)
        count_query = count_query.where(cond)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * limit
    query = query.order_by(Contest.start_time.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    contests = result.scalars().all()

    return {
        "contests": contests,
        "total": total,
        "page": page,
        "total_pages": math.ceil(total / limit) if limit > 0 else 0,
    }


async def register_for_contest(
    db: AsyncSession, contest_id: str, user_id: str
) -> ContestParticipant:
    contest = await get_contest_by_id(db, contest_id)
    now = _utc_now()

    if contest.start_time <= now:
        raise AppError(403, "CONTEST_STARTED", "Cannot register after contest has started")

    if contest.visibility == Visibility.PRIVATE:
        raise AppError(403, "PRIVATE_CONTEST", "This is a private contest. Registration requires invitation.")

    # Check existing registration
    existing = await db.execute(
        select(ContestParticipant).where(
            ContestParticipant.contest_id == uuid.UUID(contest_id),
            ContestParticipant.user_id == uuid.UUID(user_id),
        )
    )
    if existing.scalar_one_or_none():
        raise AppError(409, "ALREADY_REGISTERED", "Already registered for this contest")

    participant = ContestParticipant(
        contest_id=uuid.UUID(contest_id),
        user_id=uuid.UUID(user_id),
    )
    db.add(participant)
    await db.flush()
    return participant


async def can_submit_to_contest(
    db: AsyncSession, contest_id: str, user_id: str
) -> bool:
    """Check if user can submit (registered + contest ongoing). Uses server time (ADR-008)."""
    contest = await get_contest_by_id(db, contest_id)
    now = _utc_now()

    if now < contest.start_time or now > contest.end_time:
        return False

    result = await db.execute(
        select(ContestParticipant).where(
            ContestParticipant.contest_id == uuid.UUID(contest_id),
            ContestParticipant.user_id == uuid.UUID(user_id),
        )
    )
    return result.scalar_one_or_none() is not None
