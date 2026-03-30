"""
Contests Router — Fully Implemented
Equivalent to: backend/src/routes/contest.routes.ts
7 endpoints: list, get, create, update, delete, register, scoreboard
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import CurrentUser, get_current_user, get_optional_user
from app.dependencies.authorize import require_admin
from app.dependencies.database import get_db
from app.models.contest import ContestProblem
from app.schemas.contest import CreateContestRequest, UpdateContestRequest
from app.services.contest_service import (
    create_contest,
    delete_contest,
    get_contest_by_id,
    list_contests,
    register_for_contest,
    update_contest,
)
from app.services.scoreboard_service import generate_scoreboard

router = APIRouter()


def _to_response(c, participant_count: int = 0) -> dict:
    return {
        "id": str(c.id),
        "title": c.title,
        "slug": c.slug,
        "description": c.description,
        "startTime": c.start_time.isoformat(),
        "endTime": c.end_time.isoformat(),
        "freezeTime": c.freeze_time,
        "scoringRule": c.scoring_rule.value,
        "visibility": c.visibility.value,
        "participantCount": participant_count,
        "createdAt": c.created_at.isoformat(),
        "updatedAt": c.updated_at.isoformat(),
    }


@router.get("")
async def list_contests_endpoint(
    status: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    result = await list_contests(db, status=status, page=page, limit=limit)
    return {
        "contests": [_to_response(c) for c in result["contests"]],
        "total": result["total"],
        "page": result["page"],
        "totalPages": result["total_pages"],
    }


@router.get("/{contest_id}")
async def get_contest_endpoint(
    contest_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser | None = Depends(get_optional_user),
):
    contest = await get_contest_by_id(db, contest_id)
    resp = _to_response(contest, len(contest.participants) if contest.participants else 0)
    resp["problems"] = [
        {
            "problemId": str(cp.problem_id),
            "orderIndex": cp.order_index,
            "points": cp.points,
            "title": cp.problem.title if cp.problem else f"Problem {cp.order_index + 1}",
            "difficulty": cp.problem.difficulty.value if cp.problem else "EASY",
        }
        for cp in sorted(contest.problems or [], key=lambda x: x.order_index)
    ]
    return resp


@router.post("", status_code=201)
async def create_contest_endpoint(
    data: CreateContestRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    contest = await create_contest(
        db,
        title=data.title,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        freeze_time=data.freeze_time,
        scoring_rule=data.scoring_rule,
        visibility=data.visibility,
    )
    # Save problems if provided
    if data.problems:
        for i, p in enumerate(data.problems):
            cp = ContestProblem(
                contest_id=contest.id,
                problem_id=uuid.UUID(p.problem_id),
                order_index=p.order_index if p.order_index else i,
                points=p.points,
            )
            db.add(cp)
        await db.flush()
    return {"contestId": str(contest.id), **_to_response(contest)}


@router.put("/{contest_id}/problems")
async def update_contest_problems_endpoint(
    contest_id: str,
    problems: list[dict],
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """Replace all problems of a contest (admin only)."""
    from sqlalchemy import delete
    await db.execute(
        delete(ContestProblem).where(ContestProblem.contest_id == uuid.UUID(contest_id))
    )
    for i, p in enumerate(problems):
        cp = ContestProblem(
            contest_id=uuid.UUID(contest_id),
            problem_id=uuid.UUID(p["problemId"]),
            order_index=p.get("orderIndex", i),
            points=p.get("points"),
        )
        db.add(cp)
    return {"message": "Problems updated"}


@router.put("/{contest_id}")
async def update_contest_endpoint(
    contest_id: str,
    data: UpdateContestRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    update_data = data.model_dump(exclude_none=True)
    contest = await update_contest(db, contest_id, **update_data)
    return _to_response(contest)


@router.delete("/{contest_id}", status_code=204)
async def delete_contest_endpoint(
    contest_id: str,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    await delete_contest(db, contest_id)
    return None


@router.post("/{contest_id}/register", status_code=201)
async def register_for_contest_endpoint(
    contest_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    await register_for_contest(db, contest_id, user.user_id)
    return {"message": "Registered successfully"}


@router.get("/{contest_id}/scoreboard")
async def get_scoreboard_endpoint(
    contest_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser | None = Depends(get_optional_user),
):
    is_admin = user and user.role == "ADMIN"
    scoreboard = await generate_scoreboard(db, contest_id, is_admin=bool(is_admin))
    return scoreboard
