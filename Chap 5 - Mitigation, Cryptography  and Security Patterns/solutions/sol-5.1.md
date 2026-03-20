# Solution 5.1 — Mitigation Planning: Reduce · Resist · Recover

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — Reduce · Resist · Recover Classification

| # | Mitigation / Control | Primary Lever | Secondary Lever | Explanation |
|---|---------------------|-------------|----------------|-------------|
| 1 | Rate limiting 10 req/min/IP at API Gateway for /auth/login | **Reduce** | Recover (feeds alert threshold) | Makes brute force economically infeasible — attacker can't automate at scale |
| 2 | JWT access token TTL = 15 minutes | **Reduce** | Resist | Shrinks the window of vulnerability for stolen tokens — limits blast radius |
| 3 | Object-level authorization: check `submission.user_id == jwt.sub` | **Resist** | — | Does not prevent the attack attempt but ensures it fails — direct impact reduction |
| 4 | Append-only audit log with hash-chain for admin actions | **Recover** | Reduce (accountability deters attackers) | Enables forensic reconstruction; hash-chain prevents log tampering |
| 5 | gVisor sandbox with separate network namespace for judge | **Resist** | Reduce (harder to exploit) | Limits damage when malicious code runs — containment, not prevention |
| 6 | Monitoring + alerting: >50 failed logins/5 min from same IP | **Recover** | Reduce (triggers lockout or CAPTCHA) | Detection and response trigger — alone doesn't prevent but enables rapid response |
| 7 | Encrypt submission source code at rest with AES-256-GCM + KMS | **Resist** | — | Limits impact of DB breach — attacker gets ciphertext, not plaintext source code |
| 8 | Mandatory MFA for admins before sensitive operation | **Reduce** | — | Makes credential compromise insufficient — attacker needs a second factor |
| 9 | Generic error messages: only return `error_code`, no stack traces | **Resist** | — | Limits information available to an attacker who has triggered errors |
| 10 | Daily database backup + quarterly tested restore drill | **Recover** | — | Pure recovery control — does nothing to prevent or contain the attack |
| 11 | Input schema validation at API layer using Pydantic | **Reduce** | Resist | Reject malformed inputs before they reach business logic — reduces exploitable attack surface |
| 12 | Incident response runbook: 30-minute SLA to isolate compromised account | **Recover** | — | Defines the response process — does not reduce probability or initial impact |

---

## Task 2 — Mitigation Register (Reference Entries)

### Entry 1: TH-01 / MC-01 — Credential Stuffing on /auth/login

| Field | Content |
|-------|---------|
| **① Target Threat & Risk** | TH-01 — Spoofing — Credential Stuffing on POST /api/v1/auth/login — Risk: Critical (L=4, I=4, Score=16) |
| **② Asset / Boundary / Flow** | Asset: User Credentials Tier 2 (Asset 1.1) at Trust Boundary B1 (Internet → Web Tier), Entry Point EP-1.1 |
| **③ Mechanism (Lever: Reduce + Recover)** | Rate Limiting (Reduce): max 10 req/min/IP via sliding window in Redis. Account Lockout (Reduce): 5 failures/10min → 15min exponential lock. CAPTCHA (Reduce): triggered after 3 failures. Monitoring (Recover): alert when >50 failures/5min from same IP. |
| **④ Injection Point** | `app/middleware/rate_limit.py` (FastAPI `@limiter.limit('10/minute')`) + `app/services/auth_service.py::check_lockout()` + Redis counter `login_failures:{ip}` with TTL |
| **⑤ Evidence** | `tests/security/test_rate_limiting.py::test_login_rate_limit_returns_429_after_10_requests_per_minute`; `tests/security/test_account_lockout.py::test_account_locked_after_5_failures`; Prometheus alert rule: `login_failures_total > 50 in 5m` |
| **⑥ Residual Risk & Assumptions** | Medium — distributed botnet can bypass IP-based rate limit (each IP sends <10 req/min). Assumption: CAPTCHA will be implemented before beta; MFA will be added for admin accounts in Sprint 2. Monitoring provides detection even if rate limit is bypassed. |

### Entry 2: TH-02 / MC-03 — IDOR on /submissions/{id}

| Field | Content |
|-------|---------|
| **① Target Threat & Risk** | TH-02 — Elevation of Privilege (BOLA/IDOR) — Unauthorized access to other contestants' submissions — Risk: High (L=4, I=3, Score=12) |
| **② Asset / Boundary / Flow** | Asset: Source Code Submissions Tier 3 (Asset 2) at Trust Boundary B2 (Web → Service), Entry Point EP-1.7 (`GET /submissions/{id}`) |
| **③ Mechanism (Lever: Resist)** | Object-level Authorization (Resist): `assert submission.user_id == current_user.id` before any data returned. Admin access via separate endpoint with audit log. Rate limit on endpoint to slow enumeration. |
| **④ Injection Point** | `app/api/submissions.py::get_submission()` — `Depends(verify_submission_ownership)` injected before DB query. `app/core/authorization.py::verify_submission_ownership()` — raises 403 if IDs don't match. |
| **⑤ Evidence** | `tests/security/test_authorization.py::test_contestant_cannot_access_other_submission_returns_403`; `tests/security/test_authorization.py::test_admin_can_access_any_submission_with_audit_log` |
| **⑥ Residual Risk & Assumptions** | Low — after implementing ownership check, IDOR is effectively eliminated for this endpoint. Residual: authorization logic must be replicated correctly on any future submission-related endpoints. Assumption: code review checklist updated to require ownership check audit on all new resource endpoints. |

### Entry 3: TH-03 — DoS / RCE via Submissions

| Field | Content |
|-------|---------|
| **① Target Threat & Risk** | TH-03 — Denial of Service + Elevation of Privilege (RCE) — Malicious submission code causes resource exhaustion or sandbox escape — Risk: Critical (L=4, I=4, Score=16) |
| **② Asset / Boundary / Flow** | Asset: Judge Server Integrity, Internal Network (Asset 10 — Sandbox Config) at Trust Boundary B4 (App → Judge), Entry Point EP-1.4 → EP-2 |
| **③ Mechanism (Lever: Resist + Reduce)** | Sandbox (Resist): gVisor (`runsc`) with seccomp profile blocking all non-essential syscalls. Network Isolation (Resist): judge container has no internet access — outbound network blocked. Resource Limits (Resist): CPU=1 core, memory=256MB, wall time=30s, SIGKILL on exceed. Rate Limit (Reduce): 30 submissions/hour/user. |
| **④ Injection Point** | Docker Compose / Kubernetes: `runtime: runsc` + `network_mode: none` for judge containers. `app/judge/runner.py::execute_with_limits()` — enforces CPU/memory via subprocess timeout + Docker flags. `app/api/submissions.py` — `@limiter.limit('30/hour')` |
| **⑤ Evidence** | `tests/judge/test_sandbox.py::test_outbound_network_blocked_from_sandbox`; `tests/judge/test_resource_limits.py::test_infinite_loop_killed_within_30s`; `tests/judge/test_sandbox.py::test_file_system_access_outside_tmp_denied` |
| **⑥ Residual Risk & Assumptions** | Medium — gVisor isolation significantly reduces RCE risk but is not 100% foolproof (kernel vulnerabilities in gVisor itself). Assumption: gVisor version updated monthly; CVE monitoring via automated SCA scan on judge Docker image. DoS residual: per-user rate limit mitigates most cases; a single user with many accounts could still cause load. |

---

## Task 3 — Risk Treatment Strategy (Additional Threats)

| Threat ID | Risk Level | Strategy | Justification | Review Trigger |
|-----------|-----------|----------|--------------|----------------|
| **TH-04** | Medium | Mitigate | Low effort (1 day), reduces information leakage in all future incidents — good investment | When adding new API endpoints or changing error handling library |
| **TH-05** | High | Mitigate | Audit trail is required for compliance and incident response — cannot be deferred | When adding new admin capabilities |
| **TH-06** | High | Mitigate | JWT algorithm validation is a 30-minute fix — risk of full auth bypass is too high to Accept | When changing JWT library or auth flow |
| **TH-07** | Medium | Accept | UUID-based MinIO keys + internal-only access already make exploitation very unlikely. Risk score = 4 (Low). Monitoring in place. | When MinIO is exposed to new internal services |
| **TH-08** | Medium | Mitigate | Rate limiting + pagination is a low-effort control; reduces scraping and enumeration risk | When changing scoreboard visibility settings |
| **TH-09** | High | Mitigate | Registration flood can pollute DB and enable future abuse. CAPTCHA + IP rate limit is 1-day effort. | When registration traffic anomaly detected |
| **TH-10** | Medium | Mitigate | CSP header is a 2-hour config change; reduces XSS risk significantly | When adding new third-party scripts |

---

*Back to the lab: [labs/lab-5.1.md](../labs/lab-5.1.md)*
