"""
Scoring Service
Equivalent to: backend/src/services/scoringService.ts
SDRD Gap Fix: Use Decimal for score calculation instead of floating point.
Pattern from: assets/code/fixed/scoring.py
"""

import uuid
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.contest import Contest, ContestProblem, ContestParticipant
from app.models.submission import Submission, TestCaseResult
from app.models.user import User
from app.models.enums import SubmissionStatus, ScoringRule
from app.utils.logger import get_logger

logger = get_logger("scoring_service")

# SDRD Gap Fix: validate execution_ms range
MAX_EXECUTION_MS = 60_000

# ──────────────────────────────────────────────────────────────────────────────
# Atomic Redis Lua — Submission Quota (ASVS V15.4.1 TOCTOU fix)
# Gap Fix: scoring.py asset — INCR_IF_BELOW_LIMIT_SCRIPT
#
# Lua scripts run atomically inside Redis — no other command can interleave.
# The read, check, and increment happen as a single indivisible operation.
# ──────────────────────────────────────────────────────────────────────────────
_INCR_IF_BELOW_LIMIT_SCRIPT = """
local key     = KEYS[1]
local max_val = tonumber(ARGV[1])
local current = tonumber(redis.call('GET', key) or '0')
if current >= max_val then
    return -1   -- rate limit exceeded
end
return redis.call('INCR', key)  -- atomic increment
"""

MAX_SUBMISSIONS_PER_CONTEST = 10


async def check_and_increment_submission_quota(
    redis,
    user_id: str,
    contest_id: str,
) -> bool:
    """
    Atomically check-and-increment the per-user, per-contest submission quota.
    Returns True if submission is allowed, False if limit is reached.
    No TOCTOU race — Lua script is atomic inside Redis. (ASVS V15.4.1)
    """
    key = f"sub_count:{user_id}:{contest_id}"
    result = await redis.eval(
        _INCR_IF_BELOW_LIMIT_SCRIPT,
        1,           # number of keys
        key,         # KEYS[1]
        MAX_SUBMISSIONS_PER_CONTEST,  # ARGV[1]
    )
    return result != -1


def _safe_execution_time(ms: int | None) -> int:
    """Validate and clamp execution_ms (SDRD gap fix from scoring.py)."""
    if ms is None:
        return 0
    return max(0, min(ms, MAX_EXECUTION_MS))


async def calculate_ioi_score(
    db: AsyncSession, contest_id: str, user_id: str
) -> dict:
    """IOI scoring: sum points from accepted test cases for each problem."""
    user_result = await db.execute(
        select(User.username).where(User.id == uuid.UUID(user_id))
    )
    username = user_result.scalar_one_or_none() or "unknown"

    contest_problems = await db.execute(
        select(ContestProblem)
        .options(selectinload(ContestProblem.problem))
        .where(ContestProblem.contest_id == uuid.UUID(contest_id))
        .order_by(ContestProblem.order_index)
    )
    problem_scores = []
    total_score = 0
    solved_count = 0

    for cp in contest_problems.scalars().all():
        max_points = Decimal(str(cp.points or 0))

        submissions_result = await db.execute(
            select(Submission)
            .options(selectinload(Submission.test_case_results))
            .where(
                Submission.contest_id == uuid.UUID(contest_id),
                Submission.user_id == uuid.UUID(user_id),
                Submission.problem_id == cp.problem_id,
            )
            .order_by(Submission.submitted_at)
        )
        submissions = submissions_result.scalars().all()

        best_score = Decimal("0")
        attempts = len(submissions)
        solved_at = None

        # Count test cases for partial scoring
        tc_count_result = await db.execute(
            select(func.count()).where(TestCase.problem_id == cp.problem_id)
        )
        from sqlalchemy import func
        from app.models.test_case import TestCase
        tc_count_q = await db.execute(
            select(func.count(TestCase.id)).where(TestCase.problem_id == cp.problem_id)
        )
        total_test_cases = tc_count_q.scalar() or 0

        for sub in submissions:
            if sub.status == SubmissionStatus.ACCEPTED:
                best_score = max_points
                if not solved_at:
                    solved_at = sub.submitted_at
            elif total_test_cases > 0:
                passed = sum(
                    1
                    for r in (sub.test_case_results or [])
                    if r.status == SubmissionStatus.ACCEPTED
                )
                partial = (Decimal(str(passed)) / Decimal(str(total_test_cases)) * max_points).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
                best_score = max(best_score, partial)

        if best_score > 0:
            solved_count += 1
        total_score += int(best_score)

        problem_scores.append({
            "problemId": str(cp.problem_id),
            "score": int(best_score),
            "attempts": attempts,
            "solvedAt": solved_at.isoformat() if solved_at else None,
            "penaltyMinutes": 0,
        })

    return {
        "userId": user_id,
        "username": username,
        "totalScore": total_score,
        "solvedCount": solved_count,
        "penaltyTime": 0,
        "problems": problem_scores,
    }


async def calculate_acm_score(
    db: AsyncSession, contest_id: str, user_id: str
) -> dict:
    """ACM scoring: count solved + penalty time."""
    user_result = await db.execute(
        select(User.username).where(User.id == uuid.UUID(user_id))
    )
    username = user_result.scalar_one_or_none() or "unknown"

    contest_result = await db.execute(
        select(Contest.start_time).where(Contest.id == uuid.UUID(contest_id))
    )
    start_time = contest_result.scalar_one()

    contest_problems = await db.execute(
        select(ContestProblem)
        .where(ContestProblem.contest_id == uuid.UUID(contest_id))
        .order_by(ContestProblem.order_index)
    )

    problem_scores = []
    solved_count = 0
    total_penalty = 0

    for cp in contest_problems.scalars().all():
        submissions_result = await db.execute(
            select(Submission)
            .where(
                Submission.contest_id == uuid.UUID(contest_id),
                Submission.user_id == uuid.UUID(user_id),
                Submission.problem_id == cp.problem_id,
            )
            .order_by(Submission.submitted_at)
        )
        submissions = submissions_result.scalars().all()

        solved = False
        solved_at = None
        wrong_attempts = 0
        penalty_minutes = 0

        for sub in submissions:
            if sub.status == SubmissionStatus.ACCEPTED:
                solved = True
                solved_at = sub.submitted_at
                time_from_start = (
                    sub.contest_relative_time
                    if sub.contest_relative_time is not None
                    else int((sub.submitted_at - start_time).total_seconds() / 60)
                )
                penalty_minutes = time_from_start + (wrong_attempts * 20)
                break
            else:
                wrong_attempts += 1

        if solved:
            solved_count += 1
            total_penalty += penalty_minutes

        problem_scores.append({
            "problemId": str(cp.problem_id),
            "score": 1 if solved else 0,
            "attempts": len(submissions),
            "solvedAt": solved_at.isoformat() if solved_at else None,
            "penaltyMinutes": penalty_minutes,
        })

    return {
        "userId": user_id,
        "username": username,
        "totalScore": solved_count,
        "solvedCount": solved_count,
        "penaltyTime": total_penalty,
        "problems": problem_scores,
    }


async def calculate_contest_scores(
    db: AsyncSession, contest_id: str
) -> list[dict]:
    """Calculate and rank all participants."""
    contest_result = await db.execute(
        select(Contest).where(Contest.id == uuid.UUID(contest_id))
    )
    contest = contest_result.scalar_one()

    participants_result = await db.execute(
        select(ContestParticipant.user_id)
        .where(ContestParticipant.contest_id == uuid.UUID(contest_id))
    )
    participant_ids = [str(row[0]) for row in participants_result.all()]

    scores = []
    for uid in participant_ids:
        if contest.scoring_rule == ScoringRule.IOI:
            score = await calculate_ioi_score(db, contest_id, uid)
        else:
            score = await calculate_acm_score(db, contest_id, uid)
        scores.append(score)

    # Sort
    if contest.scoring_rule == ScoringRule.IOI:
        scores.sort(key=lambda s: (-s["totalScore"], -s["solvedCount"]))
    else:
        scores.sort(key=lambda s: (-s["solvedCount"], s["penaltyTime"]))

    return scores
