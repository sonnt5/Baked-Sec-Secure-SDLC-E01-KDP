# app/validators/code_validator.py — FIXED version
# Lab 7.3: ReDoS Prevention (ASVS V1.2.9)
#
# IS-05: regex patterns with nested quantifiers allow catastrophic
#        backtracking on crafted input — a single request can hang a
#        worker for seconds or minutes.
# Fix: timeout wrapper + pre-compiled linear patterns for known formats.

import re
import threading


# ---------------------------------------------------------------------------
# Vulnerable patterns — shown for educational analysis only
# ---------------------------------------------------------------------------
# VULNERABLE_PATTERNS: list[str] = [
#     r"(a+)+",           # nested quantifiers → exponential backtracking
#     r"(a|a)+",          # ambiguous alternation
#     r"([a-zA-Z]+)*",    # nested quantifiers on character class
# ]


# ---------------------------------------------------------------------------
# Fix 1: timeout wrapper — Fail Securely principle (ASVS V1.2.9)
# ---------------------------------------------------------------------------
def safe_regex_match(pattern: str, text: str, timeout_sec: float = 1.0) -> bool:
    """ReDoS-safe regex matching with a hard timeout.

    If the match takes longer than timeout_sec, we assume a ReDoS attempt
    and return False (Fail Securely — deny by default on anomalous input).

    For production use, prefer Fix 2 (pre-compiled linear patterns).
    Use this wrapper only when patterns come from a trusted but dynamic
    source (e.g., the problem database) and cannot be pre-compiled.
    ASVS V1.2.9 compliant.
    """
    result    = [None]
    exception = [None]

    def _match() -> None:
        try:
            result[0] = re.match(pattern, text)
        except re.error as exc:
            exception[0] = exc

    t = threading.Thread(target=_match, daemon=True)
    t.start()
    t.join(timeout=timeout_sec)

    if t.is_alive():
        # Regex is still running — likely ReDoS; fail closed
        return False
    if exception[0]:
        # Malformed pattern — also fail closed
        return False
    return bool(result[0])


# ---------------------------------------------------------------------------
# Fix 2: pre-compiled linear patterns (preferred for known formats)
# ---------------------------------------------------------------------------
# Linear patterns have no nested quantifiers and run in O(n) time.
# These cover all expected judge output formats for CODING WAR.

# Verdict: exactly one of the known strings
EXPECTED_VERDICT_PATTERN = re.compile(
    r"^(ACCEPTED|WRONG_ANSWER|TIME_LIMIT_EXCEEDED|MEMORY_LIMIT_EXCEEDED|RUNTIME_ERROR)$"
)

# Execution time: non-negative integer (ms), max 8 digits
EXECUTION_TIME_PATTERN = re.compile(r"^\d{1,8}$")

# Username: alphanumeric + underscore, 3 to 32 chars (no nested quantifiers)
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


def validate_verdict_format(verdict: str) -> bool:
    """Validate a judge verdict string using a linear-time pattern."""
    return bool(EXPECTED_VERDICT_PATTERN.match(verdict))


def validate_execution_time_string(value: str) -> bool:
    """Validate that a reported execution time is a non-negative integer string."""
    return bool(EXECUTION_TIME_PATTERN.match(value))
