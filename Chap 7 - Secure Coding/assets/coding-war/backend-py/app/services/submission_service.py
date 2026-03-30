"""
Submission Service
Equivalent to: backend/src/services/submissionService.ts
SDRD: REQ-6.1, REQ-6.7, REQ-6.8, REQ-9.1–9.4
"""

import math
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.middleware.error_handler import AppError
from app.models.submission import Submission, TestCaseResult
from app.models.problem import Problem
from app.models.enums import Language, SubmissionStatus
from app.services.contest_service import can_submit_to_contest, get_contest_by_id
from app.utils.logger import get_logger
from app.worker import enqueue_submission

logger = get_logger("submission_service")


async def create_submission(
    db: AsyncSession,
    *,
    user_id: str,
    problem_id: str,
    language: str,
    source_code: str,
    contest_id: str | None = None,
) -> Submission:
    """Create a new submission and prepare for judging."""
    # Validate problem
    result = await db.execute(select(Problem).where(Problem.id == uuid.UUID(problem_id)))
    problem = result.scalar_one_or_none()
    if not problem:
        raise AppError(404, "PROBLEM_NOT_FOUND", "Problem not found")

    # Contest validation
    contest_relative_time: int | None = None
    if contest_id:
        can_submit = await can_submit_to_contest(db, contest_id, user_id)
        if not can_submit:
            raise AppError(403, "CANNOT_SUBMIT", "Cannot submit to this contest")

        contest = await get_contest_by_id(db, contest_id)
        now = datetime.now(timezone.utc)
        contest_relative_time = int(
            (now - contest.start_time).total_seconds() / 60
        )

    submission = Submission(
        user_id=uuid.UUID(user_id),
        problem_id=uuid.UUID(problem_id),
        contest_id=uuid.UUID(contest_id) if contest_id else None,
        language=Language(language),
        source_code=source_code,
        status=SubmissionStatus.QUEUED,
        contest_relative_time=contest_relative_time,
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)

    logger.info(
        "Submission created",
        submission_id=str(submission.id),
        user_id=user_id,
        problem_id=problem_id,
    )

    # Enqueue to Celery for judging
    await db.commit()
    enqueue_submission(str(submission.id))
    return submission


async def get_submission_by_id(
    db: AsyncSession,
    submission_id: str,
    requesting_user_id: str | None = None,
    requesting_user_role: str | None = None,
) -> dict:
    """Get submission with ownership check (ADR-007)."""
    result = await db.execute(
        select(Submission)
        .options(
            selectinload(Submission.user),
            selectinload(Submission.problem),
            selectinload(Submission.test_case_results),
        )
        .where(Submission.id == uuid.UUID(submission_id))
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise AppError(404, "SUBMISSION_NOT_FOUND", "Submission not found")

    # Ownership check — non-admin can only view own submissions
    if requesting_user_role != "ADMIN" and str(submission.user_id) != requesting_user_id:
        raise AppError(403, "ACCESS_DENIED", "You can only view your own submissions")

    test_case_results = [
        {
            "testCaseId": str(r.test_case_id),
            "status": r.status.value,
            "executionTime": r.execution_time,
            "memoryUsed": r.memory_used,
        }
        for r in (submission.test_case_results or [])
    ]

    # ADR-007 / AZ-03: Determine source_code visibility
    # - Admin: always visible
    # - Owner: visible only when contest is no longer active
    # - Non-owner: never visible
    is_admin = requesting_user_role == "ADMIN"
    is_owner = str(submission.user_id) == requesting_user_id

    # Check if contest is still active (server-side time — ADR-008)
    contest_active = False
    if submission.contest_id:
        from app.services.contest_service import _utc_now
        from app.models.contest import Contest
        ct_result = await db.execute(
            select(Contest).where(Contest.id == submission.contest_id)
        )
        contest = ct_result.scalar_one_or_none()
        if contest and contest.end_time:
            contest_active = _utc_now() < contest.end_time

    # Strip source_code for non-owners or owner during active contest
    show_source = is_admin or (is_owner and not contest_active)

    return {
        "id": str(submission.id),
        "problemId": str(submission.problem_id),
        "problemTitle": submission.problem.title if submission.problem else None,
        "userId": str(submission.user_id),
        "username": submission.user.username if submission.user else None,
        "language": submission.language.value,
        "sourceCode": submission.source_code if show_source else None,
        "status": submission.status.value,
        "verdict": submission.verdict,
        "executionTime": submission.execution_time,
        "memoryUsed": submission.memory_used,
        "compilationError": submission.compilation_error if show_source else None,
        "testCaseResults": test_case_results if test_case_results else None,
        "submittedAt": submission.submitted_at.isoformat(),
        "judgedAt": submission.judged_at.isoformat() if submission.judged_at else None,
    }


async def list_submissions(
    db: AsyncSession,
    *,
    page: int = 1,
    limit: int = 20,
    user_id: str | None = None,
    problem_id: str | None = None,
    contest_id: str | None = None,
    status: str | None = None,
    requesting_user_id: str | None = None,
    requesting_user_role: str | None = None,
) -> dict:
    """List submissions with filters. Non-admins see only own submissions."""
    query = select(Submission).options(
        selectinload(Submission.user), selectinload(Submission.problem)
    )
    count_query = select(func.count(Submission.id))

    # Non-admin: force own submissions only
    if requesting_user_role != "ADMIN":
        query = query.where(Submission.user_id == uuid.UUID(requesting_user_id))
        count_query = count_query.where(Submission.user_id == uuid.UUID(requesting_user_id))
    elif user_id:
        query = query.where(Submission.user_id == uuid.UUID(user_id))
        count_query = count_query.where(Submission.user_id == uuid.UUID(user_id))

    if problem_id:
        query = query.where(Submission.problem_id == uuid.UUID(problem_id))
        count_query = count_query.where(Submission.problem_id == uuid.UUID(problem_id))

    if contest_id:
        query = query.where(Submission.contest_id == uuid.UUID(contest_id))
        count_query = count_query.where(Submission.contest_id == uuid.UUID(contest_id))

    if status:
        query = query.where(Submission.status == SubmissionStatus(status))
        count_query = count_query.where(Submission.status == SubmissionStatus(status))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * limit
    query = query.order_by(Submission.submitted_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    submissions = result.scalars().all()

    formatted = [
        {
            "id": str(s.id),
            "problemId": str(s.problem_id),
            "problemTitle": s.problem.title if s.problem else None,
            "userId": str(s.user_id),
            "username": s.user.username if s.user else None,
            "language": s.language.value,
            "status": s.status.value,
            "verdict": s.verdict,
            "executionTime": s.execution_time,
            "memoryUsed": s.memory_used,
            "submittedAt": s.submitted_at.isoformat(),
            "judgedAt": s.judged_at.isoformat() if s.judged_at else None,
        }
        for s in submissions
    ]

    return {
        "submissions": formatted,
        "total": total,
        "page": page,
        "total_pages": math.ceil(total / limit) if limit > 0 else 0,
    }
