"""
Execution Service
Equivalent to: backend/src/services/executionService.ts
Executes compiled code against test cases inside Docker sandbox.
"""

import time

from app.services.docker_sandbox import exec_in_sandbox
from app.services.compilation_service import get_run_command
from app.utils.logger import get_logger

logger = get_logger("execution_service")


def _normalize_output(output: str) -> str:
    """Normalize output for comparison: strip trailing whitespace/newlines per line."""
    lines = output.rstrip().split("\n")
    return "\n".join(line.rstrip() for line in lines)


async def execute_test_case(
    container_name: str,
    language: str,
    input_data: bytes,
    expected_output: bytes,
    *,
    time_limit_seconds: float = 5.0,
) -> dict:
    """
    Execute code against a single test case.
    Returns { status, execution_time, memory_used, output }.
    """
    run_cmd = get_run_command(language)
    start_time = time.perf_counter()

    exit_code, stdout, stderr = await exec_in_sandbox(
        container_name,
        run_cmd,
        timeout_seconds=int(time_limit_seconds) + 2,  # Buffer for process overhead
        stdin_data=input_data,
    )

    duration_ms = int((time.perf_counter() - start_time) * 1000)

    # Check Time Limit Exceeded
    if exit_code == -1 or duration_ms > int(time_limit_seconds * 1000):
        return {
            "status": "TIME_LIMIT_EXCEEDED",
            "executionTime": duration_ms,
            "memoryUsed": None,
            "output": None,
        }

    # Check Runtime Error
    if exit_code != 0:
        return {
            "status": "RUNTIME_ERROR",
            "executionTime": duration_ms,
            "memoryUsed": None,
            "output": stderr[:500] if stderr else None,
        }

    # Compare output
    actual = _normalize_output(stdout)
    expected = _normalize_output(expected_output.decode(errors="replace"))

    if actual == expected:
        return {
            "status": "ACCEPTED",
            "executionTime": duration_ms,
            "memoryUsed": None,
            "output": actual[:500],
        }
    else:
        return {
            "status": "WRONG_ANSWER",
            "executionTime": duration_ms,
            "memoryUsed": None,
            "output": actual[:500],
        }
