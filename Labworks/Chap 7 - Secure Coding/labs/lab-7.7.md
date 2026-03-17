# Lab 7.7 — Checklist, Code Review Minutes & Security Test Matrix

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: Labs 7.1–7.6 findings | Output: Secure Code Review Checklist + Review Minutes + Test Matrix

> [!NOTE]
> **Evidence chain:** SCSP (Lab 7.6) → Checklist (Lab 7.7) → Code Review Minutes (Lab 7.7) → Test Matrix (Lab 7.7) → SAST results (Lab 7.6) → all feed into Security Testing (Ch.8) and Bug Bar/FSR (Ch.9).

## Learning Objectives

- Build a vulnerability-class checklist specific to CODING WAR Python/FastAPI.
- Write Code Review Minutes for a real PR — with CWE references, findings, and closure criteria.
- Build a Security Test Ideas Matrix from threat model → control → test idea → pass/fail criteria.

---

## Task 1 — Vulnerability-Class Secure Coding Checklist

Each checklist item must have CODING WAR-specific examples, not generic descriptions:

| Category | Pass Condition (CODING WAR) | Common Anti-patterns (Python/FastAPI) | Quick Check Method | ASVS + CWE |
|----------|-----------------------------|---------------------------------------|--------------------|-----------|
| **Input Validation** | All Pydantic schemas use strict validators; no handler accepts raw `str` for security-sensitive params; sort/filter fields use allowlist dict | `Optional[str]` for language without enum constraint; accepting arbitrary column names for ORDER BY; no `max_length` on freetext fields | `grep` for `def .*(request: Request)` without Pydantic model; check schemas for `Literal[]` on security enums; unit test boundary values | V2.2.1, CWE-20 |
| **Authentication** | JWT via `Authorization: Bearer`; tokens use ES256 explicitly; all `jwt.decode()` calls have `algorithms=['ES256']`; no HS256 with hardcoded secret | Accepting `alg='none'`; using HS256 with default secret from env; not checking `exp` claim | `grep` for `jwt.decode` without `algorithms` kwarg; unit test expired token → 401; unit test `alg=none` → 401 | V9.1, CWE-347 |
| **Authorization** | All `/submissions/{id}` endpoints have `verify_submission_owner` Depends(); all `/admin/*` have `require_admin_mfa`; no client-side role checks | Missing `Depends(verify_submission_owner)` on GET endpoints; checking role from JWT in handler directly instead of Depends; admin routes missing MFA check | `grep` for `@router.get('/submissions/{` without `Depends(verify`; unit test: contestant A accessing B's submission → 403 | V8.3.1, CWE-639 |
| **Session & Token** | Access token TTL=15min; refresh token revocation by jti; tokens not logged; `HttpOnly+Secure+SameSite=Lax` on cookies | Logging `Authorization` header; 30-day access tokens; refresh tokens without jti; session cookie without `httponly` | `grep` for `Authorization` in `log.info/debug`; check token TTL in `jwt.encode`; unit test cookie flags | V7.2, V3.3, CWE-613 |
| **Cryptography** | Passwords: Argon2id with ≥64MB memory; CSPRNG: `secrets` module only (not `random`); AES-GCM with unique nonce per encryption | `hashlib.sha256` for passwords; `random.randint()` for tokens; AES-ECB; static nonce/IV | `grep` for `hashlib.*password`; `grep` for `random\.` in security paths; `grep` for `STATIC_NONCE` or `fixed_iv` | V11.2, V11.4, CWE-327 |
| **Logging & Audit** | Logs include: timestamp, request_id, actor_public_id, event_type; NEVER include: passwords, tokens, source_code, raw IP | `log.info(f'User {email} logged in')`; logging full request body; logging `Authorization` header | `grep` for `log\.(info|debug|error).*email`; `grep` for `log.*password`; log sample: no PII in fields | V16.2.5, CWE-532 |
| **Error Handling** | Generic error responses (no stack traces, no DB details); `error_ref` in response but technical details only in internal logs; same response for user-not-found and wrong-password | Returning `exc.args` in response; different error messages for valid/invalid users; `debug=True` in production FastAPI | `test_login_same_error_for_valid_invalid_user`; `grep` for `exc_info` in response; integration test: wrong email vs wrong password → identical response body and timing | V16.5.1, CWE-209 |
| **Dependency Usage** | All dependencies pinned (no `>=` or `*`); pip-audit clean (0 High/Critical); `passlib` migration planned; no dev deps in prod Docker image | `requirements.txt` with `fastapi>=0.100`; no weekly pip-audit run; dev packages (pytest, black) in production image | `diff requirements.txt vs requirements-dev.txt`; run `pip-audit`; check Docker image: `pip show pytest` | V15.2.1, CWE-1035 |
| **Data Protection** | No `source_code` in API responses except owner view; no PII in query params; JWT minimal claims (sub, role, exp only); opaque IDs for all public resources | Returning full ORM object including `source_code`; user email in URL `?email=x@y.com`; JWT payload has phone/DOB; sequential integer IDs in URLs | `grep` for `SubmissionResponse.*source_code`; `grep` for `?email=` or `?phone=`; decode JWT: must not contain PII beyond sub+role | V14.2, V15.3.1, CWE-359 |

---

## Task 2 — Secure Code Review Minutes (PR-241)

| Field | PR-241 Code Review Minutes |
|-------|--------------------------|
| **PR ID / Link** | PR-241 (coding-war-backend / GitHub) |
| **Change Objective** | Add contest leaderboard endpoint: `GET /api/v1/contests/{contest_id}/leaderboard?sort=score&order=desc&page=1` — paginated ranking of contestants by score/penalty/time. |
| **Scope (files/modules)** | `app/api/contests.py` (new route), `app/repositories/submission_repo.py` (new query `get_leaderboard`), `app/schemas/leaderboard.py` (new response schema) |
| **Focused Risk Areas** | ① Trust boundary (query parameters sort/order/page — user input to SQL), ② Data exposure (leaderboard reveals contestant standings — competitive sensitivity), ③ Performance/DoS (unbound pagination could allow heavy query), ④ Authorization (leaderboard visibility during vs after contest) |
| **Key Finding #1** | SQL injection via `sort_field`: `submission_repo.py` line 147 uses f-string with `sort_field` in ORDER BY clause. User can inject arbitrary SQL fragment. CWE-89. |
| **Severity #1** | High — directly injectable SQL in trusted DB connection. SAST finding TR-SAST-2025-003. |
| **Requested Remediation #1** | (1) Implement `ALLOWED_SORT_FIELDS` allowlist (see Lab 7.3 IS-01 fix). (2) Use SQLAlchemy column object mapping, not string. (3) Unit test: unknown sort field returns 422, not 500 or SQL error. |
| **Key Finding #2** | Missing pagination limits: `page`/`limit` parameters have no `max_value`. Malicious user could request `limit=1000000` causing memory/CPU spike. CWE-770 (Resource Allocation Without Limits). |
| **Severity #2** | Medium — DoS risk but requires authentication. |
| **Requested Remediation #2** | Add `Field(le=100)` for limit parameter. Add rate limit on leaderboard endpoint. Add query timeout (10s max) for leaderboard queries. |
| **Key Finding #3** | Leaderboard has no freeze logic: during active contest, scoreboard should optionally freeze at last N minutes for ICPC-style contests. Missing: `freeze_at_minutes` parameter in ContestConfig. |
| **Severity #3** | Low (design gap, not vulnerability) — business logic concern for contest integrity. |
| **Status** | Open (Blocked — awaiting Fix #1 and #2) |
| **Closure Criteria** | (1) No Semgrep findings on `sqlalchemy-execute-raw-query`; (2) Unit test `test_sort_field_allowlist` passes; (3) Integration test `test_pagination_limit_enforced` passes (`limit=1000000` returns 422); (4) Reviewer re-reviews SQL query — confirms parameterized; (5) PR merged only after all items verified. |

---

## Task 3 — Security Test Ideas Matrix (Submission Pipeline)

| Threat / Abuse Case | Control Applied | Control Location | Test Type | Test Idea + Test Data | Pass/Fail Criteria |
|--------------------|----------------|-----------------|----------|----------------------|-------------------|
| Contestant submits fork-bomb to deplete judgehost resources | gVisor sandbox + resource limits (CPU, mem, pids) | `sandbox_runner.py` + gVisor config | Security test (integration) | Submit: `import os; [os.fork() for _ in range(1000)]`. Verify: judge returns TLE or MLE within timeout, no host process escape. | Pass: verdict TLE/MLE within 5s; host process count unaffected; no zombie processes on host. |
| DoS via large source code upload | Pydantic `max_length` validation (64KB limit) | `app/schemas/submission.py` `SubmissionCreate` | Unit + Integration | Submit code with 65,000 bytes (1 byte over limit) and with exactly 64,000 bytes. Also test: code with 10MB body. | Pass: 65KB → 422 Validation Error; 64KB → 201 Created; 10MB → 413 Content Too Large (nginx body limit). |
| IDOR: Contestant reads other's submission | `verify_submission_owner` Depends() | `app/api/submissions.py` | Integration (IDOR) | User A creates submission, gets `sub_public_id`. User B (different JWT) tries `GET /submissions/{sub_public_id}`. Also: admin role should succeed. | Pass: User B → 403; Admin → 200; User A → 200. Same behavior for any invalid ownership. |
| Command injection via source code path manipulation | subprocess list API (`shell=False`) | `app/services/judge_service.py` | Security test | Attempt to submit code where filename contains shell metacharacters: `; rm -rf /` or `&& cat /etc/passwd`. | Pass: filename sanitized before subprocess call; OS command not executed; submission processed normally or rejected cleanly. |
| Credential stuffing on login endpoint | IP rate limit + account lockout (planned) | `app/middleware/rate_limit.py` + auth service | Integration + Load | Send 6 login attempts in 1 minute from same IP (should trigger rate limit). Send 5 failed logins for same email (should trigger lockout when implemented). | Pass: 6th request → 429 with Retry-After header; IP rate limit logs show threshold hit. (Account lockout: currently fail — see SEC-EX-2025-001) |
| Test case side-channel via execution timing | Uniform execution time response (not yet implemented) | `judge_service.py` result reporting | Security test (timing) | Submit code that executes with different timing on different test inputs (O(n) vs O(n²)). Measure if timing info in response differs by test case. | Pass: verdict response time does not reveal relative difficulty of passed/failed test cases. Ideally: all responses within ±100ms of each other after verdict. |
| SQL injection via sort field (PR-241 finding) | ORDER BY allowlist (`ALLOWED_SORT_FIELDS`) | `submission_repo.py` | Unit + Security test | `sort='score'` → 200; `sort='unknown_field'` → 422; `sort="'; DROP TABLE submissions; --"` → 422; `sort="1 UNION SELECT * FROM users"` → 422. | Pass: only allowlisted fields return 200; any non-allowlisted → 422 (not 500, not executed SQL). |
| \[Team adds test from vulnerability chains VC-01 or VC-02\] | | | | | |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Vulnerability-Class Checklist (9 categories) | **35** | Each category: pass condition has CODING WAR-specific example (2 pts), anti-pattern cites actual code pattern (2 pts), quick check is a grep/test command (1 pt). Generic descriptions do not earn full marks |
| Code Review Minutes — PR-241 | **30** | 3 findings with CWE references (5 pts each); closure criteria are testable and specific (5 pts each); risk areas focus on right things (boundary crossing, blast radius) |
| Security Test Matrix (7+ tests) | **35** | Each test: test data is specific (3 pts), pass/fail criteria are observable (4 pts), control location named (1 pt). "Verify security" is not a pass criteria — need a quantitative, observable condition |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.7.md](../solutions/sol-7.7.md)*
