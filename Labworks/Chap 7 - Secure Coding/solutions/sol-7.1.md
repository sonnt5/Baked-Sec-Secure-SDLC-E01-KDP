# Solution 7.1 — Design Invariants & Code Contracts

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. The approach shown here is one valid path. Your solution may differ and still be more appropriate for your context.

---

## Key Insights

### What distinguishes a contract from an assumption

An assumption says *what should be true*. A contract says *what must be true*, names the specific file or mechanism that enforces it, and provides a detection method a second engineer can run without asking the original author.

The most common failure pattern: teams write "all input must be validated" in their SDR and then have no SAST rule, no test, and no checklist item that would catch a handler that skips validation. The assumption never becomes a contract.

### Trust boundary map — what is often missed

- The judge result returned from a sandbox process is **untrusted** — it travels through a queue and could be tampered with before the application reads it. This is a common blind spot.
- Admin-authored content (problem statements, test cases) is **low-trust**, not trusted. An admin account may be compromised.
- Database read-back is not automatically trusted — if an attacker has written to the database (via a different exploit), reading that data back and rendering it without encoding creates a second-order XSS.

### High-value assets — beyond the obvious

Teams typically list: user credentials, JWT signing key. What is often missed:
- **Test case input/output files** — their secrecy is what makes a contest meaningful. Exposure is irreversible.
- **Verdict records** — if these can be modified, contest integrity fails silently.
- **The judge execution environment** — compromise here means arbitrary code execution on the host.

### Vulnerability chains — why combined severity exceeds individual steps

A chain's severity is set by the asset at the end, not the average of the steps. If the final step reaches `admin access + no MFA + scoreboard manipulation`, that is Critical even if the first step (user enumeration) is Low. The chain multiplies exploitability across steps, not just adds them.

**Common chains in CODING WAR:**
1. Verbose login error → email enumeration → targeted credential stuffing → account takeover
2. IDOR on submissions → read competing code → contestant strategy exposure (competition integrity)
3. Nested quantifier in regex → crafted judge output → judge worker DoS → contest availability failure

### What the Code Contract Document enables

The primary value is not preventing bugs — it is ensuring that a new engineer knows what constraints exist *before* they write their first line of code, not after a security review finds a violation.

A contract document also makes code reviews faster: instead of "is this safe?", reviewers ask "does this violate CI-03?" — which is a yes/no question with a specific answer.

---

## Reference Contract Examples

| Contract | Enforcement Location | Detection |
|----------|---------------------|-----------|
| All DB access via repository layer | `app/repositories/*.py` only | SAST rule `ci01.direct-db-in-handler`; test asserts no `db.execute()` import in `app/api/` |
| `language` field validated against allowlist | `app/schemas/submission.py` — `Literal['python','cpp','java']` | `test_invalid_language_returns_422`; Pydantic rejects at parse time |
| MFA required on all `/admin` endpoints | `@require_admin_mfa` Depends() in `app/api/admin/*.py` | `grep -r "@router\." app/api/admin/ | grep -v require_admin_mfa` |
| No PII in application logs | `LoggingMiddleware.REDACT_FIELDS` | Unit test: trigger login failure, assert log entry has no `email` or `password` field |

---

*Back to the lab: [labs/lab-7.1.md](../labs/lab-7.1.md)*
