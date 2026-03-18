# Solution 7.7 — Code Review Checklist, Review Minutes & Security Test Matrix

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. Your approach may differ and still be correct.

---

## Key Insights

### What makes a checklist item good

A useful checklist item has two properties: it is **observable** (you can determine pass or fail by reading the code or running a command) and it is **specific to this codebase** (replacing "CODING WAR" with another project name would make it wrong or meaningless).

Examples of the failure modes:
- "Input is validated" — not observable, not specific
- "Pydantic schemas use `Literal['python','cpp','java']` for the `language` field" — observable, specific
- "No SQL injection" — not observable
- "`db.execute()` is called only in `app/repositories/` modules — SAST rule `ci01` in `semgrep-rules/` enforces this" — observable, specific

The checklist should be short enough to actually complete on a PR review. Long checklists become checkbox exercises.

### PR-241 — findings beyond the known one

**Finding 1 (known from Lab 7.3):** ORDER BY injection in `submission_repo.py:147` — `sort_field` from query parameter interpolated directly into SQL.

**Finding 2 — IDOR on leaderboard data:** The leaderboard endpoint returns per-contestant data. If `submission_id` or `user_id` values in the response are not opaque (e.g., sequential integers), an attacker can enumerate all submissions. Check: does `SubmissionPublicResponse` expose `id` (integer primary key) or `public_id` (CSPRNG token)?

**Finding 3 — Unbounded pagination:** `page=1` is accepted but there is no `max_page` or `page_size` limit enforced. An attacker can request `page_size=10000` and receive the entire leaderboard in one response — creating a scraping and DoS risk. Check: does `app/schemas/leaderboard.py` enforce `page_size: int = Field(50, le=100)`?

### Security test matrix — what makes a criterion observable

The test criterion must specify the exact HTTP response an independent observer would receive, without knowing the implementation:

| Weak | Strong |
|------|--------|
| "Injection attempt is rejected" | "Request returns 422; body contains `error_code: VALIDATION_ERROR`; body does not contain the injected string" |
| "IDOR is prevented" | "GET /submissions/{alice_sub_id} with Bob's JWT returns 403; body does not contain `source_code`" |
| "Rate limit works" | "The 6th login request within 60s returns 429; body contains `retry_after` as a positive integer" |

### Discussion answers

**1. A senior developer pushes back on a checklist item.**
Evaluate the argument on whether the item is actually observable and specific, and whether the control it represents is enforced elsewhere. If SAST already catches the same pattern, the checklist item may genuinely be redundant. If the item represents a judgment call that SAST cannot make, it belongs in the checklist. Ask: "If we removed this item, how would we know if a new engineer violated the pattern?"

**2. Developer fixes one finding, argues two are acceptable.**
Document the disagreement formally. If you have the authority, require both to be fixed before merge. If you do not, escalate to the tech lead — but document your finding, your recommendation, and the outcome. A security finding that was known and deferred must be tracked as a risk item, not discarded.

**3. Intermittent test failure.**
An intermittent security test failure almost always indicates a race condition in the underlying control — not a flaky test. The security property (account lockout, rate limit, TOCTOU prevention) only works reliably if it is atomic. Investigate the control implementation before debugging the test. If the test is exposing a real race, the finding is more important than the passing rate.

---

*Back to the lab: [labs/lab-7.7.md](../labs/lab-7.7.md)*
