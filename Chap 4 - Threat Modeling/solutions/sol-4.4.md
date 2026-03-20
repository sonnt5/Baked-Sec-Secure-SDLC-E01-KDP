# Solution 4.4 — OWASP Step 2: STRIDE + Threat Trees + DREAD Qualitative Scoring

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — STRIDE / CIA-AAA Mapping (Completed)

| STRIDE | Full Name | CIA/AAA Violated | Primary DFD Element | Specific Example in CODING WAR |
|--------|-----------|-----------------|---------------------|--------------------------------|
| **S** | Spoofing | Authentication | External Entity | Credential stuffing on POST /auth/login using stolen password lists from public breach databases |
| **T** | Tampering | Integrity | Data Flow, Data Store | Modifying the submission JSON payload in transit to change the code being judged |
| **R** | Repudiation | Auditing | Process, Data Store | Admin deletes a problem with no audit trail — who deleted it cannot be determined (Note: admin_audit_logs table designed in SDD to address this) |
| **I** | Information Disclosure | Confidentiality | Data Flow, Data Store | Judge engine returns detailed stack traces and system paths in error responses, exposing internal system structure |
| **D** | Denial of Service | Availability | Process, Data Flow | Submitting an infinite loop or exponential time complexity code that consumes all CPU time on the judge node, blocking other contestants |
| **E** | Elevation of Privilege | Authorization | Process, Trust Boundary | Contestant accesses GET /submissions/{id} for a submission they don't own (IDOR/BOLA) — accessing another user's source code without authorization |

---

## Task 2 — STRIDE per Element (Selected Examples)

### External Entities

| Element | STRIDE | Threat Scenario | Asset at Risk | Current Control |
|---------|--------|----------------|---------------|----------------|
| **Contestant** | **S** | Attacker uses a list of credentials from a breach database and scripts automated login attempts against POST /auth/login. Successful login gives account access without knowing the password. | Asset 1.1 (Contestant Login Details) | TLS: ✓, Account lockout: MISSING, Rate limit: MISSING |
| **Admin** | **S** | Attacker gains admin credentials via phishing or password reuse, then logs into /admin/* with full system access. | Asset 1.2 (Admin Login Details), Asset 3 (Test Cases) | TLS: ✓, MFA: MISSING, IP whitelist: MISSING |
| **Anonymous Guest** | **S** | Attacker uses the registration endpoint to create thousands of fake accounts, polluting the user database and enabling future abuse. | Asset: User DB integrity | CAPTCHA: MISSING, Email verification: ✓ |

### Processes / Services

| Element | STRIDE | Threat Scenario | Asset at Risk | Current Control |
|---------|--------|----------------|---------------|----------------|
| **Authentication Service** | **T** | Attacker intercepts a login response and attempts JWT forgery. With RS256 (asymmetric key per SDD), the attacker cannot forge tokens without the private key. Risk: misconfiguration allowing weaker algorithms. | Asset 4 (JWT Signing Secret) | JWT signature verification with RS256: ✓ (per SDD), explicit algorithm validation needed in code |
| **Authentication Service** | **R** | A failed login attempt by an attacker is not logged. No evidence exists to reconstruct brute force attempts or account compromise timeline. | Asset 9 (Admin Audit Logs) | Login success logged: likely ✓, Failed attempts logged: MISSING |
| **Authentication Service** | **I** | Error message on failed login differs between "user not found" and "wrong password" — allows attacker to enumerate valid usernames. | Asset 1.1 (Login Details) | Uniform error message: MISSING |
| **Submission & Judge Service** | **T** | Attacker modifies the message in RabbitMQ queue to change the submission's language field from Python to C++ after submission, potentially bypassing input validation or triggering a different execution path. | Asset 2 (Source Code), Asset 3 (Test Cases) | Message signing: MISSING |
| **Submission & Judge Service** | **I** | Judge returns compilation error containing the full system path of temporary files: `/tmp/judge_abc123/contestant_solution.cpp:4: error` — exposing internal file structure. | Asset 9 (System Logs) | Error message sanitization: MISSING |

### Data Flows

| Element | STRIDE | Threat Scenario | Asset at Risk | Current Control |
|---------|--------|----------------|---------------|----------------|
| **HTTP request: client → API** | **T** | MITM attacker on same network intercepts and modifies API request — changes contest_id in submission to submit to a different contest. | Asset 2 (Submissions) | TLS: ✓ (prevents this if properly implemented) |
| **JWT token in header** | **I** | JWT token is transmitted in URL query parameter instead of Authorization header — exposed in server access logs and browser history. | Asset 4 (JWT Signing Secret implication) | Proper use of Authorization header: needs verification |
| **Message: submission → Judge Queue** | **D** | Attacker submits thousands of submissions rapidly, flooding the RabbitMQ queue and starving legitimate contestants of judging capacity. | Availability of Judge Service | Rate limiting per user: MISSING |

---

## Task 3 — Threat Tree: Account Takeover (Completed)

| Node ID | Description | AND/OR | Parent | Mitigation |
|---------|-------------|--------|--------|-----------|
| **AT-0** | Account Takeover (ROOT GOAL) | OR | — | Defense-in-depth: MFA + rate limiting + monitoring |
| **AT-1** | Steal Credentials | OR | AT-0 | MFA, HTTPS, anti-phishing training |
| **AT-1.1** | Credential stuffing via /login | Leaf | AT-1 | Rate limit 10/min/IP, account lockout after 5 failures, CAPTCHA |
| **AT-1.2** | Phishing for password | Leaf | AT-1 | MFA, security awareness training |
| **AT-1.3** | Password breach database attack | Leaf | AT-1 | Breach monitoring alerts, forced password rotation notification |
| **AT-2** | Bypass Authentication | OR | AT-0 | Algorithm validation, secure JWT implementation with RS256 |
| **AT-2.1** | JWT algorithm confusion (RS256 treated as HS256) | Leaf | AT-2 | Explicitly validate algorithm in JWT library config; reject any algorithm except RS256 |
| **AT-2.2** | Compromise or guess JWT signing private key | Leaf | AT-2 | Use cryptographically random 4096-bit RSA key; rotate every 90 days; store in Secret Manager |
| **AT-2.3** | Password reset token manipulation | Leaf | AT-2 | Short TTL (15 min), single-use tokens, HTTPS-only reset links |
| **AT-3** | Session Hijacking | OR | AT-0 | Secure cookie flags, session timeout, HttpOnly cookies |
| **AT-3.1** | Steal session token from insecure storage | Leaf | AT-3 | HttpOnly + Secure cookie flags per SDD; never use localStorage for tokens |
| **AT-3.2** | XSS to extract token from DOM | Leaf | AT-3 | CSP headers; output encoding; HttpOnly cookie (JS cannot access) |
| **AT-3.3** | Session fixation | Leaf | AT-3 | Regenerate session ID after successful login |

---

## Task 4 — DREAD Qualitative Scoring (Additional Threats)

| Threat ID | Threat Summary | Remote exploit? | Auth needed? | Automatable? | Likelihood | System takeover? | Admin access? | Crash system? | PII exposed? | Impact | Risk |
|-----------|---------------|----------------|-------------|--------------|-----------|-----------------|--------------|--------------|-------------|--------|------|
| **TH-06** | JWT algorithm confusion (RS256/HS256) | Y | Y (need valid JWT structure) | Y | LOW | N | Y (if admin JWT) | N | Y | CRITICAL | MEDIUM |
| **TH-07** | Test case exfiltration via storage key guessing | Y | Y (contestant) | Y | LOW | N | N | N | Y (test cases) | HIGH | MEDIUM |
| **TH-08** | Scoreboard scraping for user enumeration | Y | N | Y | HIGH | N | N | N | Y (username/score) | LOW | MEDIUM |
| **TH-09** | Flood registration to exhaust DB capacity | Y | N | Y | MEDIUM | N | N | Y | N | HIGH | HIGH |
| **TH-10** | Missing CSP allows XSS in problem description | Y | Y (admin) | N | LOW | N | N | N | Partial (token via XSS) | MEDIUM | MEDIUM |

---

*Back to the lab: [labs/lab-4.4.md](../labs/lab-4.4.md)*
