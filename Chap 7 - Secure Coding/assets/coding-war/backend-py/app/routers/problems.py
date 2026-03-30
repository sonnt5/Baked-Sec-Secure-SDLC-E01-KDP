"""
Problems Router — Fully Implemented
Endpoints: list, get, create, update, delete, upload-test-cases (zip),
           list-test-cases, add-single-test-case, delete-test-case
"""

import hashlib
import io
import uuid
import zipfile

from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import CurrentUser, get_current_user, get_optional_user
from app.dependencies.authorize import require_admin
from app.dependencies.database import get_db
from app.middleware.error_handler import AppError
from app.models.test_case import TestCase
from app.schemas.problem import (
    CreateProblemRequest,
    ProblemListResponse,
    ProblemResponse,
    UpdateProblemRequest,
)
from app.services.problem_service import (
    create_problem,
    delete_problem,
    get_problem_by_id,
    list_problems,
    update_problem,
)
from app.services.test_case_service import process_testcase_zip
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("problems_router")


def _to_response(p, solved_ids: set | None = None) -> dict:
    return {
        "id": str(p.id),
        "title": p.title,
        "slug": p.slug,
        "description": p.description,
        "difficulty": p.difficulty.value,
        "time_limit": p.time_limit,
        "memory_limit": p.memory_limit,
        "tags": p.tags or [],
        "visibility": p.visibility.value,
        "userSolved": str(p.id) in solved_ids if solved_ids else False,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


@router.get("")
async def list_problems_endpoint(
    page: int = 1,
    limit: int = 20,
    difficulty: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser | None = Depends(get_optional_user),
):
    """List problems with filtering and pagination."""
    is_admin = user and user.role == "ADMIN"
    result = await list_problems(
        db,
        page=page,
        limit=limit,
        difficulty=difficulty,
        visibility=None if is_admin else "PUBLIC",
    )

    # Build set of problem IDs the user has solved (any ACCEPTED submission)
    solved_ids: set[str] = set()
    if user:
        from app.models.submission import Submission
        from app.models.enums import SubmissionStatus
        solved_result = await db.execute(
            select(Submission.problem_id)
            .where(
                Submission.user_id == uuid.UUID(user.user_id),
                Submission.status == SubmissionStatus.ACCEPTED,
            )
            .distinct()
        )
        solved_ids = {str(row[0]) for row in solved_result.all()}

    return {
        "problems": [_to_response(p, solved_ids) for p in result["problems"]],
        "total": result["total"],
        "page": result["page"],
        "totalPages": result["total_pages"],
    }


@router.get("/{problem_id}")
async def get_problem_endpoint(
    problem_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser | None = Depends(get_optional_user),
):
    """Get problem details."""
    problem = await get_problem_by_id(db, problem_id)
    return _to_response(problem)


@router.post("", status_code=201)
async def create_problem_endpoint(
    data: CreateProblemRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """Create problem (Admin only)."""
    problem = await create_problem(
        db,
        title=data.title,
        description=data.description,
        difficulty=data.difficulty,
        time_limit=data.time_limit,
        memory_limit=data.memory_limit,
        tags=data.tags,
        visibility=data.visibility,
    )
    return _to_response(problem)


@router.put("/{problem_id}")
async def update_problem_endpoint(
    problem_id: str,
    data: UpdateProblemRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """Update problem (Admin only)."""
    update_data = data.model_dump(exclude_none=True)
    problem = await update_problem(db, problem_id, **update_data)
    return _to_response(problem)


@router.delete("/{problem_id}", status_code=204)
async def delete_problem_endpoint(
    problem_id: str,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """Delete problem (Admin only)."""
    await delete_problem(db, problem_id)
    return None


# ─── Test Case Endpoints ───────────────────────────────────────────────────────

@router.get("/{problem_id}/test-cases")
async def list_test_cases_endpoint(
    problem_id: str,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """List all test cases for a problem (Admin only). Returns inline content if stored."""
    await get_problem_by_id(db, problem_id)  # 404 if not found
    result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == uuid.UUID(problem_id))
        .order_by(TestCase.order_index)
    )
    test_cases = result.scalars().all()

    items = []
    for tc in test_cases:
        input_text = tc.input_content
        output_text = tc.output_content

        # Fall back to S3 if inline content not stored
        if input_text is None and tc.input_file:
            try:
                from app.services.s3_service import download_testcase_file
                input_text = download_testcase_file(tc.input_file).decode("utf-8", errors="replace")
            except Exception:
                input_text = "(S3 fetch failed)"

        if output_text is None and tc.output_file:
            try:
                from app.services.s3_service import download_testcase_file
                output_text = download_testcase_file(tc.output_file).decode("utf-8", errors="replace")
            except Exception:
                output_text = "(S3 fetch failed)"

        items.append({
            "id": str(tc.id),
            "order_index": tc.order_index,
            "is_hidden": tc.is_hidden,
            "input": input_text or "",
            "output": output_text or "",
            "created_at": tc.created_at.isoformat(),
        })

    return {"testCases": items, "total": len(items)}


class AddTestCaseRequest(BaseModel):
    input: str
    output: str
    is_sample: bool = False  # If True → is_hidden=False (visible to users)


@router.post("/{problem_id}/test-cases/single", status_code=201)
async def add_single_test_case_endpoint(
    problem_id: str,
    data: AddTestCaseRequest,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """Add a single text test case (Admin only)."""
    await get_problem_by_id(db, problem_id)

    # Determine next order_index
    result = await db.execute(
        select(TestCase.order_index)
        .where(TestCase.problem_id == uuid.UUID(problem_id))
        .order_by(TestCase.order_index.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    next_index = (last + 1) if last is not None else 0

    checksum_in = hashlib.sha256(data.input.encode()).hexdigest()
    checksum_out = hashlib.sha256(data.output.encode()).hexdigest()

    tc = TestCase(
        problem_id=uuid.UUID(problem_id),
        input_file="",
        output_file="",
        input_content=data.input,
        output_content=data.output,
        input_checksum=checksum_in,
        output_checksum=checksum_out,
        is_hidden=not data.is_sample,
        order_index=next_index,
    )
    db.add(tc)
    await db.flush()
    await db.refresh(tc)

    logger.info("Added single test case", problem_id=problem_id, tc_id=str(tc.id))
    return {
        "id": str(tc.id),
        "order_index": tc.order_index,
        "is_hidden": tc.is_hidden,
        "input": tc.input_content,
        "output": tc.output_content,
    }


@router.delete("/{problem_id}/test-cases/{tc_id}", status_code=204)
async def delete_test_case_endpoint(
    problem_id: str,
    tc_id: str,
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """Delete a single test case (Admin only)."""
    result = await db.execute(
        select(TestCase).where(
            TestCase.id == uuid.UUID(tc_id),
            TestCase.problem_id == uuid.UUID(problem_id),
        )
    )
    tc = result.scalar_one_or_none()
    if not tc:
        raise AppError(404, "TEST_CASE_NOT_FOUND", "Test case not found")

    await db.delete(tc)
    logger.info("Deleted test case", tc_id=tc_id, problem_id=problem_id)
    return None


_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
_ZIP_MAGIC = b"PK\x03\x04"


@router.post("/{problem_id}/test-cases", status_code=201)
async def upload_test_cases_endpoint(
    problem_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin: CurrentUser = Depends(require_admin),
):
    """Upload test cases zip (Admin only) — legacy ZIP support."""
    problem = await get_problem_by_id(db, problem_id)

    # Gap fix #2a: Enforce file size limit (10 MB) to prevent memory exhaustion.
    content = await file.read(_MAX_UPLOAD_BYTES + 1)
    if len(content) > _MAX_UPLOAD_BYTES:
        raise AppError(
            413, "FILE_TOO_LARGE", f"Upload exceeds maximum size of {_MAX_UPLOAD_BYTES // 1024 // 1024} MB"
        )
    if not content:
        raise AppError(400, "EMPTY_FILE", "Uploaded file is empty")

    # Gap fix #2b: Verify ZIP magic bytes before parsing (prevents content-type spoofing).
    if not content.startswith(_ZIP_MAGIC):
        raise AppError(400, "INVALID_FILE_TYPE", "File must be a valid ZIP archive")

    try:
        zip_buffer = io.BytesIO(content)
        zip_file = zipfile.ZipFile(zip_buffer)
    except zipfile.BadZipFile:
        raise AppError(400, "INVALID_ZIP", "Uploaded file is not a valid zip")

    count = await process_testcase_zip(db, str(problem.id), zip_file)
    return {"message": f"Uploaded {count} test cases", "testCasesCount": count}
