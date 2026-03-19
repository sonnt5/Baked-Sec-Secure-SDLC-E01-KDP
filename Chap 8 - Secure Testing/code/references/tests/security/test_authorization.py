# code/reference/tests/security/test_authorization.py
# Chapter 8, Lab 8.2: Authorization / IDOR Security Tests
#
# Reference implementation — open only after completing your own.
# Run: pytest -m "security and idor" -v

import re
import pytest

pytestmark = [pytest.mark.security, pytest.mark.asyncio]


@pytest.mark.idor
async def test_TC_IDOR_001_contestant_cannot_read_other_submission(
    client, alice_token, bob_token, alice_submission
):
    """TC-IDOR-001: Bob cannot read Alice's submission.

    This is the most critical test in the suite — it is evidence that
    Code Contract CI-01 (verify_submission_owner) is enforced on every route.
    If this test is removed or disabled, CI-01 is assumed but unverified.

    Threat: TH-02 (IDOR on /submissions/{id}).
    Oracle:
      - Alice (owner) → 200
      - Bob (attacker) → 403 or 404
      - Bob's response does NOT contain source_code field
    """
    sub_id = alice_submission.public_id

    resp_alice = await client.get(
        f"/api/v1/submissions/{sub_id}",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert resp_alice.status_code == 200

    resp_bob = await client.get(
        f"/api/v1/submissions/{sub_id}",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert resp_bob.status_code in {403, 404}, (
        f"Attacker must not read another user's submission, got {resp_bob.status_code}"
    )
    # source_code must never appear in an error response
    assert "source_code" not in resp_bob.json(), (
        "source_code must not be present in 403/404 response body"
    )


@pytest.mark.idor
async def test_TC_IDOR_002_admin_can_access_any_submission(
    client, admin_token, alice_submission
):
    """TC-IDOR-002: Admin role bypasses ownership check.

    Verifies the positive case — admin bypass must work for the system
    to be operable (admins need to review all submissions).
    Oracle: 200 for admin accessing any contestant's submission.
    """
    sub_id = alice_submission.public_id

    resp = await client.get(
        f"/api/v1/submissions/{sub_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200, (
        f"Admin must access any submission (200), got {resp.status_code}"
    )


@pytest.mark.idor
async def test_TC_IDOR_003_submission_ids_are_opaque(client, alice_token):
    """TC-IDOR-003: Submission public_ids must not be sequential integers.

    Sequential integer IDs allow trivial enumeration of all submissions
    with a simple loop (1, 2, 3...). Opaque CSPRNG IDs prevent this.

    Oracle: IDs are not plain integers, length >= 8, not sequentially incrementing.
    """
    ids = []
    for i in range(3):
        resp = await client.post(
            "/api/v1/submissions",
            json={
                "language": "python",
                "source_code": f"print({i})",
                "problem_id": "prob_test_001",
                "contest_id": "cst_test_001",
            },
            headers={"Authorization": f"Bearer {alice_token}"},
        )
        assert resp.status_code in {200, 201, 202}
        ids.append(resp.json()["public_id"])

    for id_ in ids:
        assert not id_.isdigit(), f"ID must not be a plain integer: {id_!r}"
        assert len(id_) >= 8,    f"ID must have sufficient length: {id_!r}"

    # Check for sequential pattern (sub_1, sub_2, sub_3)
    suffixes = [re.sub(r"^[^_]+_", "", id_) for id_ in ids]
    are_sequential = (
        all(s.isdigit() for s in suffixes)
        and all(
            int(suffixes[i]) + 1 == int(suffixes[i + 1])
            for i in range(len(suffixes) - 1)
        )
    )
    assert not are_sequential, f"IDs must not be sequential: {ids}"
