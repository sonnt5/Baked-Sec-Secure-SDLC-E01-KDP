# Lab 5.2 — Structural Mitigations: Architecture Hardening

> **Chapter 5 · Mitigations, Security Patterns, and Cryptography**
> Input: Architecture Ch.3 + DFD Ch.4 | Output: Architecture Hardening Report + Annotated Diagram

> [!NOTE]
> **Artifact for this lab:** Architecture Hardening Report — includes: (1) Attack Surface Audit, (2) Windows of Vulnerability Analysis, (3) Data Minimization Plan, (4) PEP/PDP Placement Design, (5) Annotated Architecture Diagram. This is the technical deliverable for the SDR gate.

## Learning Objectives

- Conduct a systematic Attack Surface Audit — missing no entry points.
- Analyze Windows of Vulnerability and propose time-based defenses.
- Apply Data Minimization across 5 exposure surfaces.
- Design PEP/PDP placement — define where policy is enforced and where it is evaluated.
- Annotate the Architecture Diagram with structural security controls.

## Context

Structural Mitigations are the first and most important layer of defensive design — they change the architecture to make attacks fundamentally harder, rather than simply adding controls on top of the existing design. If the Architecture Diagram (Ch.3) is the blueprint for *"how to build"*, then the Architecture Hardening Report is the blueprint for *"how to make it harder to attack"*.

---

## Task 1 — Attack Surface Audit

Review the entire CODING WAR Attack Surface using the Entry Point Inventory from Lab 4.2. For each entry point, assess the potential to reduce the attack surface and identify compensating controls where reduction is not possible.

| EP ID | Interface / Endpoint | Reducible? | How to Reduce Attack Surface | Compensating Control if Not Reducible |
|-------|---------------------|-----------|------------------------------|---------------------------------------|
| **EP-1.1** | POST /api/v1/auth/login (public) | No — required | — | Rate limit + account lockout + CAPTCHA |
| **EP-1.6** | Admin console /admin/* (auth required) | Yes | IP allowlist + VPN requirement — reduce from public internet to internal network only | Full audit logging + MFA session |
| **EP-2** | Message queue consumer (internal) | Yes | Network policy: only judge-service pod can publish; schema validation rejects malformed messages | Dead letter queue + alerting on schema violations |
| **EP-1.2** | POST /api/v1/auth/register (public) | Yes — partially | Mandatory email verification before account activation; rate limit registration | CAPTCHA for bulk registration prevention |
| **EP-1.4** | POST /api/v1/submissions (auth) | No — core feature | — | Sandbox isolation + resource limits + timeout |
| **EP-1.5** | POST /api/v1/auth/password-reset (public) | No — required | — | Uniform response time (prevent timing attack) + email-only response |
| \[EP from Lab 4.2\] | | | | |
| \[EP from Lab 4.2\] | | | | |

After completing the table, calculate the **Attack Surface Score**: sum of all EP Risk Levels (Critical=4, High=3, Medium=2, Low=1). Record the score before and after applying proposed reductions.

| Metric | Before Hardening | After Hardening |
|--------|-----------------|----------------|
| **Total Attack Surface Score** | \[Calculate from EP Inventory\] | \[After applying reductions\] |
| **Number of CRITICAL EPs** | \[Calculate\] | \[After reductions\] |
| **Number of HIGH EPs** | \[Calculate\] | \[After reductions\] |
| **Number of publicly accessible EPs without rate limiting** | \[Calculate\] | \[After reductions\] |

---

## Task 2 — Windows of Vulnerability Analysis

A "Window of Vulnerability" is the time from when a vulnerability exists to when it is discovered or no longer exploitable. Analyze the 6 most important vulnerability windows in CODING WAR:

| Vulnerability Window | Begins when... | Ends when... | Estimated Duration | Solution to Shorten the Window |
|---------------------|---------------|-------------|-------------------|-------------------------------|
| **Compromised JWT token still valid** | Token is issued | Token expires | 15 minutes (access) / 7 days (refresh) | Reduce access TTL; implement token revocation list in Redis; forced rotation on suspicious activity |
| **Unpatched dependency with CVE** | CVE published | Patch deployed | Days–weeks if manual | SCA automated scan in CI/CD; dependency update bot (Renovate/Dependabot); CVE alert → auto-PR |
| **Session after password change** | Password changed | Old sessions expire | 15 minutes (current access TTL) | Invalidate ALL refresh tokens when password changes; maintain revocation list |
| **Admin credential leak** | Credential leaked | Rotation triggered | Undefined — no monitoring | Privileged access monitoring; anomaly detection (unusual hours, location); auto-alert |
| **No account lockout** | First failed attempt | — | No window close — vulnerability persists indefinitely | Implement lockout: 5 failures/10min → 15min lock → exponential backoff |
| **Unmonitored data export** | Export triggered | — | Indefinite — not detected | Audit log ALL exports; alert when bulk export > threshold; require justification field |

---

## Task 3 — Data Minimization Plan

Apply the *"Only the Data You Really Need"* principle across 5 exposure surfaces of CODING WAR. For each surface, identify what data is being over-exposed and propose a specific minimization approach.

### API Responses

| | |
|---|---|
| **❌ Current state** | `GET /api/v1/users/{id}` returns: `{id, username, email, full_name, phone, date_of_birth, created_at, last_login_ip, password_hash_preview, role, internal_db_id}` |
| **⚠️ Risk** | PII over-exposure; internal IDs leak; phone + DOB are not needed for any UI flow |
| **✅ Proposed minimization** | \[Fill in specific minimization approach — not generic\] |
| **🔧 Implementation** | \[Fill in implementation detail: Pydantic schema field exclusion / log redaction / opaque ID generation...\] |

### Error Messages

| | |
|---|---|
| **❌ Current state** | When SQL constraint fails: `{error: 'duplicate key value violates unique constraint users_email_key', detail: 'Key (email)=(user@test.com) already exists', hint: 'Change the conflicting key value'}` |
| **⚠️ Risk** | Database structure exposure; user enumeration; internal table names leaked |
| **✅ Proposed minimization** | \[Fill in specific minimization approach\] |
| **🔧 Implementation** | \[Fill in implementation detail\] |

### Application Logs

| | |
|---|---|
| **❌ Current state** | Access log: `'User john.doe@example.com (IP: 203.x.x.x) submitted code: import os; os.system("whoami")'` — raw PII + raw submission content |
| **⚠️ Risk** | PII in logs (GDPR risk); raw submission content creates additional attack surface if the log system is compromised |
| **✅ Proposed minimization** | \[Fill in specific minimization approach\] |
| **🔧 Implementation** | \[Fill in implementation detail\] |

### URLs & IDs

| | |
|---|---|
| **❌ Current state** | `GET /api/v1/submissions/12345` — sequential integer ID. Password reset: `/reset?email=user@example.com&token=abc123` |
| **⚠️ Risk** | IDOR (TH-02); user enumeration via email in URL; token exposed in server logs, browser history, CDN logs |
| **✅ Proposed minimization** | \[Fill in specific minimization approach\] |
| **🔧 Implementation** | \[Fill in implementation detail\] |

### JWT Token Payload

| | |
|---|---|
| **❌ Current state** | `{sub: 123, email: 'user@test.com', full_name: 'Nguyen Van A', phone: '0901234567', role: 'admin', exp: ...}` |
| **⚠️ Risk** | PII in JWT payload is base64-decoded by anyone with the token; phone + full_name are unnecessary for authorization |
| **✅ Proposed minimization** | \[Fill in specific minimization approach\] |
| **🔧 Implementation** | \[Fill in implementation detail\] |

---

## Task 4 — PEP/PDP Placement Design

Design the Policy Enforcement Points (PEP) and Policy Decision Points (PDP) for CODING WAR. A PEP is where access is blocked or allowed — a PDP is where the decision is computed.

> [!NOTE]
> **Reminder:** PEP enforces — PDP decides. Example: the API Gateway is a PEP (it blocks the request if the JWT is invalid), while the Auth Service is the PDP (it decides whether the JWT is valid). A well-designed trust boundary crossing must have at least 1 PEP.

| Location in Architecture | PEP or PDP? | Policy Enforced/Evaluated | Trust Boundary Covered | Implementation Approach |
|--------------------------|-------------|--------------------------|----------------------|------------------------|
| **API Gateway / Nginx** | PEP | Rate limiting, JWT signature validation, schema validation, TLS termination | B1 (Internet → Web Tier) | nginx rate_limit_zone + FastAPI middleware `@limiter.limit()` |
| **Auth Service — token verification** | PDP | Evaluate: signature valid? Token not expired? User active? Role matches requirement? | B1 → B2 | FastAPI `Depends(get_current_user)` — centralized auth dependency |
| **SubmissionController.submit()** | PEP | Enforce: user authenticated + enrolled in contest + contest currently active | B2 (Web → Service) | `Depends(verify_contest_enrollment)` dependency chain |
| **JudgeService consumer** | PEP + PDP | Validate message schema + verify message origin; decide if submission can be judged | B2 → B3 (Queue) | HMAC signature on messages + schema validation |
| **Database access layer** | PEP | Enforce: use least-privilege DB role per operation type | B3 (Service → Data) | Separate connection pools: `ro_pool` / `rw_pool` — not sharing admin connection |
| \[Add location\] | | | | |

---

## Task 5 — Annotated Architecture Diagram (Synthesis Artifact)

Based on the Architecture Diagram from Lab 3.2, create an Annotated version incorporating all structural security controls identified in Lab 5.2. This is the most visual artifact of the Architecture Hardening Report.

The diagram must show:
- PEP locations clearly marked (e.g., 🛡️ icon or distinct color)
- Trust Boundaries B1–B4 with annotation: controls applied at each boundary
- Data flows labeled: encrypted/plaintext, authenticated/unauthenticated
- Judge sandbox isolation: visual boundary around the judge container
- KMS/Secret Store if designed in Lab 5.5 (or a placeholder)

> 📎 Insert Annotated Architecture Diagram here
>
> Suggested tool: draw.io / Lucidchart / PlantUML. Open the file from Lab 3.2 and add a security annotation layer.
> Color coding: Red = high risk / unprotected, Yellow = partially protected, Green = well-controlled

> [!TIP]
> See `assets/CODING_WAR_AnnotatedArchitecture.drawio` for a reference solution. This is one valid approach — your team may have different annotation choices based on your specific design decisions.

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Attack Surface Audit + Score comparison | **25** | All EPs from Lab 4.2 included, reduction proposals are realistic, score improvement has specific numbers |
| Windows of Vulnerability (6 windows) | **24** | Each window: realistic duration estimate (2 pts) + specific implementable shortening solution (2 pts) |
| Data Minimization Plan (5 surfaces) | **25** | Each surface: problem correctly identified (1 pt) + specific solution, not generic (2 pts) + implementation approach (2 pts) |
| PEP/PDP Placement (5+ locations) | **16** | PEP vs PDP correctly distinguished, boundary covered is correct, implementation approach is feasible |
| Annotated Architecture Diagram | **10** | PEP locations marked, trust boundaries annotated, data flow security labels present |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-5.2.md](../solutions/sol-5.2.md)*
