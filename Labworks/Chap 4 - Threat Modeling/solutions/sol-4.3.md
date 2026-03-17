# Solution 4.3 — OWASP Step 1c: Assets + Attack Surface Mapping

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — Asset Register (Additional Assets)

| ID | Name | Description & Why Protected | Tier | Sensitivity | Trust Levels with Access |
|----|------|------------------------------|------|-------------|--------------------------|
| **7** | **Session Tokens (Redis)** | JWT refresh tokens stored in Redis. Compromise → persistent session hijacking without needing credentials. | Tier 1 | CRITICAL | (2) Contestant — own token; (3) Admin; internal Redis only |
| **8** | **Rate Limit State (Redis)** | Counter state for rate limiting per IP/user. Manipulation → rate limit bypass, enabling brute force. | Tier 2 | MEDIUM | (4) Internal Services; Infra team |
| **9** | **System Logs** | Application logs containing request metadata, user IDs, submission IDs, IP addresses. | Tier 2 | HIGH | (3) Admin; DevOps; SIEM system — append-only ideally |
| **10** | **gVisor/Sandbox Configuration** | seccomp profiles and sandbox configs controlling what judge-executed code can do. Compromise → sandbox escape enablement. | Tier 1 | CRITICAL | DevOps only; not accessible from app code |

---

## Task 2 — Asset Priority Ranking (Corrected Ranking)

Corrected full ranking after adding all assets:

| Rank | Asset ID | Asset Name | Priority Score | Rationale |
|------|----------|-----------|---------------|-----------|
| #1 | 4 | JWT Signing Secret | 12 | Highest: full auth bypass if compromised |
| #2 | 10 | Sandbox Config | 12 | Highest: RCE escape possible if misconfigured |
| #3 | 7 | Session Tokens | 9 | Session hijacking without credential theft |
| #4 | 1.1 | Contestant Login Details | 9 | Mass account takeover |
| #5 | 1.2 | Admin Login Details | 8 | Admin takeover — high privilege |
| #6 | 3 | Test Cases | 6 | Contest integrity, competitive fairness |
| #7 | 5 | Contest Results | 6 | Public scoreboard manipulation |
| #8 | 2 | Source Code Submissions | 4 | IP theft, academic dishonesty |
| #9 | 6 | DB Connection Strings | 4 | DevOps-only access reduces exposure |

---

## Task 4 — Entry Point Control Matrix (Additional EPs)

| EP ID | Endpoint | Trust Level Required | Current Controls | Missing Controls | Fix Priority |
|-------|---------|---------------------|-----------------|-----------------|-------------|
| **1.7** | GET /submissions/{id} | (2) Contestant | JWT Auth, TLS | Object-level ownership check (`submission.user_id == jwt.sub`) | CRITICAL |
| **1.9** | POST/PUT /api/v1/problems/* | (3) Admin / (7) Problem Setter | JWT Auth, Role check | Audit log for all changes, version history | HIGH |
| **3** | MinIO Object Storage | (4) Judge Engine, (8) SA | Internal network only | Pre-signed URL expiry (short TTL), Access logging | HIGH |

---

## Notes on Attack Surface Map

The Attack Surface Map should show:

- **CRITICAL (Red):** EP-1.1 (Login), EP-1.4 (Submissions), EP-1.6 (Admin Console), EP-1.7 (Submission getById)
- **HIGH (Orange):** EP-1.5 (Password Reset), EP-2 (Message Queue), EP-3 (Object Storage)
- **MEDIUM/LOW (Blue/Green):** EP-1.2 (Registration), EP-1.3 (Problem List), EP-1.8 (Scoreboard)

The map groups EPs into 4 zones: HTTP API (public), Admin Zone (restricted), Internal Services (message queue, object storage), and Email (external).

---

*Back to the lab: [labs/lab-4.3.md](../labs/lab-4.3.md)*
