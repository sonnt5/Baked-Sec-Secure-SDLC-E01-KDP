# Lab 4.3 — OWASP Step 1c: Assets + Attack Surface Mapping

> **Chapter 4 · Threat Modeling and Risk-Driven Prioritization**
> Input: DFD from Lab 4.2 | Output: Asset Register, Attack Surface Map, EP Control Matrix

> [!NOTE]
> **OWASP Note:** The OWASP Asset format includes: ID, Name, Description, AND Trust Levels (cross-reference). This is a key distinction: each asset is linked to the Trust Levels that have access — creating a clear authorization matrix for security design.

## Learning Objectives

- Build an Asset Register in OWASP format with Trust Level cross-references.
- Calculate a Priority Score and build an Asset Tier Pyramid.
- Create an Attack Surface Map and an Entry Point Control Matrix.

---

## Task 1 — Asset Register (OWASP format with Trust Level cross-ref)

| ID | Name | Description & Why Protected | Tier | Sensitivity | Trust Levels with Access (from Lab 4.2) |
|----|------|------------------------------|------|-------------|----------------------------------------|
| **1** | **User Credentials** | Password hashes + email. Compromise → account takeover chain. | Tier 2 | HIGH | (2) Contestant — own account; (3) Admin — all accounts; (5) DB Read User; (6) DB R/W User |
| **1.1** | **Contestant Login Details** | username, email, password_hash of contestants | Tier 2 | HIGH | (2) Contestant — own only; (3) Admin; (5) DB Read; (6) DB R/W |
| **1.2** | **Admin Login Details** | username, email, password_hash of admins | Tier 1 | CRITICAL | (3) Admin — own only; (5) DB Server Admin |
| **2** | **Source Code Submissions** | Submitted source code. If leaked → academic dishonesty risk. | Tier 3 | MEDIUM | (2) Contestant — own only (should be); (3) Admin; (4) Judge Engine; (6) DB R/W |
| **3** | **Test Cases (Problem Solutions)** | Input/output test cases. Leak → contest integrity compromise. | Tier 2 | HIGH | (3) Admin only; (4) Judge Engine; (6) DB R/W |
| **4** | **JWT Signing Secret** | Secret key to sign/verify JWTs. Compromise → full auth bypass. | Tier 1 | CRITICAL | (3) Admin (infra); Secret Manager only |
| **5** | **Contest Results & Scores** | Rankings, scores. Manipulation → reputation damage. | Tier 3 | MEDIUM | (2) Contestant — read own; (3) Admin — all; public scoreboard (limited) |
| **6** | **Database Connection Strings** | DB URL + credentials. Compromise → direct DB access. | Tier 1 | CRITICAL | DevOps team, Secret Manager only |
| \[Add Asset\] | \[Fill in\] | \[Fill in\] | \[Tier\] | \[Sensitivity\] | \[Fill in Trust Levels — cross-ref to Lab 4.2\] |

---

## Task 2 — Asset Priority Ranking

Priority Score = Sensitivity (1–4) × Exposure Level (1–4). Rank and note the protection priority:

| Asset ID | Asset Name | Sensitivity (1–4) | Exposure Level (1–4) | Priority Score | Rank | Protection Priority Note |
|----------|-----------|-------------------|---------------------|---------------|------|--------------------------|
| **4** | JWT Signing Secret | 4 (Tier 1) | 3 (internal + config access) | 12 | #1 | Secret Manager, 90-day rotation, never log |
| **1.2** | Admin Login Details | 4 (Tier 1) | 2 (limited access) | 8 | #2 | Mandatory MFA, IP whitelist on admin console |
| **3** | Test Cases | 3 (Tier 2) | 2 (judge internal access) | 6 | #3 | Read-only access for judge, admin-only writes |
| **1.1** | Contestant Login Details | 3 (Tier 2) | 3 (contestant + admin) | 9 | \[Rank?\] | Bcrypt min cost 12, rate limit on login |
| **6** | DB Connection Strings | 4 (Tier 1) | 1 (DevOps only) | 4 | \[Rank?\] | Vault/Secret Manager, never in source code |
| **2** | Source Code Submissions | 2 (Tier 3) | 2 (contestant/admin) | 4 | \[Rank?\] | Object-level AuthZ, no public access |
| **5** | Contest Results | 2 (Tier 3) | 3 (public scoreboard) | 6 | \[Rank?\] | Read-only public, write protected |

---

## Task 3 — Attack Surface Map

> 📎 Insert Attack Surface Map here
>
> Draw the system at the center. Surrounding it: EPs grouped by type (HTTP API, Admin Console, Message Queue, File Upload). Color-code by risk: Red = CRITICAL, Orange = HIGH, Blue/Green = MEDIUM/LOW. Annotate the Trust Level required for each EP.

---

## Task 4 — Entry Point Control Matrix

| EP ID | Endpoint | Trust Level Required | Current Controls | Missing Controls | Fix Priority |
|-------|---------|---------------------|-----------------|-----------------|-------------|
| **1.1** | POST /auth/login | (1) Anonymous | TLS/HTTPS | MFA option, Account lockout, CAPTCHA after 3 fails, Rate limit per IP | CRITICAL |
| **1.4** | POST /submissions | (2) Contestant | JWT Auth, TLS | Sandbox isolation, Resource limits (CPU/mem/time), Outbound network block | CRITICAL |
| **1.5** | POST /auth/password-reset | (1) Anonymous | TLS | Uniform response (prevent enumeration), Rate limit, Email-only response, Constant response time | HIGH |
| **1.6** | Admin Console /admin/* | (3) Admin | JWT Auth | Mandatory MFA, IP whitelist, Audit log for all actions, Session timeout | CRITICAL |
| **2** | Message Queue | (4) Judge Service | Internal network | Schema validation, Dead letter queue, Message signing/verification | HIGH |
| \[EP from Lab 4.2\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Asset Register with Trust Level cross-ref | **30** | ≥8 assets, Trust Levels correctly linked to Lab 4.2, Description explains why each is protected |
| Priority Ranking | **20** | Score calculated correctly, ranking is logical, Protection Note is realistic |
| Attack Surface Map | **20** | All EPs present, grouped clearly, risk color-coding applied, Trust Levels annotated |
| EP Control Matrix | **30** | Current controls are accurate, missing controls are realistic and specific |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-4.3.md](../solutions/sol-4.3.md)*
