# Lab 6.5 — Privacy by Design & Trade-off Management

> **Chapter 6 · Security Design and Review**
> Input: MRS Lab 6.2 + Data Design 6.4 | Output: Privacy Design Controls Checklist + Trade-off Decision Log

> [!NOTE]
> **Artifacts for this lab:** (1) Privacy Design Controls Checklist — mapping privacy policy to design controls. (2) Trade-off Decision Log — recording decisions when security, usability, performance, and cost conflict. (3) Design Simplicity Assessment — evaluating architecture complexity and proposing simplifications.

## Learning Objectives

- Translate privacy policy into concrete design controls following the chain: Policy → Requirements → Design Controls.
- Identify and document trade-offs when security conflicts with usability/performance/cost — not always choosing "most secure."
- Evaluate Design Simplicity — complexity is the enemy of security because it obscures vulnerabilities.
- Understand why accepted risks must be explicitly documented, not left implicit.

---

## Task 1 — Privacy Policy → Design Controls Chain

Map each privacy policy directive to concrete design controls and implementation locations:

| # | Privacy Policy Directive | → Design Requirement | → Design Control (mechanism) | Implementation Location | Evidence |
|---|--------------------------|---------------------|------------------------------|------------------------|----------|
| **1** | **Purpose Limitation:** data may only be used for the purpose it was collected (registration → login and communication only) | Email must not be used for analytics, marketing, or third-party sharing | Token Vault: inter-service calls use `user_public_id`, not email; email only in Auth Service DB | Auth Service DB isolation; inter-service API contracts verify no email field | API response inspection: email not present in /submissions, /contests, /scoreboard responses |
| **2** | **Data Minimization:** only collect data truly needed | Registration form only requires: username, email, password — no phone, DOB, full_name required | Pydantic `UserRegister` schema: only 3 fields; extra fields rejected (`model_config forbid extra`) | `app/schemas/user.py` | Schema test: POST with extra fields returns 422 |
| **3** | **Retention Limitation:** each data class has a defined TTL, deleted when expired | Inactive accounts (>2 years no login) must be anonymized or deleted; submissions retained 2 years then purged | Scheduled deletion job with tombstone records; GDPR erasure flow; crypto-shred for encrypted data | Celery scheduled task; DB migration for anonymization schema | Deletion job test; verify: after job runs, no PII accessible for anonymized accounts |
| **4** | **Sharing Approval:** outbound data flows must have controlled mechanisms | User data cannot be exported to any third party without explicit authorization + audit log | Admin export requires 2-person approval; export logs every field accessed; no bulk PII export without approval workflow | Admin API + Separation of Privilege gate | Export test: single admin cannot trigger bulk export without second approval |
| **5** | **Access Scoping:** different roles see different data | Contestants see own data only; Admins see all with audit; Public sees aggregated/anonymized only | Role-based response projection: `PublicProfile` (no PII), `OwnProfile` (email visible), `AdminView` (all fields + audit log on access) | Pydantic response schemas per role; `response_model` varies by `user.role` | IDOR test + role-based response test |
| **6** | \[Team adds from privacy policy\] | | | | |

---

## Task 2 — Trade-off Decision Log

When security conflicts with usability/performance/cost, the team must make an explicit decision and document it.

> [!NOTE]
> **Reminder:** An accepted risk is not bad design — it is honest design. The problem is when risk is accepted but not documented. Six months later, no one remembers why the decision was made, and a new developer may "fix" it in a way that creates a new vulnerability.

### SR-D01: JWT Access Token Expiry — Security vs UX

Security wants 5-minute expiry (minimize stolen token window). UX wants 24-hour expiry (users don't re-login frequently). Performance wants longer expiry (reduce token refresh requests).

| Field | Content |
|-------|---------|
| **Options considered** | |
| **Decision** | |
| **Rationale** | |
| **Residual Risk** | |
| **Monitoring Plan** | |
| **Review Trigger** | |

### SR-D02: Source Code Storage — Encrypt Everything vs Selective Encryption

Security wants to encrypt all submissions (100% coverage). Engineering estimate: Envelope Encryption adds ~50ms/submission + KMS cost $0.03/10k API calls. Contest with 50k submissions = $150/contest + latency impact.

| Field | Content |
|-------|---------|
| **Options considered** | |
| **Decision** | |
| **Rationale** | |
| **Residual Risk** | |
| **Monitoring Plan** | |
| **Review Trigger** | |

### SR-D03: Admin 2-Person Approval — Security vs Operational Speed

Security wants 2-person approval for ALL admin operations. Operations wants single-admin for speed during contests (if co-admin unavailable, operations blocked). Legal/compliance has no requirement.

| Field | Content |
|-------|---------|
| **Options considered** | |
| **Decision** | |
| **Rationale** | |
| **Residual Risk** | |
| **Monitoring Plan** | |
| **Review Trigger** | |

### SR-D04: Rate Limiting Aggressiveness — DoS Prevention vs Legitimate Usage

Security wants max 5 submissions/hour (strict DoS prevention). Competitive programmers during training may legitimately submit 20+ times/hour. Current rate: 10/hour.

| Field | Content |
|-------|---------|
| **Options considered** | |
| **Decision** | |
| **Rationale** | |
| **Residual Risk** | |
| **Monitoring Plan** | |
| **Review Trigger** | |

### SR-D05: \[Team identifies a trade-off in CODING WAR\]

\[Fill in scenario\]

| Field | Content |
|-------|---------|
| **Options considered** | |
| **Decision** | |
| **Rationale** | |
| **Residual Risk** | |
| **Monitoring Plan** | |
| **Review Trigger** | |

---

## Task 3 — Design Simplicity Assessment

Evaluate CODING WAR architecture complexity and identify simplification opportunities. *"Complexity is the enemy of security"* — every unnecessary component is a potential attack surface:

| Component / Flow | Complexity Level (H/M/L) | Complexity Source | Security Risk from Complexity | Simplification Proposal | Trade-off if Simplified |
|-----------------|------------------------|------------------|------------------------------|------------------------|------------------------|
| **Authentication flow** | Medium | JWT access + refresh + revocation list | Token revocation logic adds complexity; revocation check on every request adds latency | Consider: short TTL only (no refresh tokens) for v1.0 — less complexity, acceptable UX | Users need to re-login after 15min — UX degradation |
| **Submission encryption** | High | Envelope Encryption + KMS integration + DEK lifecycle | Wrong implementation (static nonce, etc.) creates vulnerability; KMS unavailability blocks judging | Start with DB-level TDE (simpler) for v1.0; upgrade to Envelope Encryption in v2.0 | Less granular key control; CMK rotation affects all submissions not selectively |
| **Judge service isolation** | High | gVisor + namespace isolation + seccomp + resource limits | Complex sandbox config increases misconfig risk; each layer adds attack surface | Accept: complexity here is necessary — no simpler way to run untrusted code safely | N/A — cannot simplify without compromising core security property |
| \[Add component\] | | | | | |
| \[Add component\] | | | | | |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Privacy Design Controls Chain (5+ directives) | **25** | Each chain: policy → requirement → control → implementation → evidence is complete. Controls must be concrete, not "ensure privacy" |
| Trade-off Decision Log (5 scenarios) | **40** | Each decision: ≥2 options with pros/cons (4 pts), decision justified (2 pts), residual risk honest (2 pts), monitoring plan actionable (2 pts) |
| Design Simplicity Assessment (4+ components) | **20** | Complexity source specifically identified; risk from complexity explained; simplification proposal is realistic |
| Reasoning quality | **15** | Trade-off decisions demonstrate mature engineering judgment — not "always choose security"; decisions are context-appropriate |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-6.5.md](../solutions/sol-6.5.md)*
