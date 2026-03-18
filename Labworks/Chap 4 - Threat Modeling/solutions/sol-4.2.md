# Solution 4.2 — OWASP Step 1b: DFD + Entry/Exit Points + Trust Levels + External Dependencies

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 2 — DFD Level-0: Description

The DFD Level-0 (Context Diagram) shows CODING WAR as a single process surrounded by external entities:

- **External Entities:** Browser/Client (Contestant, Admin, Anonymous), Email Service (SMTP)
- **System Process:** CODING WAR System
- **Key Data Flows:** HTTP requests in / HTTP responses out; email notifications out
- **Trust Boundary B1:** Internet ↔ CODING WAR (dashed border)

> 📎 See `assets/CODING_WAR_ThreatModel_OWASP.json` — import into OWASP Threat Dragon to view the rendered DFD.

## Task 3 — DFD Level-1: Key Elements

**Processes (≥5):** Authentication Service, Problem Service, Submission Service, JudgeWorker, Contest/Scoreboard Service

**Data Stores (≥4):** PostgreSQL DB, Redis Cache, RabbitMQ Queue, S3-compatible Object Storage

**Trust Boundaries (≥4):**
- B1: Internet → Nginx/Web Tier
- B2: Web Tier → Application Services
- B3: Application Services → Data Tier (DB, Cache, Queue)
- B4: Application Services → JudgeWorker (separate execution environment with network isolation and mTLS authentication)

---

## Task 4 — Trust Levels (Additional entries)

| ID | Name | Description | Linked Entry Points | Linked Assets |
|----|------|-------------|---------------------|--------------|
| **7** | Object Storage Service Account | S3-compatible storage account used by the application to read/write test case files | \[Internal B3 boundary\] | Asset 3 (Test Cases — full access) |
| **8** | Secret Manager | Vault/AWS Secrets Manager service that holds credentials | \[Internal — accessed at startup\] | Asset 4 (JWT Secret), Asset 6 (DB Connection Strings) |
| **9** | NTP Service | Network Time Protocol service for time synchronization across servers | \[External dependency\] | Contest timing integrity (Start/End Time) |

---

## Task 5 — Additional Entry Points

| EP ID | Name | Description | Trust Levels | Risk Level |
|-------|------|-------------|-------------|-----------|
| **1.7** | Submission Status Polling | GET /api/v1/submissions/{id} — polls for judging result | (2) Contestant | MEDIUM |
| **1.8** | Contest Scoreboard | GET /api/v1/contests/{id}/scoreboard | (1) Anonymous (public), (2) Contestant | LOW |
| **1.9** | Problem Management API | POST/PUT/DELETE /api/v1/problems/* | (3) Admin | HIGH |
| **2** | Message Queue (RabbitMQ) | Internal queue — App Service publishes submission tasks, JudgeService consumes | (4) Judge Engine, Internal Services | HIGH |
| **3** | Object Storage (S3-compatible) | Internal API — JudgeService reads test case files via mTLS | (4) Judge Engine, (7) Storage SA | HIGH |

---

## Task 6 — Additional Exit Points

| XP ID | Name | Description | Potential Threats | Controls Needed |
|-------|------|-------------|------------------|----------------|
| **XP-07** | Judge Execution Output | Compilation errors and runtime output returned to contestant | I (compiler error reveals language version, file paths), I (timing reveals test case count) | Sanitize compiler output; return generic timing; redact system paths |
| **XP-08** | Contest Result Announcement | System announcement when contest ends | I (contestant list exposure), S (spoofed announcement) | AuthN on announcement push; rate limit notification emails |

---

## Task 7 — External Dependencies (Additional)

| DEP ID | Description | Under Dev Team Control? | Trust Assumption | Risk if Compromised |
|--------|-------------|------------------------|-----------------|---------------------|
| **DEP-06** | DNS provider — domain resolution for coding-war.example.com | No (Registrar/Infra) | DNS records are correct and not hijacked | DNS hijacking → all traffic redirected to attacker |
| **DEP-07** | TLS certificate (Let's Encrypt or CA) | Partial (Infra renews) | Certificate is valid and renewed before expiry | Expired cert → browser warnings; MITM possible if MiTM CA compromise |
| **DEP-08** | NTP Service (Network Time Protocol) | No (Infrastructure/OS) | System clocks are synchronized across all servers | Time drift → contest start/end time inconsistencies, JWT expiry issues |

---

*Back to the lab: [labs/lab-4.2.md](../labs/lab-4.2.md)*
