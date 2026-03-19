# Solution 7.6 — Secure Coding Standard Profile & SAST/SCA Triage

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. Your approach may differ and still be correct.

---

## Key Insights

### What makes an SCSP useful vs. a compliance artifact

An SCSP that a team will actually use has three properties:
1. **Rules have reasons.** "Never use `shell=True`" is a directive. "Never use `shell=True` because it allows the shell to interpret metacharacters as commands — use the list API instead" is a rule. Developers who understand the reason make better decisions in edge cases.
2. **Enforcement is specified per rule.** If a rule has no associated SAST check, no test, and no checklist item, it only has a chance of being followed.
3. **Exceptions have a process.** Every real codebase has situations where a rule creates genuine friction. An SCSP without an exception process will be ignored.

### Semgrep rules — level of specificity

The reference rules in `code/semgrep-rules/coding-war-custom.yaml` target specific patterns (`db.execute($STR + ...)`, `subprocess.run(..., shell=True, ...)`). They do not flag generic "SQL query" or "subprocess" usage — only the unsafe pattern.

The message in each rule tells a developer:
1. What the rule detected
2. What the correct alternative is
3. Which ASVS control and CWE number apply

A rule whose message just says "security issue detected" will be suppressed immediately.

### SF-001 triage: the two-part verdict

**Conclusion:** True Positive — the code is genuinely vulnerable.

The `sort_field` parameter in the f-string is user-supplied (from `GET /submissions?sort=`). Standard parameterization cannot fix it (ORDER BY cannot be parameterized). This is IS-01 from Lab 7.3.

**Closure criteria that a second engineer can verify:**
1. `semgrep scan --config coding-war-custom.yaml app/` produces zero findings for `ci01.raw-sql-execute`
2. `pytest -k test_sort_field_allowlist` passes with inputs: `sort=score` → 200, `sort='; DROP TABLE--` → 422
3. Code review confirms `ALLOWED_SORT_FIELDS` dict is used — no raw string in `ORDER BY`

"The code has been fixed and reviewed" is not a criterion — it cannot be verified independently.

### CVE-2024-33663 triage: context-dependent exploitability

The CVE applies when `jwt.decode(token, key)` is called without specifying `algorithms`. In that case, `python-jose` accepts the algorithm from the token header — including `"alg": "none"`, which requires no signature.

**Investigation required before confirming severity:**
- Search all call sites: `grep -r "jwt.decode" app/`
- For each call site, verify whether `algorithms=['ES256']` (or equivalent) is specified
- If all call sites specify `algorithms` explicitly: **Not-Exploitable in this codebase** (document the evidence)
- If any call site omits `algorithms`: **True Positive** — that endpoint accepts unsigned tokens claiming any role

The correct long-term fix is migration to `joserfc` (actively maintained) or `PyJWT` (widely used, explicit algorithms required by default).

### Security exception — what makes it binding

A security exception has no value unless it includes:
- **An expiration date** — a specific calendar date, not "when the Redis redesign is complete"
- **Compensating controls** — real mitigations, not intentions. "We will monitor" is not a control.
- **Conditions that void it early** — if the compensating controls are removed, the exception is automatically void

Example compensating controls for missing account lockout:
1. IP-level rate limit of 5 requests/minute on `POST /auth/login` (verifiable: `pytest -k test_login_rate_limit`)
2. Anomaly detection alert if any IP exceeds 20 login attempts in 5 minutes (verifiable: alert fires in staging)
3. Forced password reset for accounts with >10 failed attempts in 24h (verifiable: manual test)

---

*Back to the lab: [labs/lab-7.6.md](../labs/lab-7.6.md)*
