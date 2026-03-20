# code/reference/tests/security/test_rate_limiting.py
# Chapter 8, Lab 8.2: Rate Limiting Security Tests
#
# Reference implementation — open only after completing your own.
# Run: pytest -m "security and ratelimit" -v

import pytest

pytestmark = [pytest.mark.security, pytest.mark.asyncio]


@pytest.mark.ratelimit
async def test_TC_RateLimit_001_login_rate_limit_triggers_429(client):
    """TC-RateLimit-001: 6th login request within the window returns 429.

    Threat: TH-01 — credential stuffing.
    Oracle:
      - Requests 1-5: NOT 429 (must not be blocked prematurely)
      - Request 6:    429 with Retry-After header
    Note: checking only request 6 is insufficient — the test would pass
    even if the rate limiter triggered on request 1.
    """
    for i in range(5):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@test.com", "password": f"wrong_{i}"},
        )
        assert resp.status_code != 429, (
            f"Request {i + 1} must not be rate limited yet"
        )

    resp_blocked = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@test.com", "password": "wrong_6"},
    )
    assert resp_blocked.status_code == 429
    assert "Retry-After" in resp_blocked.headers, (
        "429 must include Retry-After header"
    )
    assert resp_blocked.json().get("error_code") == "RATE_LIMIT_EXCEEDED"


@pytest.mark.ratelimit
async def test_TC_RateLimit_002_submission_rate_limit_per_user(client, alice_token):
    """TC-RateLimit-002: Per-user submission quota enforced.

    Threat: TH-07 — DoS via submission flooding.
    Oracle: submissions 1-10 succeed; submission 11 returns 429.
    """
    limit = 10
    payload = {
        "language": "python",
        "source_code": "print('hello')",
        "problem_id": "prob_test_001",
        "contest_id": "cst_test_001",
    }
    headers = {"Authorization": f"Bearer {alice_token}"}

    for i in range(limit):
        resp = await client.post("/api/v1/submissions", json=payload, headers=headers)
        assert resp.status_code in {200, 201, 202}, (
            f"Submission {i + 1} within limit must succeed, got {resp.status_code}"
        )

    resp_over = await client.post("/api/v1/submissions", json=payload, headers=headers)
    assert resp_over.status_code == 429, (
        f"Submission beyond limit must return 429, got {resp_over.status_code}"
    )


@pytest.mark.ratelimit
async def test_TC_RateLimit_003_retry_after_is_positive_integer(client):
    """TC-RateLimit-003: Retry-After header value must be a positive integer.

    Oracle: Retry-After is a digit string and its integer value > 0.
    A negative or zero value would be meaningless to the client.
    """
    for _ in range(6):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@test.com", "password": "wrong"},
        )

    assert resp.status_code == 429
    retry_after = resp.headers.get("Retry-After", "")
    assert retry_after.isdigit(), (
        f"Retry-After must be a digit string, got: {retry_after!r}"
    )
    assert int(retry_after) > 0, (
        f"Retry-After must be positive, got: {retry_after}"
    )
