"""
Scoreboard Service
Equivalent to: backend/src/services/scoreboardService.ts
Handles scoreboard generation with ranking, caching, and freeze logic.
"""

import json
import uuid
from datetime import datetime, timezone

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.contest import Contest
from app.services.scoring_service import calculate_contest_scores
from app.utils.logger import get_logger

logger = get_logger("scoreboard_service")

# Redis client for scoreboard caching
_redis: aioredis.Redis | None = None


async def _get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def _assign_ranks(participants: list[dict]) -> list[dict]:
    """Assign ranks with tie handling."""
    ranked = []
    current_rank = 1

    for i, p in enumerate(participants):
        if i > 0:
            prev = participants[i - 1]
            is_tie = (
                prev["totalScore"] == p["totalScore"]
                and prev["penaltyTime"] == p["penaltyTime"]
            )
            if not is_tie:
                current_rank = i + 1

        ranked.append({**p, "rank": current_rank})

    return ranked


def _should_freeze(contest: Contest, is_admin: bool) -> bool:
    """Check if scoreboard should be frozen."""
    if is_admin or contest.freeze_time is None:
        return False

    now = datetime.now(timezone.utc)
    freeze_at = contest.end_time.replace(tzinfo=timezone.utc) if contest.end_time.tzinfo is None else contest.end_time
    from datetime import timedelta
    freeze_at = freeze_at - timedelta(minutes=contest.freeze_time)

    end_time = contest.end_time.replace(tzinfo=timezone.utc) if contest.end_time.tzinfo is None else contest.end_time
    return freeze_at <= now < end_time


async def generate_scoreboard(
    db: AsyncSession,
    contest_id: str,
    is_admin: bool = False,
) -> dict:
    """Generate scoreboard with ranking, caching, and freeze."""
    # Get contest
    result = await db.execute(
        select(Contest).where(Contest.id == uuid.UUID(contest_id))
    )
    contest = result.scalar_one_or_none()
    if not contest:
        return {"participants": [], "isFrozen": False}

    is_frozen = _should_freeze(contest, is_admin)
    cache_key = f"scoreboard:{contest_id}:{'frozen' if is_frozen else 'live'}"

    # Try cache
    try:
        r = await _get_redis()
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    # Calculate scores
    scores = await calculate_contest_scores(db, contest_id)
    ranked = _assign_ranks(scores)

    scoreboard = {
        "participants": ranked,
        "isFrozen": is_frozen,
    }

    # Cache (30s during contest, 5min after)
    now = datetime.now(timezone.utc)
    start = contest.start_time.replace(tzinfo=timezone.utc) if contest.start_time.tzinfo is None else contest.start_time
    end = contest.end_time.replace(tzinfo=timezone.utc) if contest.end_time.tzinfo is None else contest.end_time
    is_ongoing = start <= now < end
    ttl = 30 if is_ongoing else 300

    try:
        r = await _get_redis()
        await r.setex(cache_key, ttl, json.dumps(scoreboard))
    except Exception:
        pass

    return scoreboard


async def invalidate_scoreboard_cache(contest_id: str) -> None:
    """Invalidate scoreboard cache for a contest."""
    try:
        r = await _get_redis()
        keys = [
            f"scoreboard:{contest_id}:live",
            f"scoreboard:{contest_id}:frozen",
        ]
        await r.delete(*keys)
    except Exception:
        pass
