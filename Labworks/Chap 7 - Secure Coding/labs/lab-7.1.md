# Lab 7.1 — Design Invariants → Code Contracts

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: Architecture + SDR Ch.3–6 | Output: Code Contract Document + Invariant Map

> [!NOTE]
> **OWASP ASVS v5.0.0:** ASVS V15.1.1 — *"Verify that application documentation defines risk-based remediation time targets for different vulnerability severities."* V2.1.1 — *"Verify that all input validation requirements are documented, enforced at a trusted service layer, and cannot be bypassed."* Core concept: design assumptions must become code invariants — otherwise the SDR is security theater.

## Learning Objectives

- Translate design assumptions (from SDR Ch.6) into specific code invariants.
- Understand and apply the 3 axes: Data Flow & Untrusted Input, Assets & Risk, Design Invariants → Code Contracts.
- Analyze vulnerability chains — why "small bugs" combine into major incidents.
- Build the Code Contract Document as the baseline for code reviews in Labs 7.2–7.7.

---

## Task 1 — The 3 Axes of Secure Coding: Analysis for CODING WAR

For each of the 3 coding axes, identify concrete examples in CODING WAR:

| Axis | Definition (applied to CODING WAR) | Examples + Implication |
|------|------------------------------------|----------------------|
| **① Data Flows & Untrusted Input** | Every input crossing a trust boundary is untrusted — including from message queue, webhook, and database read-back. Tainted data must be tracked from Source → Sink. | Sources: `POST /submissions` (source_code), `GET /submissions?sort=`, webhook callbacks, RabbitMQ messages from external judge. Dangerous sinks: SQL queries, `os.exec()`, template rendering, regex engine, subprocess. Implication: contestant `source_code` is tainted — never execute directly, never log raw, never echo in response without sanitization. |
| **② Assets & Risk** | A bug near a high-value asset (HVA) is a security vulnerability. The same bug near unimportant code is not. | CODING WAR HVAs: test cases, JWT signing key, verdict records, user credentials. Risk implication: integer overflow near verdict scoring = Critical. Same overflow in UI pagination = Low. Test: during code review, always ask "does this variable affect any HVA?" |
| **③ Design Invariants → Code Contracts** | Design assumptions must become code invariants — conditions that code always maintains, regardless of how the caller behaves. | Design assumption: "All DB access goes through the repository layer" → Code invariant: handler files have no `db.execute()` directly. Design assumption: "MFA required for admin actions" → Code invariant: `@require_recent_mfa` decorator on every `/admin` endpoint. Violation detection: SAST rule + code review checklist + unit test. |

---

## Task 2 — Code Contract Document (Main Artifact)

Translate design assumptions from the SDR (Ch.6 Lab 6.7) into code invariants. Each entry must have: (a) design assumption, (b) code invariant, (c) enforcement location, (d) violation detection method.

> [!WARNING]
> A design assumption is not a code invariant until it has a specific enforcement location and a violation detection method. *"Should use parameterized queries"* is an assumption. *"repo/submission_repo.py: all queries use SQLAlchemy ORM; SAST rule bans db.execute() with string concat; unit test verifies no raw SQL"* is an invariant.

| ID | Design Assumption (from SDR Ch.6) | Code Invariant (what code must always maintain) | Enforcement Location | Violation Detection | Priority / ASVS |
|----|-----------------------------------|-------------------------------------------------|---------------------|--------------------|--------------------|
| **CI-01** | All DB access must go through the repository/service layer (no direct db access in controllers/handlers) | No handler module imports db_session directly; all queries go through `*Repository` classes; no `db.execute()` with string concatenation anywhere | `app/api/*.py`: imports only repository classes. `app/repositories/*.py`: only place with `db.execute()`. | SAST rule: detect `db.execute()` outside repositories. Code review checklist item #1. Unit test: verify no direct SQL in handler files. | Critical / ASVS V1.2.4 |
| **CI-02** | All user input must be validated at the trust boundary before entering business logic | Pydantic models validate ALL input at API layer; no handler function accepts raw `str` for security-sensitive parameters; allowlists for language, sort fields | `app/schemas/*.py`: Pydantic models with strict validators. `app/api/*.py`: all handlers use typed Pydantic schemas, no raw `request.body()` parsing. | SAST rule: detect untyped request body parsing. Unit tests: boundary cases for each schema. ASVS V2.2.1 verification. | Critical / ASVS V2.2 |
| **CI-03** | MFA required for all admin actions (high-risk operations) | Every `/admin/*` endpoint has `@require_admin_mfa` dependency; no admin operation bypasses MFA check even if admin is JWT-authenticated | `app/api/admin/*.py`: `@require_admin_mfa` on every router function. No admin operation without decorator. | Code review: grep for `@router.post/get` in admin modules missing `@require_admin_mfa`. Unit test: admin endpoint without MFA → 401. | Critical / ASVS V6.5 |
| **CI-04** | Judge only executes code in a sandboxed environment — never directly on host | `JudgeService.run_code()` always calls `sandbox_runner.execute()` — never `os.subprocess`, `os.system`, `exec()` directly. Sandbox is never bypassed. | `app/services/judge_service.py`: only method that executes code. `sandbox_runner.py`: only place with subprocess calls. Strict import control. | SAST rule: detect subprocess/os.system outside sandbox_runner.py. Integration test: attempt code execution outside sandbox path. | Critical / ASVS V15.3 |
| **CI-05** | Verdict records are append-only — no update or delete after creation | `VerdictRepository` has `create()` only — no `update()` or `delete()` methods. DB: verdict table has no UPDATE privilege for app user. | `app/repositories/verdict_repo.py`: only insert operations. DB migration: revoke UPDATE on verdicts from app_user role. | Unit test: attempt to update verdict via VerdictRepository → AttributeError. DB audit: verify no UPDATEs on verdicts table. | High / ASVS V15.3 |
| **CI-06** | No PII or secrets in application logs | `LoggingMiddleware` redacts: password, token, source_code fields from all log entries. Logger never called with raw sensitive objects. | `app/middleware/logging_middleware.py`: REDACT_FIELDS list applied before any `log.info()`/`log.error()` call. | SAST rule: detect `logging.info/debug` called with Submission objects directly. Unit test: log sample audit — grep for password/token patterns. | High / ASVS V16.2.5 |
| **CI-07** | Source code is never echoed raw in error responses or API responses | `ErrorHandler` never includes `submission.source_code` in error body. API response schemas use projection (no `source_code` in public responses except owner view). | `app/core/error_handlers.py`: `StandardErrorResponse` with fixed fields only. `app/schemas/submission.py`: `SubmissionPublicResponse` excludes source_code. | Integration test: trigger error on submission endpoint → verify source_code not in response body. ASVS V13.4 compliance. | Medium / ASVS V13.4 |
| **CI-08** | \[Team adds from SDR Issue Log Ch.6\] | | | | |

---

## Task 3 — Vulnerability Chain Analysis

Vulnerability chains occur when multiple "small bugs" combine into a dangerous attack path.

### VC-01: Verbose Error → User Enumeration → Credential Stuffing

| Step | Bug | Severity (isolated) | Asset | Chain with next? |
|------|-----|--------------------|----|-----------------|
| 1 | POST /auth/login returns "User with email X not found" (different from "Invalid password" for existing user) | Low (info disclosure) | User existence info | → Enables step 2 |
| 2 | Attacker enumerates valid emails by brute-forcing email patterns and distinguishing two error messages | Medium (reconnaissance) | Valid email list | → Enables step 3 |
| 3 | No account lockout — rate limit is IP-only (bypassed with distributed botnet) | Medium (missing control) | Account lockout | → Enables step 4 |
| 4 | **Combined:** valid email list + password from breach databases + no lockout → credential stuffing | **Critical** (account takeover) | User accounts, submissions, test cases | ⚠️ Final impact |

**Fix:** CI-01 equivalent for login (uniform error message — same response for valid/invalid email, same response time). CI-03 equivalent for login (account lockout after 5 failures/10min). ASVS: V16.5.1, V6.3.3.

### VC-02: IDOR → Submission Read → Verdict Tampering → Contest Integrity Failure

| Step | Bug | Severity (isolated) | Asset | Chain with next? |
|------|-----|--------------------|----|-----------------|
| 1 | `GET /api/v1/submissions/{id}` missing object-level ownership check (CI-01 violated) | High (IDOR) | Other contestants' submissions | → Enables step 2 |
| 2 | Attacker reads submissions of leading contestant — learns their approach | High (IP theft) | Contestant IP / strategy | → Enables step 3 |
| 3 | Verdict records not hash-chained — can be altered after judging if DB user has UPDATE privilege (CI-05 violated) | Critical (tampering) | Contest integrity | → Enables step 4 |
| 4 | **Combined:** read others' solutions + admin account without MFA (CI-03) → manipulate final scoreboard | **Critical** (contest integrity failure) | Contest results, prize validity | ⚠️ Final impact |

**Fix:** CI-01 enforcement (ownership check via `Depends()`). CI-05 enforcement (append-only verdict table). CI-03 enforcement (MFA for admin). ASVS: V8.3.1, V2.1, V15.4.

### VC-03: \[Team constructs\]

Identify a new vulnerability chain in CODING WAR — minimum 3 steps, ending with impact ≥ High. Analyze in the format above.

---

## Discussion Questions

1. Invariant CI-04 (judge sandbox) — why is this a "code invariant" that matters more than just a "test case"? If there is no specific enforcement location, does the invariant have value?

2. Vulnerability Chain VC-02 starts with IDOR (High) but ends at Critical. Why is the chain's final severity higher than any individual bug?

3. Design assumption "MFA required for admin" exists in the SDR from Ch.6. If a new developer joins and doesn't know this assumption, they might accidentally violate CI-03. How does the Code Contract Document help in this scenario?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| 3 Axes Analysis for CODING WAR | **15** | Each axis: specific examples from CODING WAR (not generic), implication is actionable |
| Code Contract Document (7+ invariants) | **45** | Each invariant: enforcement location has specific file/path (3 pts), violation detection method is actionable (2 pts). "Should use X" is not a code invariant |
| Vulnerability Chain Analysis (2 + 1 team) | **30** | Each chain: ≥3 steps, isolated vs chained severity clearly distinguished, fix linked to specific CI code contract |
| Discussion questions | **10** | Answers demonstrate understanding of enforcement vs documentation distinction |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.1.md](../solutions/sol-7.1.md)*
