"""
Code Validator Utilities
Gap Fix: ReDoS Prevention (ASVS V1.2.9)
Pattern from: assets/code/fixed/code_validator.py

IS-05: regex patterns with nested quantifiers allow catastrophic backtracking.
Fix: timeout wrapper + pre-compiled linear patterns.
"""

import re
import threading

# ──────────────────────────── Pre-compiled patterns ────────────────────────────

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,32}$")
VERDICT_PATTERN = re.compile(
    r"^(ACCEPTED|WRONG_ANSWER|TIME_LIMIT_EXCEEDED|MEMORY_LIMIT_EXCEEDED|RUNTIME_ERROR|COMPILATION_ERROR|QUEUED|RUNNING|COMPILING)$"
)
EXECUTION_TIME_PATTERN = re.compile(r"^\d{1,8}$")


# ──────────────────────────── Timeout-protected match ────────────────────────────

def safe_regex_match(pattern: str, text: str, timeout_sec: float = 1.0) -> bool:
    """
    ReDoS-safe regex matching with a hard timeout.
    If the match takes longer than timeout_sec, returns False (fail securely).
    ASVS V1.2.9 compliant.
    """
    result: list[re.Match | None] = [None]
    exception: list[Exception | None] = [None]

    def _match() -> None:
        try:
            result[0] = re.match(pattern, text)
        except re.error as exc:
            exception[0] = exc

    t = threading.Thread(target=_match, daemon=True)
    t.start()
    t.join(timeout=timeout_sec)

    if t.is_alive():
        return False  # Timeout — treat as no match (deny by default)
    if exception[0]:
        return False
    return bool(result[0])


# ──────────────────────────── Validators ────────────────────────────

def validate_username(value: str) -> bool:
    """Validate username against pre-compiled linear pattern."""
    return bool(USERNAME_PATTERN.match(value))


def validate_verdict(verdict: str) -> bool:
    """Validate a judge verdict string using a linear-time pattern."""
    return bool(VERDICT_PATTERN.match(verdict))


def validate_execution_time_ms(value: int) -> bool:
    """Validate execution time is within safe bounds (0–60000ms)."""
    return 0 <= value <= 60_000
