# Solution 7.6 — SCSP & SAST/SCA Triage

> [!WARNING]
> **Reference Solution** — Complete the lab on your own before consulting this.

---

## SAST Triage TR-SAST-2025-003 — Key Fields

**Triage Conclusion:** True Positive. The `sort_field` variable on line 147 is interpolated directly into the SQL string via an f-string: `f"ORDER BY {sort_field} DESC"`. The value comes from the GET query parameter `?sort=` with no validation. An attacker can supply `sort=score; DROP TABLE submissions; --` or use time-based blind SQLi via `sort=CASE WHEN (SELECT count(*) FROM users) > 0 THEN score ELSE submission_time END`.

**Severity:** High (CWE-89). While direct `DROP TABLE` might fail on DB permissions, time-based blind SQLi can enumerate DB schema and data. The `contest_id` in the same query is also string-concatenated and is also injectable.

**Closure Criteria must include:** (1) SAST re-run on fixed code returns zero findings for `sqlalchemy-execute-raw-query` in `submission_repo.py`. (2) Unit test `test_sort_injection_returns_422_for_unknown_field` passes. (3) Manual test: `sort="'; DROP TABLE submissions; --"` returns 422 (not 500). Not just "fix the code" — the SAST re-run is essential to confirm the fix is actually present in the committed code.

---

## SCA Triage TR-SCA-2025-007 — Key Points

**Why "True Positive (potentially)" is the correct conclusion:**
The CVE is real, but whether it is exploitable in CODING WAR depends on implementation. If every `jwt.decode()` call specifies `algorithms=['ES256']`, the attack vector is closed even with the vulnerable library version. The triage therefore requires a code review step before the final severity can be determined. This is the correct approach — filing it as "True Positive, Critical" without checking would lead to unnecessary emergency response; "False Positive" without checking would be irresponsible. "True Positive (conditionally)" with a code review step is the professionally correct middle ground.

---

## Security Exception — Key Quality Criteria

A well-written Security Exception must have:
1. **Bounded expiration** — not "until we fix it" but "expires Sprint 5, date DD/MM/YYYY"
2. **Verifiable compensating controls** — not "we'll monitor it" but "Alert rule: >5 unique IPs targeting same email within 10min → PagerDuty alert ID XYZ"
3. **Acceptance conditions that could invalidate the exception** — if IP rate limit is removed, the exception is void
4. **Named approver** — not "the team" but "AppSec Lead [name] + Engineering Manager [name]"

---

*Back to the lab: [labs/lab-7.6.md](../labs/lab-7.6.md)*
