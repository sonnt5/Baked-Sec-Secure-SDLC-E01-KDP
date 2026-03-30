"""
TestCase Service
Equivalent to: backend/src/services/testCaseService.ts
Handles test case upload from zip files with S3 storage + SHA-256 checksums.
"""

import zipfile
import re

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.error_handler import AppError
from app.models.test_case import TestCase
from app.services.s3_service import get_testcase_s3_key, upload_testcase_file
from app.utils.checksum import compute_sha256
from app.utils.logger import get_logger

logger = get_logger("test_case_service")


async def process_testcase_zip(
    db: AsyncSession, problem_id: str, zip_file: zipfile.ZipFile
) -> int:
    """
    Process a zip file containing test cases (input/output pairs).
    Expected zip structure: {N}.in / {N}.out pairs (e.g., 1.in, 1.out, 2.in, 2.out)

    Returns the number of test cases created.
    """
    # Parse zip contents
    file_names = zip_file.namelist()
    input_files: dict[int, str] = {}
    output_files: dict[int, str] = {}

    for name in file_names:
        # Skip directories and hidden files
        if name.endswith("/") or name.startswith("__") or name.startswith("."):
            continue

        basename = name.split("/")[-1]  # Handle nested dirs
        match = re.match(r"^(\d+)\.(in|out)$", basename)
        if match:
            index = int(match.group(1))
            ext = match.group(2)
            if ext == "in":
                input_files[index] = name
            else:
                output_files[index] = name

    # Validate pairs
    indices = sorted(set(input_files.keys()) & set(output_files.keys()))
    if not indices:
        raise AppError(
            400, "NO_TEST_CASES", "No valid test case pairs found (expected N.in / N.out)"
        )

    # Delete existing test cases for this problem
    await db.execute(delete(TestCase).where(TestCase.problem_id == problem_id))

    # Create new test cases
    for order_index, file_index in enumerate(indices):
        input_content = zip_file.read(input_files[file_index])
        output_content = zip_file.read(output_files[file_index])

        # Compute SHA-256 checksums
        input_checksum = compute_sha256(input_content)
        output_checksum = compute_sha256(output_content)

        # Upload to S3 with encryption (ADR-006)
        input_key = get_testcase_s3_key(problem_id, order_index, "in")
        output_key = get_testcase_s3_key(problem_id, order_index, "out")
        upload_testcase_file(input_key, input_content)
        upload_testcase_file(output_key, output_content)

        # Create database record
        test_case = TestCase(
            problem_id=problem_id,
            input_file=input_key,
            output_file=output_key,
            input_checksum=input_checksum,
            output_checksum=output_checksum,
            order_index=order_index,
        )
        db.add(test_case)

    await db.flush()
    logger.info(
        "Test cases uploaded",
        problem_id=problem_id,
        count=len(indices),
    )
    return len(indices)
