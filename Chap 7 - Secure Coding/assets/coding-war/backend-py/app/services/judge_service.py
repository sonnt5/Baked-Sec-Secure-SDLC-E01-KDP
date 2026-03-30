"""
Judge Service
Equivalent to: backend/src/services/judgeService.ts
Main judge worker: compile → run against test cases → update verdict.
SDRD: REQ-9.1–9.4 (SHA-256 integrity, sandboxed execution)
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import NullPool

from app.config import settings
from app.models.submission import Submission, TestCaseResult
from app.models.test_case import TestCase
from app.models.enums import SubmissionStatus
from app.services.docker_sandbox import create_sandbox, start_sandbox, destroy_sandbox
from app.services.compilation_service import compile_code
from app.services.execution_service import execute_test_case
from app.services.s3_service import download_testcase_file
from app.services.scoreboard_service import invalidate_scoreboard_cache
from app.utils.checksum import verify_sha256
from app.utils.logger import get_logger

logger = get_logger("judge_service")


def _make_judge_session():
    """
    Create a fresh async engine + session for use inside a Celery task.

    WHY NullPool: Celery's ForkPoolWorker runs each task via asyncio.run(), which
    creates and then CLOSES a new event loop. SQLAlchemy's default connection pool
    holds connections bound to that loop. The next task's asyncio.run() gets a new
    loop, but the pooled connections still reference the old (closed) loop →
    "Future attached to a different loop" crash.

    NullPool disables pooling entirely: every session opens a fresh connection and
    closes it on exit, so there are no stale event-loop references.
    """
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def judge_submission(submission_id: str) -> None:
    """
    Main judge workflow for a single submission.
    1. Fetch submission + test cases from DB
    2. Create Docker sandbox
    3. Compile source code
    4. Run against each test case
    5. Update results and verdict
    """
    async with _make_judge_session()() as db:

        # 1. Fetch submission
        result = await db.execute(
            select(Submission)
            .options(selectinload(Submission.problem))
            .where(Submission.id == uuid.UUID(submission_id))
        )
        submission = result.scalar_one_or_none()
        if not submission:
            logger.error("Submission not found for judging", submission_id=submission_id)
            return

        # Update status to COMPILING
        submission.status = SubmissionStatus.COMPILING
        await db.commit()

        # Fetch test cases
        tc_result = await db.execute(
            select(TestCase)
            .where(TestCase.problem_id == submission.problem_id)
            .order_by(TestCase.order_index)
        )
        test_cases = tc_result.scalars().all()

        container_name = None
        try:
            # 2. Create sandbox
            time_limit_seconds = (submission.problem.time_limit or 5000) / 1000.0
            memory_limit = f"{submission.problem.memory_limit or 256}m"

            container_name = await create_sandbox(
                submission.language.value,
                submission.source_code,
                memory_limit=memory_limit,
            )
            await start_sandbox(container_name)

            # 3. Compile
            success, error = await compile_code(
                container_name, submission.language.value, submission.source_code
            )

            if not success:
                submission.status = SubmissionStatus.COMPILATION_ERROR
                submission.compilation_error = error
                submission.judged_at = datetime.now(timezone.utc)
                await db.commit()
                return

            # 4. Run against test cases
            submission.status = SubmissionStatus.RUNNING
            await db.commit()

            all_accepted = True
            worst_status = SubmissionStatus.ACCEPTED
            max_time = 0
            max_memory = 0

            for tc in test_cases:
                # Use inline content stored directly in the DB (dev mode — no S3 required).
                # input_file / output_file hold raw text content seeded by seed_problems.py.
                input_data = tc.input_file.encode()
                output_data = tc.output_file.encode()

                # Verify integrity (still compute + compare SHA-256 from stored checksum)
                if not verify_sha256(input_data, tc.input_checksum):
                    logger.error("Input checksum mismatch", test_case_id=str(tc.id))
                    continue

                if not verify_sha256(output_data, tc.output_checksum):
                    logger.error("Output checksum mismatch", test_case_id=str(tc.id))
                    continue

                # Execute
                result = await execute_test_case(
                    container_name,
                    submission.language.value,
                    input_data,
                    output_data,
                    time_limit_seconds=time_limit_seconds,
                )

                # Map string status to enum
                tc_status = SubmissionStatus(result["status"])

                # Create test case result
                tc_result = TestCaseResult(
                    submission_id=submission.id,
                    test_case_id=tc.id,
                    status=tc_status,
                    execution_time=result["executionTime"],
                    memory_used=result["memoryUsed"],
                    output=result.get("output"),
                )
                db.add(tc_result)

                # Track worst status
                if tc_status != SubmissionStatus.ACCEPTED:
                    all_accepted = False
                    worst_status = tc_status

                if result["executionTime"]:
                    max_time = max(max_time, result["executionTime"])

            # 5. Update submission verdict
            submission.status = SubmissionStatus.ACCEPTED if all_accepted else worst_status
            submission.verdict = submission.status.value
            submission.execution_time = max_time
            submission.judged_at = datetime.now(timezone.utc)
            await db.commit()

            # Invalidate scoreboard cache if contest submission
            if submission.contest_id:
                await invalidate_scoreboard_cache(str(submission.contest_id))

            logger.info(
                "Judging complete",
                submission_id=submission_id,
                verdict=submission.verdict,
                execution_time=max_time,
            )

        except Exception as e:
            logger.error("Judge error", submission_id=submission_id, error=str(e))
            submission.status = SubmissionStatus.RUNTIME_ERROR
            submission.verdict = "JUDGE_ERROR"
            submission.judged_at = datetime.now(timezone.utc)
            await db.commit()

        finally:
            if container_name:
                await destroy_sandbox(container_name)
