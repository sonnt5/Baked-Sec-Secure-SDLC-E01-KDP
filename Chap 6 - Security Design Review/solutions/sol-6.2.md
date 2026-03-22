# Solution 6.2 — Measurable Security Requirements & Protection Goals

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.

---

## Task 1 — Admin Accountability and Credential Security Protection Goals

| Business Objective | Protection Goal | If Not Met |
|-------------------|----------------|-----------|
| **Admin accountability** | Every admin action must be attributable to a specific individual; no admin can deny having performed an action; audit records must survive for ≥90 days and cannot be deleted by the actor (per admin_audit_logs table design in SDD 7.2) | Contest manipulation goes undetected; legal liability in prize disputes; compliance audit failures |
| **Credential security** | User accounts must resist automated credential attacks; a compromised single password must not be sufficient to take over an account (MFA for admin accounts per security requirements); account recovery must not create new attack vectors | Mass account takeover during a contest; reputational damage; potential prize fraud |

---

## Task 2 — Additional Requirements (Team-added examples)

| ID | Goal Area | End Goal | Metric / Threshold | Test Condition | Owner |
|----|----------|----------|--------------------|---------------|-------|
| **SR-C03** | Secret Management | JWT signing secret and DB credentials must not appear in source code, logs, or environment dumps | 0 occurrences in git history; 0 in application logs; stored only in KMS/Vault or secure environment variables | `gitleaks` scan in CI returns 0 findings; grep for known secret patterns in log samples returns 0 matches | DevOps + Security |
| **SR-AAA03** | Authorization Scope | A contestant may only access their own submission data; no cross-user data leakage via any API endpoint | 0 successful IDOR exploits in security testing; 100% submission endpoints have ownership verification | Penetration test: iterate 1000 submission IDs as contestant B — 0 records returned that belong to contestant A | Backend |
| **SR-P02** | Data Retention | Submission source code must be purged after 2 years post-contest (per privacy policy); user accounts inactive for 2+ years must be anonymized | 0 submissions older than 2 years in DB (verified by scheduled audit); 0 active PII fields for accounts inactive >2 years | Scheduled retention job test; verify: no plaintext email for accounts `last_login_at < now - 2years` | DevOps / Data Owner |

---

## Task 3 — Traceability Matrix (Additional Rows)

| Business Objective | Protection Goal | Requirement ID | Design Mechanism | Pattern |
|-------------------|----------------|---------------|-----------------|---------|
| Credential security | User enumeration prevention | SR-AAA01 (uniform response) | `PasswordResetService.constant_time_response()` + `dummy_verify()` | Avoid Predictability + Least Information |
| Participant privacy | PII minimization in logs | SR-P01 | Privacy-Aware Log Schema (Lab 6.4) + `build_access_log()` function | Least Information |
| Credential security | Secret management | SR-C03 | gitleaks in CI + KMS/Vault for JWT + DB credentials (Lab 5.5 CDR) | Transparent Design + Secure by Default |

---

*Back to the lab: [labs/lab-6.2.md](../labs/lab-6.2.md)*
