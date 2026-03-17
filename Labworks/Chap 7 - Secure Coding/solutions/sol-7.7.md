# Solution 7.7 — Checklist, Code Review Minutes & Test Matrix

> [!WARNING]
> **Reference Solution** — Complete the lab on your own before consulting this.

---

## Key Principles for Quality Artifacts

**Checklist quality test:** Replace every CODING WAR-specific example with "see your codebase" — if the checklist still makes sense, it's too generic. A strong checklist item for authentication says `grep for jwt.decode without algorithms kwarg` and `unit test alg=none → 401`, not "verify JWT is validated."

**Code Review Minutes — what makes closure criteria strong:**
Weak: "Fix the SQL injection issue." Strong: "(1) No Semgrep findings on `sqlalchemy-execute-raw-query` in `submission_repo.py` after fix. (2) Unit test `test_sort_field_allowlist` passes — `sort=unknown_field` returns 422. (3) Reviewer manually re-reads the SQL query and confirms no f-string interpolation." The closure criteria must be independently verifiable by someone who didn't write the fix.

**Test Matrix pass/fail criteria quality:**
The hallmark of a weak pass criterion: "Verify security is maintained." The hallmark of a strong one: "Return code is 403, response body contains `error_code: PERMISSION_DENIED`, and the response body does NOT contain `source_code`." Observable, measurable, binary. A tester who has never seen the system should be able to determine pass or fail from the criterion alone.

---

## Team-added test (VC-01 chain):

| Threat | Control | Location | Test Type | Test Data | Pass/Fail |
|--------|---------|---------|-----------|-----------|----------|
| User enumeration via login error messages | Uniform error response | `app/core/error_handlers.py` | Unit + timing test | (1) POST /auth/login with valid email + wrong password. (2) POST /auth/login with nonexistent email + any password. Measure both response body and response time. | Pass: both return identical JSON body `{"error_code": "AUTH_INVALID", "message": "Invalid credentials"}`. Response time difference < 50ms (Argon2id dummy verify runs in both cases). |

---

*Back to the lab: [labs/lab-7.7.md](../labs/lab-7.7.md)*
