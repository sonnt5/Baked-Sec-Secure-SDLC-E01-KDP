# code/reference/tests/conftest.py
# Chapter 8, Lab 8.2: pytest Security Test Infrastructure
#
# Reference implementation — open only after completing your own.
#
# Design decisions documented here are the subject of Lab 8.2 Task 1:
#   Q1: Why are ALICE_ID, BOB_ID, ADMIN_ID fixed strings?
#   Q2: Why must the client fixture use scope="function"?
#   Q3: Why does admin_token include mfa_verified=True?

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# ---------------------------------------------------------------------------
# Fixed test user IDs
# ---------------------------------------------------------------------------
# Q1 answer: fixed IDs make tests deterministic and debuggable.
# If IDs were random, the alice_submission fixture and the IDOR assertion
# would need complex coordination. Fixed IDs also make log traces readable.
ALICE_ID = "usr_alice_test_fixed"   # contestant role
BOB_ID   = "usr_bob_test_fixed"     # contestant role, different from Alice
ADMIN_ID = "usr_admin_test_fixed"   # admin role with MFA verified


# ---------------------------------------------------------------------------
# HTTP client fixture
# ---------------------------------------------------------------------------
# Q2 answer: scope="function" gives each test a fresh client with no state
# carry-over. If scope="session", a rate-limit test that exhausts the limit
# would cause the next test's legitimate request to return 429 — a false
# failure. Cookie or session state from one test must not affect another.
@pytest_asyncio.fixture(scope="function")
async def client():
    """Fresh async HTTP client per test — no state carry-over."""
    from app.main import app
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


# ---------------------------------------------------------------------------
# Database fixture (session-scoped — shared across tests for performance)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="session")
async def db():
    """Async database session for test data setup."""
    from app.database import get_test_db
    async with get_test_db() as session:
        yield session


# ---------------------------------------------------------------------------
# Token fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def alice_token():
    """JWT for contestant Alice."""
    from app.core.security import create_access_token
    return create_access_token({"sub": ALICE_ID, "role": "contestant"})


@pytest.fixture
def bob_token():
    """JWT for contestant Bob (different user from Alice — used in IDOR tests)."""
    from app.core.security import create_access_token
    return create_access_token({"sub": BOB_ID, "role": "contestant"})


@pytest.fixture
def admin_token():
    """JWT for admin user with MFA verified.

    Q3 answer: mfa_verified=True enforces Code Contract CI-03 —
    every /admin/* endpoint requires Depends(require_admin_mfa).
    This fixture simulates a legitimate admin session that has completed MFA.
    If CI-03 is changed to check a different claim name, this fixture
    must break — the coupling is intentional.
    """
    from app.core.security import create_access_token
    return create_access_token({
        "sub": ADMIN_ID,
        "role": "admin",
        "mfa_verified": True,
    })


# ---------------------------------------------------------------------------
# Data fixtures
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def alice_submission(db):
    """Submission record owned by Alice.

    Used in IDOR tests: Bob must not be able to access this submission.
    The fixture creates a real DB record so the route handler executes the
    full ownership check path.
    """
    from tests.factories import SubmissionFactory
    return await SubmissionFactory.create(user_id=ALICE_ID, db=db)


# ---------------------------------------------------------------------------
# Marker registration
# ---------------------------------------------------------------------------
def pytest_configure(config):
    config.addinivalue_line("markers", "security: security test — runs in CI gate")
    config.addinivalue_line("markers", "auth: authentication tests")
    config.addinivalue_line("markers", "idor: authorization / IDOR tests")
    config.addinivalue_line("markers", "ratelimit: rate limiting tests")
    config.addinivalue_line("markers", "crypto: cryptography usage tests")
    config.addinivalue_line("markers", "input: input validation tests")
    config.addinivalue_line("markers", "admin: admin access control tests")
    config.addinivalue_line("markers", "session: session management tests")
    config.addinivalue_line("markers", "logic: business logic security tests")
