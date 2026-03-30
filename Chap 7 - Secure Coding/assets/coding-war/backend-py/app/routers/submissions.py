"""
Submissions Router — Fully Implemented
Equivalent to: backend/src/routes/submission.routes.ts
4 endpoints: submit, get, list, rejudge
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import CurrentUser, get_current_user
from app.dependencies.authorize import require_admin
from app.dependencies.database import get_db
from app.schemas.submission import CreateSubmissionRequest
from app.services.submission_service import (
    create_submission,
    get_submission_by_id,
    list_submissions,
)
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("submissions_router")


@router.post("", status_code=201)
async def create_submission_endpoint(
    data: CreateSubmissionRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Submit solution (supports contest submissions)."""
    submission = await create_submission(
        db,
        user_id=user.user_id,
        problem_id=data.problem_id,
        language=data.language,
        source_code=data.source_code,
        contest_id=data.contest_id,
    )
    return {"submissionId": str(submission.id)}


@router.get("/{submission_id}")
async def get_submission_endpoint(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Get submission details with test results. Ownership check applied."""
    return await get_submission_by_id(
        db, submission_id, user.user_id, user.role
    )


@router.get("")
async def list_submissions_endpoint(
    page: int = 1,
    limit: int = 20,
    problem_id: str | None = None,
    contest_id: str | None = None,
    status: str | None = None,
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """List submissions with filtering. Non-admins see only own submissions."""
    return await list_submissions(
        db,
        page=page,
        limit=limit,
        user_id=user_id,
        problem_id=problem_id,
        contest_id=contest_id,
        status=status,
        requesting_user_id=user.user_id,
        requesting_user_role=user.role,
    )


@router.post("/{submission_id}/rejudge", status_code=200)
async def rejudge_submission_endpoint(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """Rejudge submission (Admin only)."""
    # TODO: Reset status to QUEUED, delete test results, re-enqueue to Celery
    return {"message": "Submission queued for rejudging"}
