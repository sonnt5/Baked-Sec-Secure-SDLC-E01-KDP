# Lab 6.2 — Measurable Security Requirements & Protection Goals

> **Chapter 6 · Security Design and Review**
> Input: Business objectives + Threat List | Output: Security Requirements Spec (MRS)

> [!NOTE]
> **Artifact for this lab:** Measurable Security Requirements Specification (MRS) — a document translating protection goals into requirements with measurable criteria. Format: Goal Area → End Goal → Metric/Threshold → Test Condition → Owner.

## Learning Objectives

- Translate business objectives into protection goals at the right abstraction level (not "need security," not "use AES-256").
- Write security requirements with specific metrics — not "the system should be secure" but "judging SLO ≥ 99.5%, p95 latency ≤ 10s under designed abuse scenarios."
- Distinguish a functional requirement ("user can login") from a security requirement ("login must be rate-limited to 5 attempts/minute/IP").
- Build traceability: Business Objective → Protection Goal → Measurable Requirement → Design Mechanism.

## Context

Security requirements must be **measurable** — if a reviewer cannot clearly say pass or fail, the requirement has no value in an SDR. "The system must be secure" is a non-requirement. "All admin actions must be logged; the audit trail must be tamper-evident; retention 90 days; sensitive fields redacted" is a testable requirement.

---

## Task 1 — Identify Business Objectives and Protection Goals

CODING WAR has 5 primary business objectives. For each objective, identify protection goals (intermediate level — specific but not yet tied to implementation):

| Business Objective | Risk Type (CIA/AAA) | Protection Goal | If Goal Not Met — Business Impact |
|-------------------|--------------------|-----------------|------------------------------------|
| **Fair and competitive judging — results must be accurate and untamperable** | Integrity | Verdicts and scores of every submission must be tamper-evident; test cases must be protected from disclosure; judge results must be non-repudiable | Contestants lose trust in the platform; legal liability if prizes are involved |
| **Participant privacy — source code and submissions are contestants' IP** | Confidentiality + Privacy | Source code submissions must only be accessed by authorized parties; logs must not contain raw submission content | Contestants unwilling to use the platform; potential IP theft claims |
| **Platform availability — contests must run on schedule** | Availability | The contest judging system must be operational during the contest window; DoS via submission floods must be mitigated | Contest organizer reputation damage; prize distribution delays |
| **Admin accountability — admin actions must be traceable** | Accountability (AAA) | \[Fill in protection goal\] | \[Fill in business impact\] |
| **Credential security — user accounts must be protected** | Authentication (AAA) | \[Fill in protection goal\] | \[Fill in business impact\] |

---

## Task 2 — Write Measurable Security Requirements (Main Artifact)

For each protection goal, write ≥1 measurable requirement using the standard format. Each requirement must have: End Goal, specific Metric/Threshold, Test Condition (pass/fail criteria), and Owner.

> [!WARNING]
> **Common mistake:** Requirement tied to implementation ("must use bcrypt") instead of outcome ("password hash must resist offline brute-force: hash time ≥ 100ms, GPU cracking impractical"). Technology choice belongs in the design decision; the requirement states the expected security property.

| ID | Goal Area | End Goal (Requirement) | Metric / Threshold | Test Condition (Pass/Fail) | Owner |
|----|----------|----------------------|-------------------|---------------------------|-------|
| **Confidentiality** | | | | | |
| **SR-C01** | Traffic Confidentiality | All client ↔ server communication must be encrypted in transit, downgrade-resistant | TLS 1.2 min, TLS 1.3 preferred; coverage = 100% endpoints; 0 HTTP endpoints | Automated TLS scan (testssl.sh); HSTS header present; HTTP redirects to HTTPS | DevOps |
| **SR-C02** | Submission Data at Rest | Source code submissions must be encrypted at rest; encryption key managed independently of data | 100% submissions encrypted (AES-256-GCM); DEK wrapped by KMS CMK; 0 plaintext in DB | Verify submissions table: `code_ciphertext` present, no plaintext `source_code` column; KMS key policy audit | Backend + DevOps |
| **SR-C03** | \[Team adds\] | | | | |
| **Integrity** | | | | | |
| **SR-I01** | Verdict Integrity | Judgment results cannot be modified after judge completes | 100% verdicts stored as immutable records; hash-chain audit log; 0 UPDATE on verdicts table after creation | Verify: verdicts table has no UPDATE trigger; hash verification test passes; audit log integrity check | Backend |
| **SR-I02** | Submission Integrity | Source code submitted cannot be altered in transit or storage | HMAC/AEAD auth tag on every submission; `InvalidTag` exception raised on tampering | Test: modify 1 byte of stored ciphertext → verify `InvalidTag` raised on decrypt attempt | Backend |
| **SR-I03** | \[Team adds\] | | | | |
| **Availability** | | | | | |
| **SR-A01** | Contest Availability | Judging service must be available during contest window even under submission flooding | SLO ≥ 99.5% during contest hours; p95 judging latency ≤ 10s; max 10 submissions/hour/user enforced | Load test: simulate 500 contestants submitting concurrently → latency and error rate within SLO; rate limit blocks at 11th submission | DevOps + Backend |
| **SR-A02** | \[Team adds\] | | | | |
| **Authentication, Authorization, Accountability & Privacy** | | | | | |
| **SR-AAA01** | Authentication Assurance | Credential stuffing attacks must be significantly slowed; account lockout must prevent brute force | Rate limit: max 5 logins/min/IP; account lockout: 5 failures/10min → 15min lock; uniform error response (prevent user enumeration) | Test: 6 requests/min → 429 returned; `test_account_lockout_after_5_failures`; `test_login_response_identical_for_valid_invalid_user` | Backend |
| **SR-AAA02** | Admin Accountability | 100% admin actions must be attributable and non-repudiable | Audit log: 100% admin API calls logged with user_id, timestamp, action, affected_object; tamper-evident (hash-chain); retention ≥ 90 days; sensitive fields redacted | Verify: every admin action creates an audit entry; test: delete audit log as admin → permission denied; hash-chain verification passes | Backend + DevOps |
| **SR-P01** | Privacy Minimization | PII must not appear raw in application logs, error messages, or unnecessary API responses | 0 PII fields in access logs raw; 0 email/name in error responses; JWT payload has ≤ 3 fields (sub, role, exp) | Log sample audit: grep for email/phone patterns in access logs → 0 matches; API response inspection: no PII in error bodies; JWT decode inspection | Backend |
| **SR-P02** | \[Team adds — data retention\] | | | | |
| **SR-AAA03** | \[Team adds — authorization scope\] | | | | |

---

## Task 3 — Traceability Matrix

Build a traceability chain from Business Objective → Protection Goal → Security Requirement → Design Mechanism (from Labs 5.2–5.3). This artifact demonstrates that "nothing is orphaned" in the security design.

| Business Objective | Protection Goal | Requirement ID | Design Mechanism (Ch.5) | Pattern Applied |
|-------------------|----------------|---------------|------------------------|----------------|
| Fair judging — verdict integrity | Tamper-evident verdicts | SR-I01 | Immutable DB record + hash-chain audit log (Lab 5.2 Audit Log Middleware) | Transparent Design + Audit Trail |
| Participant privacy | Source code confidentiality | SR-C02 | Envelope Encryption (Lab 5.6 `EnvelopeEncryptionService`) | Least Information + Defense in Depth |
| Platform availability | DoS prevention | SR-A01 | Rate limiting + resource limits per submission (Lab 5.1 Mitigation Register) | Defense in Depth + Fail Securely |
| Admin accountability | 100% admin logging | SR-AAA02 | `AuditLogMiddleware` (Lab 5.1) + append-only storage | Accept Security Responsibility |
| Credential security | Credential stuffing prevention | SR-AAA01 | Rate limiting + account lockout (Lab 5.1) | Fail Securely + Least Privilege |
| \[Business objective\] | | | | |
| \[Business objective\] | | | | |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Protection Goals (5 goals) | **20** | Goals are at the correct abstraction level: not too vague, not tied to implementation |
| Measurable Security Requirements (≥10) | **50** | Each requirement: metric/threshold with a specific number (3 pts), test condition with clear pass/fail criteria (2 pts). Non-testable requirements do not earn full marks |
| Traceability Matrix (≥7 rows) | **20** | Each row: complete chain from objective → mechanism; pattern correctly named |
| Completeness | **10** | All 5 goal areas (C/I/A/AAA/Privacy) have at least 1 requirement; no area is omitted |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-6.2.md](../solutions/sol-6.2.md)*
