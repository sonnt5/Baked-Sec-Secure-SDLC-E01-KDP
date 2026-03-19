# code/reference/tests/security/test_authentication.py
# Chapter 8, Lab 8.2: Authentication Security Tests
#
# Reference implementation — open only after completing your own.
# Run: pytest -m "security and auth" -v

import base64
import json
import time

import pytest
import pytest_asyncio

pytestmark = [pytest.mark.security, pytest.mark.asyncio]


@pytest.mark.auth
async def test_TC_Auth_001_expired_token_rejected(client):
    """TC-Auth-001: Expired JWT must be rejected with no grace period.

    Threat: TH-01 — session replay with an expired token.
    Oracle: 401; token value NOT in response body; no traceback in response.
    """
    from app.core.security import create_access_token

    expired_token = create_access_token(
        {"sub": "usr_alice", "role": "contestant"},
        expires_delta=-3600,
    )

    resp = await client.get(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert resp.status_code == 401
    assert resp.json().get("error_code") == "AUTH_EXPIRED"
    body_str = str(resp.json()).lower()
    assert "traceback" not in body_str
    assert "stack" not in body_str
    # Token value must not be reflected
    assert expired_token[:10] not in resp.text


@pytest.mark.auth
async def test_TC_Auth_002_algorithm_none_rejected(client):
    """TC-Auth-002: JWT with alg=none must be rejected.

    Threat: TH-08 — algorithm confusion attack (CVE-2024-33663 class).
    Oracle: 401 even when forged payload claims admin role.
    """
    header = base64.urlsafe_b64encode(
        json.dumps({"alg": "none", "typ": "JWT"}).encode()
    ).decode().rstrip("=")

    payload = base64.urlsafe_b64encode(
        json.dumps({
            "sub": "usr_admin",
            "role": "admin",
            "mfa_verified": True,
            "exp": 9_999_999_999,
        }).encode()
    ).decode().rstrip("=")

    forged = f"{header}.{payload}."

    resp = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {forged}"},
    )

    assert resp.status_code == 401, (
        f"alg=none forged token must be rejected, got {resp.status_code}"
    )


@pytest.mark.auth
async def test_TC_Auth_003_login_error_identical_for_valid_and_invalid_user(client):
    """TC-Auth-003: Login errors must be identical regardless of whether email exists.

    Threat: user enumeration (VC-01 step 2 from Lab 7.1).
    Oracle: same status, same error_code, same message for both cases.
    Note: timing must also be identical (covered by constant-time dummy hash in
    app/core/error_handlers.py — see Lab 7.5 fixed version).
    """
    resp_wrong_pw = await client.post(
        "/api/v1/auth/login",
        json={"email": "alice@test.com", "password": "wrong_password"},
    )
    resp_no_user = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody_xyz@notexist.com", "password": "wrong_password"},
    )

    assert resp_wrong_pw.status_code == 401
    assert resp_no_user.status_code == 401

    assert resp_wrong_pw.json()["error_code"] == resp_no_user.json()["error_code"], (
        "error_code must be identical — different codes leak user existence"
    )
    assert resp_wrong_pw.json()["message"] == resp_no_user.json()["message"], (
        "message must be identical — different messages leak user existence"
    )

    combined = resp_wrong_pw.text + resp_no_user.text
    assert "alice@test.com" not in combined
    assert "nobody_xyz" not in combined


@pytest.mark.auth
async def test_TC_Auth_004_missing_token_returns_401_not_403(client):
    """TC-Auth-004: Missing Authorization header must return 401 AUTH_REQUIRED.

    Oracle: 401 (not 403); error_code is AUTH_REQUIRED.
    Note: 401 = unauthenticated; 403 = authenticated but forbidden.
    Using 403 for missing credentials is a semantic error.
    """
    resp = await client.get("/api/v1/submissions")
    assert resp.status_code == 401
    assert resp.json().get("error_code") == "AUTH_REQUIRED"


@pytest.mark.auth
async def test_TC_Auth_005_malformed_tokens_rejected(client):
    """TC-Auth-005: All structurally invalid tokens must return 401.

    Oracle: 401 for every variant; no internal details in response body.
    Tests 4 structurally distinct bad tokens.
    """
    bad_tokens = [
        "not-a-jwt",          # no dots at all
        "Bearer",             # keyword without token
        "abc.def",            # two segments (missing signature)
        "a.b.c.d.e",          # five segments (too many)
    ]
    for token in bad_tokens:
        resp = await client.get(
            "/api/v1/submissions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401, (
            f"Malformed token {token!r} must return 401, got {resp.status_code}"
        )
        body_str = str(resp.json()).lower()
        assert "traceback" not in body_str, (
            f"No traceback for malformed token {token!r}"
        )
        assert "stack" not in body_str
