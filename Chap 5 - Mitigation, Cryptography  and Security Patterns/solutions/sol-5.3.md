# Solution 5.3 — Security Design Patterns: Pattern Application Worksheet

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 3 — Code Analysis (Reference Answers)

**Question 1 — 6 Layers of Defense in Depth for submission:**

| Layer | Control | Lever |
|-------|---------|-------|
| 1 | JWT Authentication via `Depends(get_current_user)` — only authenticated users can submit | Reduce |
| 2 | Rate limiting `@limiter.limit('10/hour')` — prevents flooding | Reduce |
| 3 | Pydantic schema validation `SubmissionCreate` — rejects invalid language, oversized code | Reduce + Allowlist |
| 4 | Contest enrollment check `Depends(verify_contest_enrollment)` — only enrolled users in active contests | Resist |
| 5 | JudgeService sandbox + resource limits — contains malicious code execution | Resist |
| 6 | `AuditLogMiddleware` (implicit, logs every request regardless of outcome) | Recover |

**Question 2 — Why must each layer be independent?**

Independence means: if an attacker bypasses Layer 3 (Pydantic validation — e.g., by sending a request with a valid JWT but a raw HTTP client that skips client-side validation), they still face Layer 4 (contest enrollment check) and Layer 5 (sandbox). Each layer operates on different assumptions: Layer 1 checks identity, Layer 3 checks data shape, Layer 4 checks business state, Layer 5 checks execution environment. They cannot be bypassed as a unit — each requires a different attack vector.

If Layer 3 is bypassed (e.g., oversized code reaches JudgeService): Layer 5 resource limits still kill the process at 256MB. The attack succeeds at one layer but fails at another — this is the definition of effective Defense in Depth.

**Question 3 — `verify_contest_enrollment()` implementation:**

```python
from fastapi import Depends, HTTPException, status
from datetime import datetime, timezone
from app.models import ContestRegistration, Contest
from app.core.security import get_current_user
from app.db import get_db

async def verify_contest_enrollment(
    contest_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
) -> Contest:
    """
    PEP: enforce user is enrolled + contest is currently active.
    Raises 403 if not enrolled, 422 if contest not active.
    """
    now = datetime.now(timezone.utc)

    # Check contest exists and is active
    contest = await db.get(Contest, contest_id)
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    if not (contest.start_time <= now <= contest.end_time):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Contest is not currently active"
        )

    # Check enrollment — Least Privilege: contestant must be registered
    registration = await db.execute(
        select(ContestRegistration)
        .where(
            ContestRegistration.contest_id == contest_id,
            ContestRegistration.user_id == current_user.id
        )
    )
    if not registration.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this contest"
        )

    return contest
```

**Question 4 — `validate_second_approval()` pseudocode:**

```python
async def validate_second_approval(
    approval2_token: str,
    contest_id: str,
    approver1_id: str
) -> bool:
    """
    Separation of Privilege: check that:
    1. Token is valid and not expired (max 60s window)
    2. Token was issued for THIS specific contest_id
    3. Approver2 is different from approver1 (not self-approving)
    4. Approver2 has admin role
    5. Token is single-use (mark as used after validation)
    """
    token_data = await approval_token_store.get(approval2_token)

    if not token_data:
        return False  # Token not found or already used

    if token_data['contest_id'] != contest_id:
        return False  # Token for different contest

    if token_data['approver_id'] == approver1_id:
        return False  # Same person cannot approve twice

    if token_data['role'] != 'admin':
        return False  # Approver2 must be admin

    if datetime.utcnow() - token_data['issued_at'] > timedelta(seconds=60):
        return False  # Approval window expired

    # Mark token as used — prevent replay
    await approval_token_store.delete(approval2_token)
    return True
```

---

*Back to the lab: [labs/lab-5.3.md](../labs/lab-5.3.md)*
