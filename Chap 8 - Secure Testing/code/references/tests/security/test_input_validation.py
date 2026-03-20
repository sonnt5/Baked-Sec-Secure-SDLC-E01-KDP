# code/reference/tests/security/test_input_validation.py
# Chapter 8, Lab 8.2: Input Validation Security Tests
#
# Reference implementation — open only after completing your own.
# Run: pytest -m "security and input" -v

import pytest

pytestmark = [pytest.mark.security, pytest.mark.asyncio]

# ---------------------------------------------------------------------------
# Parametrized payload table
# Each entry: (payload_override, expected_status, reason)
# ---------------------------------------------------------------------------
SUBMISSION_PAYLOADS = [
    # Injection in language field — allowlist must reject
    (
        {"language": "python; rm -rf /", "source_code": "print(1)"},
        422,
        "Shell metachar in language must be rejected",
    ),
    (
        {"language": "../../../etc/passwd", "source_code": "x"},
        422,
        "Path traversal in language must be rejected",
    ),
    # XSS in source_code — stored not rendered, so accepted
    # (source_code is executed in sandbox, never rendered as HTML)
    (
        {"language": "python", "source_code": "<script>alert(1)</script>"},
        201,
        "XSS in source_code is accepted — stored safely, not rendered",
    ),
    # Size limits
    (
        {"language": "python", "source_code": "x" * 65_001},
        422,
        "Source code exceeding 64KB must be rejected",
    ),
    (
        {"language": "python", "source_code": "x" * 64_000},
        201,
        "Source code at exactly 64KB must be accepted",
    ),
    # Valid baseline
    (
        {"language": "python", "source_code": "print('hello')"},
        201,
        "Valid Python submission must be accepted",
    ),
    # Unsupported language
    (
        {"language": "cobol", "source_code": "HELLO WORLD"},
        422,
        "Unsupported language must be rejected",
    ),
    # Empty source code
    (
        {"language": "python", "source_code": ""},
        422,
        "Empty source code must be rejected",
    ),
]


@pytest.mark.input
@pytest.mark.parametrize(
    "payload_override, expected_status, reason",
    SUBMISSION_PAYLOADS,
)
async def test_TC_Input_001_submission_validation(
    client, alice_token, payload_override, expected_status, reason
):
    """TC-Input-001: Submission endpoint enforces language allowlist and size limits.

    Threat: TH-07 — input validation bypass leading to DoS or injection.
    Code Contract CI-02: Pydantic validates all input at the API layer.

    Additional oracle for 422 responses: the error body must not contain
    sql, traceback, or internal — validation errors must not leak system details.
    """
    payload = {
        "problem_id": "prob_test_001",
        "contest_id": "cst_test_001",
        **payload_override,
    }

    resp = await client.post(
        "/api/v1/submissions",
        json=payload,
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    assert resp.status_code == expected_status, (
        f"[{reason}] Expected {expected_status}, "
        f"got {resp.status_code}: {resp.text[:200]}"
    )

    if resp.status_code == 422:
        body_lower = str(resp.json()).lower()
        assert "sql" not in body_lower,       "422 must not contain SQL keywords"
        assert "traceback" not in body_lower, "422 must not contain traceback"
        assert "internal" not in body_lower,  "422 must not contain 'internal'"
