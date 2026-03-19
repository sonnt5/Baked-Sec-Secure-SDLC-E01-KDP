# code/reference/fuzz/test_hypothesis.py
# Chapter 8, Lab 8.7: Hypothesis Property-Based Tests
#
# Reference implementation — open only after completing your own.
# Run: pytest code/reference/fuzz/test_hypothesis.py -v --hypothesis-show-statistics
# Install: pip install hypothesis --break-system-packages
#
# Property-based tests encode security INVARIANTS — conditions that must hold
# for ANY valid input, not just the examples a developer thought to write.

import pytest
from decimal import Decimal
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Property 1: Scoring always returns int
# ---------------------------------------------------------------------------
# allow_nan=False: Decimal NaN cannot be converted to int — would cause
#   ValueError on every call, making the test a false positive.
# allow_infinity=False: same reason; penalty of infinity is not a real case.
@given(
    base_score=st.integers(min_value=0, max_value=1_000_000),
    wrong_attempts=st.integers(min_value=0, max_value=1_000),
    penalty=st.decimals(
        min_value=Decimal("0"), max_value=Decimal("100"),
        allow_nan=False,
        allow_infinity=False,
    ),
)
@settings(max_examples=500, suppress_health_check=[HealthCheck.too_slow])
def test_scoring_always_returns_integer(base_score, wrong_attempts, penalty):
    """Property: calculate_penalty_score always returns int, never float.

    Security relevance: float return would introduce precision errors
    that asymmetrically disadvantage contestants with fractional penalties.
    This is a fairness invariant — its violation would be exploitable.
    """
    from app.services.scoring import calculate_penalty_score

    result = calculate_penalty_score(base_score, wrong_attempts, penalty)

    assert isinstance(result, int), (
        f"Result must be int, got {type(result).__name__}: "
        f"base={base_score}, attempts={wrong_attempts}, penalty={penalty}"
    )


# ---------------------------------------------------------------------------
# Property 2: Score is monotonically non-increasing with wrong attempts
# ---------------------------------------------------------------------------
@given(
    base_score=st.integers(min_value=0, max_value=1_000_000),
    wrong_attempts=st.integers(min_value=0, max_value=100),
)
def test_scoring_monotonically_non_increasing(base_score, wrong_attempts):
    """Property: adding one more wrong attempt never increases the score.

    Security relevance: a bug where score increases with wrong attempts would
    be exploitable — contestants could artificially inflate their scores.
    """
    from app.services.scoring import calculate_penalty_score

    penalty = Decimal("20")
    score_n   = calculate_penalty_score(base_score, wrong_attempts,     penalty)
    score_n1  = calculate_penalty_score(base_score, wrong_attempts + 1, penalty)

    assert score_n >= score_n1, (
        f"Score must not increase with more wrong attempts: "
        f"{score_n} (n={wrong_attempts}) < {score_n1} (n+1={wrong_attempts + 1})"
    )


# ---------------------------------------------------------------------------
# Property 3: Login errors never contain internal stack details
# ---------------------------------------------------------------------------
# 8+ patterns covering the full CODING WAR stack:
#   traceback, stack_trace — Python error output
#   sqlalchemy, asyncpg    — ORM and DB driver (reveals DB type and version)
#   postgresql             — DB server
#   redis                  — cache layer
#   /app/                  — server filesystem path
#   pydantic, uvicorn      — framework fingerprinting
INTERNAL_LEAK_PATTERNS = [
    "traceback",
    "stack_trace",
    "sqlalchemy",
    "asyncpg",
    "postgresql",
    "redis",
    "/app/",
    "pydantic",
    "uvicorn",
    "alembic",
]


@given(
    email=st.emails(),
    password=st.text(min_size=1, max_size=200),
)
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_login_error_never_leaks_internals(email, password):
    """Property: login error responses never contain internal implementation details.

    Security relevance: any internal detail in an error response gives an attacker
    information about the technology stack, query structure, or server layout —
    reducing the effort required for a targeted attack.
    """
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )

    if resp.status_code in {400, 401, 422, 429}:
        body_lower = resp.text.lower()
        for pattern in INTERNAL_LEAK_PATTERNS:
            assert pattern not in body_lower, (
                f"Error response leaks internal detail {pattern!r}: "
                f"email={email!r}, status={resp.status_code}"
            )


# ---------------------------------------------------------------------------
# Property 4: Submission public_ids are always opaque
# ---------------------------------------------------------------------------
@given(
    source_code=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
        min_size=1, max_size=100,
    )
)
@settings(max_examples=50)
@pytest.mark.asyncio
async def test_submission_ids_always_opaque(source_code):
    """Property: submission public_ids are non-integer and have sufficient entropy.

    Tested through the API (not the generator function) because:
    - The API pipeline may transform IDs (serializer, ORM mapping, schema)
    - A unit test of the generator would not catch a downstream int() cast
    - Integration-level tests cover code paths that unit tests miss

    Security relevance: sequential integer IDs allow trivial enumeration (TH-02).
    """
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.core.security import create_access_token

    token = create_access_token({"sub": "usr_hyp_test", "role": "contestant"})

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/api/v1/submissions",
            json={
                "language": "python",
                "source_code": source_code,
                "problem_id": "prob_test_001",
                "contest_id": "cst_test_001",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    if resp.status_code in {200, 201, 202}:
        public_id = resp.json().get("public_id", "")
        assert not public_id.isdigit(), (
            f"Submission ID must not be a plain integer: {public_id!r}"
        )
        assert len(public_id) >= 8, (
            f"Submission ID must have sufficient length: {public_id!r}"
        )
