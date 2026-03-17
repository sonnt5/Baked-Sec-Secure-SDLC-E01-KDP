# Lab 7.5 — Error Handling, Logging & Dependency Management

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: CODING WAR error/log code | Output: Error Model Spec + Log Schema + Dep. Audit

> [!NOTE]
> **OWASP ASVS v5.0.0:** V16.5.1 — generic message when unexpected or security-sensitive error occurs. V16.2.5 — when logging sensitive data, enforce logging redaction. V15.2.1 — application only contains components that have not reached end-of-life.

## Learning Objectives

- Write an Error Handler following the "Say Enough, Not Too Much" principle.
- Design a logging schema: sufficient for forensics, without exposing PII/secrets.
- Conduct a dependency audit: identify CVEs, update strategy.
- Complete ASVS V16 + V15.2 compliance check.

---

## Task 1 — Safe Error Handler Design

Study [`code/fixed/error_handlers.py`](../code/fixed/error_handlers.py).

> **Context:** Error handling has two separate channels: (1) **User-facing:** only `error_code` + user-friendly message (no stack trace, no DB details). (2) **Internal logs:** enough technical context to debug but WITHOUT raw secrets, passwords, tokens, or PII. This is a security architecture decision, not just a coding style.

Complete the error handling decision table:

| Error Scenario | HTTP Status | Error Code | Include in Response? | Log Level + What to Log | ASVS Note |
|---------------|------------|-----------|---------------------|------------------------|----------|
| User with email X not found during login | 401 | `AUTH_INVALID` | `error_code` only — same as wrong password (enumeration prevention) | WARN: `failed_login_attempt`, `ip_hash`, `user_agent_class`, `timestamp` (NOT email) | V16.5.1 + V16.3.1 |
| SQL constraint violation (duplicate submission) | 409 | `VALIDATION_ERROR` | "Submission already exists for this problem in this contest" | ERROR: `constraint_name`, `user_public_id`, `contest_id` (NOT raw SQL error) | V16.5.1: no DB internals |
| JWT expired token | 401 | `AUTH_EXPIRED` | "Session expired. Please log in again." | INFO: `token_expired_event`, `user_public_id`, `timestamp` (NOT token value) | V16.3.1 + V16.5.1 |
| Internal DB connection failure | 503 | `SERVICE_UNAVAILABLE` | "Service temporarily unavailable. retry_after: 60" | ERROR: `db_connection_failed`, `error_ref`, `timestamp` (NOT connection string) | V16.5.2: fails gracefully |
| Pydantic validation failure on submission | 422 | `VALIDATION_ERROR` | `field_errors` with field names + human-readable reasons (no code/stack trace) | DEBUG: `validation_failed`, `schema_name`, `field_list` (NOT raw input value for security fields) | V16.5.1 + V2.2 |

**Key question:** Why do both "user not found" and "wrong password" return the same `AUTH_INVALID` error code? What attack does this prevent, and what is the timing requirement for complete protection?

---

## Task 2 — Privacy-Safe Logging Schema (ASVS V16.2)

Design a complete log schema for CODING WAR — sufficient to investigate incidents, minimal PII exposure:

| Log Category | Required Fields (ASVS V16.2.1) | Fields NEVER Log | Security Event? (V16.3) |
|-------------|-------------------------------|-----------------|------------------------|
| **Authentication Events** | timestamp, request_id, event_type (login_success/failure/lockout), `actor_public_id` (NEVER email), `client_ip_hash` (SHA-256[:16]), `user_agent_class` (browser/mobile/bot — NOT full UA string), `mfa_used` (bool) | password (even hashed), email, full JWT token, raw IP address | YES — V16.3.1: all auth ops logged. Alert on: >5 failures/10min from same ip_hash |
| **Authorization Events** | timestamp, request_id, event_type (denied/granted), actor_public_id, resource_type, resource_public_id, action_attempted | JWT payload content, role details beyond role_name | YES — V16.3.2: failed auth attempts logged |
| **Submission Events** | timestamp, request_id, submission_public_id, contest_id, language, actor_public_id, verdict (after judging) | source_code (even partial — too large + sensitive), test case content, execution details beyond time_ms | Partial — log when verdict is suspicious |
| **Admin Actions** | timestamp, request_id, actor_public_id, action (create_contest/modify_verdict/export_data), affected_resource, mfa_session_id | Admin passwords, raw data content of exports | YES — V16.3.3: tamper-evident append-only storage |
| **Error Events** | timestamp, request_id, error_ref, error_type, path (no query params), exc_type (not exc_args) | Stack traces (internal sink only), exception message (may contain SQL/paths/tokens), request body | Partial — log security-relevant errors |

---

## Task 3 — Dependency Audit Report (ASVS V15.2)

Conduct a dependency audit for CODING WAR Python packages:

| Package | Current Version | Status | Known CVE? | Update Strategy | SBOM Included? |
|---------|---------------|--------|-----------|----------------|---------------|
| **fastapi** | 0.109.2 | Active | None known | Pin exact: `==0.109.2`. Dependabot PR auto-review. SemVer: patch updates auto-approve. | Yes — cyclonedx-py |
| **python-jose[cryptography]** | 3.3.0 | Active — WATCH | CVE-2024-33663 (older) | Investigate CVE applicability. Test: JWT behavior unchanged. Consider switching to `joserfc`. | Yes |
| **cryptography** | 42.0.2 | Active | None current | HIGH priority: update within 7 days of any CVE. Crypto libs = critical supply chain. | Yes — critical |
| **passlib[argon2]** | 1.7.4 | **STALE** — last update 2022 | None known but unmaintained | Plan migration to `argon2-cffi` directly. Set 90-day deadline to replace or verify security. | Yes — flag as stale |
| **sqlalchemy[asyncio]** | 2.0.27 | Active | None known | Dependabot auto-review. Major version pinned. | Yes |
| **pydantic** | 2.6.4 | Active | None known | Auto-update patch/minor. Pin major. | Yes |
| **gVisor (runtime)** | Release 20250303 | Active | None known | Pin by digest `sha256:...` not tag. Quarterly upgrade test with sandbox escape verification. | Via container image SBOM (Trivy) |
| \[Add more dependencies\] | | | | | |

After the audit, complete the ASVS V15.2 compliance table:

| ASVS Control | Status | Evidence / Gap |
|-------------|--------|---------------|
| **15.2.1** — No EOL components | Fail (Partial) | `passlib` 1.7.4 is effectively EOL (no updates since 2022). Plan to migrate within 90 days. `python-jose`: watch mode. |
| **15.2.2** — Defense against dependency loss | Partial | Private PyPI mirror: PLANNED. `requirements.txt` with hashes: PARTIAL (no `--require-hashes` enforced in CI). Gap: enforce hash checking in CI pipeline. |
| **15.2.3** — Production has only necessary components | Partial | Dev dependencies in `requirements-dev.txt` (separate from `requirements.txt`). Gap: verify no pytest/debug packages in production Docker image. |
| **15.2.4** — All transitive dependencies from trusted registries | Partial | Direct dependencies from PyPI. Transitive: not audited separately. Gap: run `pip-audit --requirement requirements.txt` for transitive scan. |
| **15.1.2** — SBOM maintained | Partial | `cyclonedx-py` generates SBOM. CI pipeline: NOT YET AUTOMATED. Gap: add SBOM generation to CI and store with each release artifact. |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Error Handler analysis (ASVS V16.5) | **25** | Correlation ID in log but not response (5 pts); separate internal/external channels (10 pts); no stack trace in response (5 pts); last-resort handler defined (5 pts) |
| Error Decisions Table (5 scenarios) | **25** | Each scenario: status code correct (1 pt), error_code prevents enumeration where needed (2 pts), log fields correct (2 pts). LOGIN failure → same error for valid/invalid user = critical |
| Logging Schema (5 categories) | **25** | "Never Log" fields include password + tokens + raw IP (not just "sensitive") (2 pts each); Security Event categorization correct (1 pt each) |
| Dependency Audit + ASVS V15.2 | **25** | `passlib` identified as stale (5 pts); CVE for `python-jose` noted (5 pts); SBOM status honest (5 pts); update strategies have concrete deadlines, not "will update later" (10 pts) |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.5.md](../solutions/sol-7.5.md)*
