# Lab 4.2 — OWASP Step 1b: DFD + Entry/Exit Points + Trust Levels + External Dependencies

> **Chapter 4 · Threat Modeling and Risk-Driven Prioritization**
> Input: Architecture from Lab 3.2 | Output: DFD-0, DFD-1, Entry/Exit table, Trust Levels, External Deps

> [!NOTE]
> **OWASP Note:** OWASP highlights 4 critical elements when scoping the work: (1) Entry Points — where attackers interact; (2) Exit Points — where data leaves the system (often overlooked but important for XSS and information disclosure); (3) Trust Levels — access rights with cross-references; (4) External Dependencies — production environment and third-party components outside the dev team's control.

## Learning Objectives

- Draw DFD Level-0 and Level-1 using correct DFD notation per the OWASP/Microsoft threat modeling standard.
- Identify both Entry Points AND Exit Points (OWASP) — cross-referenced to Trust Levels.
- Build a Trust Levels table: define access tiers and link them to Entry Points and Assets.
- Create an External Dependencies table: document dependencies outside the dev team's control.

---

## Task 1 — DFD Notation Legend

Before drawing, confirm your understanding of DFD symbols per the OWASP/Microsoft standard:

| Symbol Shape | DFD Element | Description | Example in CODING WAR |
|-------------|-------------|-------------|----------------------|
| **Rectangle** | External Entity | An entity outside the system that interacts via an entry point | Contestant, Admin, Email Service |
| **Circle / Oval** | Process | A task that processes data within the system | Authentication Service, JudgeService |
| **Two parallel horizontal lines** | Data Store | A location where data is stored (does not modify data) | PostgreSQL DB, Redis Cache |
| **Arrow with label** | Data Flow | The direction data moves | POST /submissions → Judge Queue |
| **Dashed border** | Trust Boundary | A boundary where the trust level changes | Internet → Web Tier (B1) |

---

## Task 2 — DFD Level-0 (Context Diagram)

Draw the DFD Level-0: the system as a single process, external entities, primary data flows, and the Internet trust boundary.

> 📎 Insert DFD Level-0 (Context Diagram) here
>

---

## Task 3 — DFD Level-1 (Decomposed)

Decompose the system into ≥5 processes, ≥4 data stores, and ≥4 trust boundaries (B1–B4).

> 📎 Insert DFD Level-1 here
>
> Recommendation: annotate \[S\]\[T\]\[R\]\[I\]\[D\]\[E\] on the DFD at risk points after completing Lab 4.4

---

## Task 4 — Trust Levels (OWASP)

> [!NOTE]
> **OWASP Note:** OWASP defines Trust Levels as *"access rights that the application will grant to external entities."* Trust Levels are cross-referenced with Entry Points and Assets. This creates a 3-dimensional matrix: Entry Point × Trust Level × Asset — which helps identify authorization gaps.

| ID | Name | Description | Linked Entry Points | Linked Assets |
|----|------|-------------|--------------------|--------------| 
| **1** | Anonymous User | Unauthenticated user — can only access public pages | EP-01 (login page), EP-04 (register) | Asset: Public problem list only |
| **2** | Authenticated Contestant | Logged-in user with Contestant role | EP-02 (submit), EP-03 (view problems), EP-09 (view own submissions) | Asset: Own submissions, contest data |
| **3** | Authenticated Admin | Logged-in user with Admin role | EP-06 (create contest/problem), EP-08 (admin console) | Asset: All problems, all submissions, user data |
| **4** | Judge Engine (Internal Service) | Internal service that executes judging code | EP-07 (message queue consumer) | Asset: Execution environment, test cases |
| **5** | Database Service Account (Read) | DB account with SELECT privilege only | \[Internal B3 boundary\] | Asset: Read access to all DB tables |
| **6** | Database Service Account (Read/Write) | DB account with SELECT/INSERT/UPDATE | \[Internal B3 boundary\] | Asset: Full DB read/write access |
| **7** | \[Add trust level\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Task 5 — Entry Points (OWASP format with Trust Level cross-reference)

> [!NOTE]
> **OWASP Note:** The OWASP Entry Points format uses a major.minor ID scheme to represent layering (e.g., EP 1.1 is a sub-entry of EP 1 — HTTPS Port). This is more precise than a flat list.

| EP ID | Name | Description | Trust Levels | Risk Level |
|-------|------|-------------|--------------|-----------|
| **1** | HTTPS Endpoint | All CODING WAR traffic enters via TLS/HTTPS. All EPs below are sub-entries. | (1) Anonymous User, (2) Authenticated Contestant, (3) Admin | — |
| **1.1** | Login Page / API | POST /api/v1/auth/login — accepts credentials, verifies against DB, returns JWT | (1) Anonymous User, (3) User with Invalid Credentials | HIGH |
| **1.2** | Registration Page / API | POST /api/v1/auth/register — creates a new account | (1) Anonymous User | MEDIUM |
| **1.2.1** | Registration Validation Function | Validates email format, username uniqueness, password strength | (1) Anonymous User | MEDIUM |
| **1.3** | Problem List / Detail | GET /api/v1/problems, GET /api/v1/problems/{id} | (1) Anonymous, (2) Contestant | LOW |
| **1.4** | Submission API | POST /api/v1/submissions — submits source code | (2) Authenticated Contestant | CRITICAL |
| **1.5** | Password Reset | POST /api/v1/auth/password-reset | (1) Anonymous User | MEDIUM |
| **1.6** | Admin Console | /admin/* — manage problems, users, contests | (3) Admin | CRITICAL |
| **2** | Message Queue (Internal) | submission.created topic — triggers the judge service | (4) Judge Engine (Internal) | HIGH |
| \[Add EP\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Task 6 — Exit Points (OWASP — often overlooked)

> [!NOTE]
> **OWASP Note:** OWASP emphasizes Exit Points because they are associated with information disclosure and XSS. *"Exit points might prove useful when attacking the client: cross-site-scripting vulnerabilities and information disclosure vulnerabilities both require an exit point for the attack to complete."* All locations where data leaves the system must be listed.

| XP ID | Name | Description | Potential Threats | Controls Needed |
|-------|------|-------------|------------------|----------------|
| **XP-01** | Login Response | Response from /auth/login — returns JWT or an error message | I (error message leaks user existence), R (failed attempts not logged) | Uniform error messages, log ALL attempts |
| **XP-02** | Submission Result Response | Judge response: verdict, execution time, memory usage | I (verbose errors expose judge internals), I (timing side-channel) | Generic errors, sanitize judge output |
| **XP-03** | Problem Detail Page | HTML/JSON serving problem content — may contain dynamic data | T (XSS if admin input not sanitized), I (test case hints leak) | Output encoding, CSP header |
| **XP-04** | Scoreboard / Rankings | Public endpoint returning contestant rankings | I (user enumeration via scoreboard), D (scraping causes load) | Rate limit, pagination, optional anonymization |
| **XP-05** | Email Notifications | System emails: contest results, password reset links | I (reset link may be intercepted), S (email spoofing) | HTTPS reset links, short TTL, DKIM/SPF |
| **XP-06** | Admin Export (if present) | Admin exports user lists / submissions as CSV/Excel | I (mass data exfiltration), R (no audit trail for exports) | Auth check, audit log, rate limit |
| \[Add XP\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Task 7 — External Dependencies (OWASP)

> [!NOTE]
> **OWASP Note:** *"External dependencies are items external to the code of the application that may pose a threat. These items are typically still within the control of the organization, but possibly not within the control of the development team."* These must be documented to understand trust assumptions.

| DEP ID | Description | Under Dev Team Control? | Trust Assumption | Risk if Compromised |
|--------|-------------|------------------------|-----------------|---------------------|
| **DEP-01** | CODING WAR will deploy on a hardened Linux server (Ubuntu 22.04). Server has a firewall exposing only ports 443 and 22 (restricted). | No (Infra/Ops team) | Server hardening is correct; OS patches are up-to-date | Server takeover if unpatched CVE |
| **DEP-02** | PostgreSQL database server on a separate node with TLS. Only the app server is whitelisted. | No (DB Admin) | DB-level access control is correct; backup policy exists | Full data exfiltration |
| **DEP-03** | Redis cache for sessions and rate limiting. Non-persistent. | No (Infra team) | Redis is not accessible from the Internet; memory-only | Session hijacking, rate limit bypass |
| **DEP-04** | Email service (SMTP provider — e.g., SendGrid). External. | No (Third-party) | SMTP provider delivers reliably; TLS for transmission | Password reset token interception |
| **DEP-05** | Judge execution sandbox (Docker + gVisor). Managed by DevOps. | Partial (Infra deploys, Dev team configures) | Sandbox isolation is effective; gVisor blocks syscalls | RCE escape from sandbox |
| **DEP-06** | \[Add dependency\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| DFD-0 + DFD-1 (correct notation) | **25** | Correct symbols (rectangle/circle/parallel lines/arrow/dashed), ≥4 trust boundaries |
| Trust Levels table (OWASP format) | **20** | ≥6 trust levels, clear cross-reference to EPs and Assets |
| Entry Points (major.minor layering) | **20** | ≥10 EPs with layered notation, Trust Level cross-ref for each EP |
| Exit Points | **20** | ≥6 XPs with specific potential threats (not just "information disclosure") |
| External Dependencies | **15** | ≥5 dependencies, trust assumptions and risks documented |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-4.2.md](../solutions/sol-4.2.md)*
