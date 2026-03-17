# Lab 7.6 — Secure Coding Standard Profile & SAST/SCA Triage

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: Ch.5–7 artifacts | Output: Secure Coding Standard Profile + SAST/SCA Records

> [!NOTE]
> **OWASP ASVS v5.0.0:** V15.1.1 — *"Verify that application documentation defines risk-based remediation time targets for different vulnerability severities."* V15.1.3 — *"Verify that documentation identifies functionality which is security-sensitive and requires heightened review scrutiny."*

## Learning Objectives

- Write a Secure Coding Standard Profile (SCSP) for CODING WAR FastAPI/Python.
- Complete a SAST Triage Record for a SQL injection finding from Semgrep.
- Complete an SCA Triage Record for a CVE finding in `python-jose`.
- Write a Security Exception for a finding that cannot be fixed in the current sprint.

---

## Task 1 — Secure Coding Standard Profile (SCSP)

Review the custom Semgrep rules in [`code/semgrep-rules/coding-war-custom.yaml`](../code/semgrep-rules/coding-war-custom.yaml). Then complete the SCSP document:

| Field | CODING WAR — Value |
|-------|-------------------|
| **Profile ID** | SCSP-CODING-WAR-001 |
| **Project Name** | CODING WAR — Competitive Programming Platform |
| **App Type** | Backend API (REST/JSON), microservice architecture, async FastAPI |
| **Environment** | Internet-facing (contestant/public API) + Internal (judge service, admin console) |
| **Risk Level** | High — competitive integrity (test cases = HVA), user data (PII), admin operations (critical), judge execution (RCE potential) |
| **Language Stack** | Python 3.11+, FastAPI, SQLAlchemy (async), PostgreSQL, Redis, RabbitMQ, Docker/gVisor |
| **Reference Standards** | ① OWASP Secure Coding Practices Quick Reference Guide ② OWASP ASVS v5.0.0 — Level 2 target (Level 3 for auth + crypto + judge sandbox) ③ NIST SSDF (SP 800-218) — PS.1, PW.1, PW.4, PW.8 ④ CWE Top 25 — vulnerability classification for SAST triage ⑤ Python-specific: Bandit SAST rules + pip-audit SCA |
| **Scope** | All Python source code in `app/` directory + security-related runtime config (nginx, Docker, K8s manifests). Excludes: test code in `tests/` (reviewed separately). Migration scripts: included for SQL injection review. |
| **Security-Sensitive Modules (ASVS V15.1.3)** | ① `app/core/security.py` — JWT, MFA, auth logic ② `app/repositories/*.py` — all DB queries (injection sink) ③ `app/services/judge_service.py` + `sandbox_runner.py` — RCE risk ④ `app/core/crypto.py` — encryption/hashing ⑤ `app/middleware/idempotency.py` + `rate_limit.py` — DoS controls ⑥ `app/api/admin/*.py` — privileged operations |
| **Mandatory Rules (Zero tolerance)** | ① No string concatenation in SQL queries — use SQLAlchemy ORM only ② No `shell=True` in subprocess calls ③ No hardcoded secrets, API keys, passwords in source code ④ No logging of passwords, tokens, PII ⑤ No `eval()` or `exec()` outside `sandbox_runner.py` ⑥ All `/admin` endpoints must have `@require_admin_mfa` decorator |
| **Exclusions with Rationale** | ① MISRA/CERT C — N/A (Python, not C). ② ASVS Level 3 for low-risk endpoints (GET /problems, GET /contests) — accepted risk given public read-only nature. Documented: SCSP-EXCL-001. ③ SameSite=Strict for all cookies — excluded for login flow UX reasons; SameSite=Lax acceptable per CSRF threat model. Documented: SCSP-EXCL-002. |
| **Enforcement Tools** | ① Semgrep — custom rules (`code/semgrep-rules/coding-war-custom.yaml`) + `p/python` + OWASP rules. Run in CI on every PR. ② Bandit — secondary SAST for Python-specific issues. ③ pip-audit — every dependency update + weekly scheduled scan. ④ detect-secrets — pre-commit hooks for hardcoded secrets. |
| **Remediation SLA (ASVS V15.1.1)** | Critical: fix before merge (blocking). High: fix within 7 days or before next release. Medium: fix within 30 days. Low: next sprint (tracked in backlog). |
| **Proposer** | Security Champion (Backend Lead) |
| **Approver** | AppSec Lead + Tech Lead |
| **Review Cycle** | Every major release OR 6 months (whichever sooner); mandatory review after any Critical/High CVE in dependencies |

---

## Task 2 — SAST Triage Record (Semgrep SQL Injection finding)

Run (or simulate) the custom Semgrep rules:
```bash
pip install semgrep --break-system-packages
semgrep scan \
  --config code/semgrep-rules/coding-war-custom.yaml \
  --json -o semgrep-results.json \
  app/
```

Complete the SAST Triage Record for finding `TR-SAST-2025-003`:

| Field | Value |
|-------|-------|
| **Record ID** | TR-SAST-2025-003 |
| **Type** | SAST |
| **Tool** | Semgrep v1.65 |
| **Rule ID** | `python.sqlalchemy.security.sqlalchemy-execute-raw-query` |
| **Location** | `app/repositories/submission_repo.py:147` |
| **Commit / PR** | `abc1234` / PR-241 (Add contest leaderboard endpoint) |
| **Finding Description** | `db.execute()` called with f-string containing `sort_field` variable from user request. `sort_field` comes from GET query parameter with no allowlist validation. |
| **Triage Conclusion** | \[True Positive / False Positive / Acceptable Risk — with reasoning\] |
| **Severity** | \[Fill in: CWE, impact, exploitability\] |
| **Impact** | \[Fill in\] |
| **Proposed Fix** | \[Fill in: reference IS-01 fix from Lab 7.3\] |
| **Evidence** | \[Fill in: test case IDs, SAST re-run result\] |
| **Processing SLA** | 7 days (High severity per SCSP-CODING-WAR-001) |
| **Status** | Open (In Progress) |
| **Closure Criteria** | \[Fill in: must include SAST re-run showing zero findings\] |

---

## Task 3 — SCA Triage Record (python-jose CVE)

Run (or simulate) the SCA scan:
```bash
pip install pip-audit --break-system-packages
pip-audit --requirement requirements.txt --format json -o sca-results.json
```

Complete the SCA Triage Record for `TR-SCA-2025-007`:

| Field | Value |
|-------|-------|
| **Record ID** | TR-SCA-2025-007 |
| **Type** | SCA |
| **Tool** | pip-audit v2.7.2 |
| **Library, version** | `python-jose[cryptography]` 3.3.0 |
| **CVE** | CVE-2024-33663 — Algorithm confusion attack: `python-jose` allows 'none' algorithm JWT if not explicitly rejected in verify step |
| **Location** | `requirements.txt:8` |
| **Finding Description** | `python-jose` 3.3.0 is vulnerable to algorithm confusion. If verification code does not explicitly specify `algorithms=['ES256']`, a crafted JWT with `alg='none'` may be accepted. Impact depends on how `jose.jwt.decode()` is called. |
| **Triage Conclusion** | \[True Positive (potentially) — explain why code review is required to confirm\] |
| **Severity** | \[Fill in: High pending code review, or Critical if confirmed\] |
| **Impact Scope** | `app/core/security.py` uses `python-jose` for JWT verification |
| **Investigation Result** | \[Code review of `app/core/security.py`: verify every `jwt.decode()` call has explicit `algorithms=['ES256']`\] |
| **Proposed Fix** | \[Fill in: Option 1: Update to `joserfc`. Option 2: Audit all decode() calls. Option 3: Add static analysis rule.\] |
| **Upgrade Plan** | \[Fill in: target library, timeline, rollout strategy\] |
| **Processing SLA** | 7 days (High per SCSP) |
| **Status** | Open — Code review in progress |

---

## Task 4 — Security Exception Record

Complete the Security Exception for account lockout (Lab 7.1 CI-02, vulnerability chain VC-01) which cannot be implemented in the current sprint because the shared rate-limit infrastructure needs redesign:

| Field | Value |
|-------|-------|
| **Exception ID** | SEC-EX-2025-001 |
| **Scope** | POST /api/v1/auth/login — missing per-email account lockout |
| **Control/Requirement** | Code Contract CI-02 (ASVS V6.3.3): "Account lockout after 5 failed login attempts/10 minutes per email." |
| **Risk Assessment** | \[Fill in: likelihood, impact, overall risk level\] |
| **Reason for Not Fixing** | Per-email lockout requires Redis distributed counter + per-account state. Current Redis cluster config is single-node (no replication). Full fix requires Redis cluster + per-email state migration — 2 sprint effort, depends on DevOps sprint. |
| **Acceptance Conditions** | Exception valid ONLY IF: (1) IP rate limiting (10/min/IP) remains in place, (2) CAPTCHA challenge after 3 failures from same IP, (3) Alert monitoring active for >5 unique IPs targeting same email within 10min. |
| **Compensating Controls** | \[Fill in: list specific, verifiable controls\] |
| **Final Remediation Plan** | \[Fill in: Sprint X: Redis cluster. Sprint Y: implement per-email lockout with test evidence.\] |
| **Expiration Date** | \[Fill in: specific date — must be bounded\] |
| **Proposer / Approver** | Security Champion / AppSec Lead + Engineering Manager |
| **Status** | Proposed — Pending Approval |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| SCSP Document | **30** | Security-sensitive modules listed (ASVS V15.1.3) (10 pts); mandatory rules actionable (5 pts); remediation SLA references ASVS (5 pts); exclusions have justification (10 pts) |
| SAST Triage Record | **25** | Triage conclusion is True Positive with reasoning (5 pts); proposed fix addresses root cause not symptom (10 pts); closure criteria include SAST re-run (10 pts) |
| SCA Triage Record | **25** | CVE impact correctly assessed as conditional pending code review (5 pts); upgrade plan has timeline + rollout strategy (10 pts); "code review required to confirm" = correct approach (10 pts) |
| Security Exception Record | **20** | Compensating controls are specific and verifiable (5 pts); expiration date present (5 pts); acceptance conditions bound the exception (10 pts) |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.6.md](../solutions/sol-7.6.md)*
