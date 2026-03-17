# Solution 4.1 — OWASP Step 1a: Threat Model Information & Privacy

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — Threat Model Information Block

| Field | Value |
|-------|-------|
| **Application Name** | CODING WAR |
| **Application Version** | v1.0-beta |
| **Application Description** | CODING WAR is an online judge platform built for university programming contests. It allows contestants to submit code solutions that are automatically compiled, executed, and graded against test cases. The system supports problem management, contest organization, real-time scoring, and role-based access for contestants, problem setters, and admins. |
| **Document Owner** | Security Engineering Team |
| **Participants** | Security Engineer (lead), Backend Developer, Infrastructure/DevOps Engineer |
| **Reviewer(s)** | Security Architect |
| **Date Created** | \[Fill in\] |
| **Last Updated** | \[Fill in\] |
| **Methodology** | 4-Question Framework (Kohnfelder) + STRIDE per element + OWASP Threat Modeling Process |
| **Scope Summary** | In scope: CODING WAR web application, API server, JudgeService, PostgreSQL, Redis, RabbitMQ, MinIO. Out of scope: client browsers, upstream SMTP provider, external CDN. |
| **Related Documents** | SRS Lab 2.3 \| Architecture Design Lab 3.2 \| API Spec Lab 3.3 \| Deployment Design Lab 3.4 |

---

## Task 2 — Security vs. Privacy Classification

| # | Scenario | Type | Explanation |
|---|----------|------|-------------|
| 1 | Hacker steals DB password hashes via SQL injection | **S** | CIA violation (Confidentiality). The attacker bypasses a technical security control. No personal data handling policy is at issue. |
| 2 | CODING WAR logs contestant IPs without a deletion policy or ToS disclosure | **P** | Privacy issue: data is collected beyond necessity, retained without policy, and users are not informed. No security breach occurred. |
| 3 | Admin can view all submitted source code with no audit log | **B** | Both: Security (R — no audit trail, violates AAA) and Privacy (contestants' code is their intellectual work, accessed without transparency). |
| 4 | System requires a phone number at registration but never uses it | **P** | Privacy: data minimization principle violated. Collecting unnecessary PII. No security control is bypassed. |
| 5 | Error messages expose internal stack traces and system paths | **S** | Information Disclosure (CIA — Confidentiality). Leaking internal system details that could assist an attacker. |
| 6 | Contestant email list shared with sponsor without consent | **P** | Privacy: data shared beyond the original collection purpose without user consent. No security control is broken. |
| 7 | Session token doesn't expire after 30 days of inactivity | **S** | Security: session management flaw (broken authentication / AAA violation). Enables session hijacking after account compromise. |
| 8 | System logs record source code in plaintext without access controls | **B** | Both: Security (I — unauthorized access to logs violates CIA) and Privacy (source code is personal IP; unprotected plaintext log is a privacy violation). |

---

## Task 3 — Privacy-by-Design Data Lifecycle

### Data Type 1: Account information (username, email, password hash, IP)

| Stage | Current Mechanism | Privacy Risk | Proposed Improvement |
|-------|------------------|--------------|---------------------|
| **Collect** | Required at registration: username, email, password, IP logged on login | Over-collection of IP address; no explicit purpose stated | Collect only what is needed; document IP logging purpose in Privacy Policy |
| **Use** | Email for verification and notifications; IP for rate limiting; password hash for auth | IP could be used beyond stated purpose | Restrict IP use to security functions only; enforce purpose limitation |
| **Share** | Unknown — no sharing policy documented | Risk of sharing with sponsors, analytics providers, or third parties without consent | Document data sharing policy; prohibit sharing without explicit consent |
| **Retain** | No retention policy — data appears to be kept indefinitely | Unnecessary retention increases breach impact | Define retention periods: active accounts, inactive accounts (e.g., delete after 2 years of inactivity) |
| **Delete** | No deletion mechanism for users | Users cannot exercise right to erasure | Implement account deletion with cascading anonymization of linked submissions |

### Data Type 2: Source code submissions

| Stage | Current Mechanism | Privacy Risk | Proposed Improvement |
|-------|------------------|--------------|---------------------|
| **Collect** | Code submitted via POST /submissions; stored in DB | Code is intellectual property; collected without explicit ownership statement | Add ToS clause clarifying IP ownership of submitted code |
| **Use** | Used only for judging — but accessible to admins | Admin access to code without audit trail is a privacy risk | Log all admin access to submissions; restrict to specific justified roles |
| **Share** | Not shared externally — but no policy prevents it | Potential for contest organizer to share code samples publicly | Define explicit policy: code is private by default unless contestant opts in to public sharing |
| **Retain** | Retained indefinitely in DB | Unnecessary long-term retention of sensitive work | Define retention: delete contest submissions N months post-contest; offer export before deletion |
| **Delete** | No deletion | Contestants cannot remove their code | Allow deletion request; anonymize vs. hard delete based on contest integrity rules |

### Data Type 3: Judging results & scores

| Stage | Current Mechanism | Privacy Risk | Proposed Improvement |
|-------|------------------|--------------|---------------------|
| **Collect** | Auto-generated from judging; includes verdict, timing, memory | Timing data could be a side-channel | Aggregate timing before exposing; provide only verdict + pass/fail per test case |
| **Use** | Displayed on scoreboard; used for ranking | Public scoreboard exposes performance data contestants may wish to keep private | Offer opt-out from public scoreboard; allow anonymous display |
| **Share** | Public scoreboard is openly accessible | User enumeration via scoreboard | Add rate limiting; consider pseudonym display option |
| **Retain** | Retained indefinitely | Historical scores reveal patterns over time | Define retention: keep contest records for 1 year post-contest |
| **Delete** | No deletion | No right to erasure on performance data | Allow score anonymization (keep aggregate statistics, remove individual linkage) |

### Data Type 4: Problem test cases

| Stage | Current Mechanism | Privacy Risk | Proposed Improvement |
|-------|------------------|--------------|---------------------|
| **Collect** | Uploaded by Problem Setters to MinIO | Test cases represent problem setter IP | Add metadata: problem setter name, creation date, classification |
| **Use** | Used exclusively by JudgeService | Risk of unauthorized access if storage key is guessed or leaked | Use non-guessable storage keys (UUID-based); validate access before serving |
| **Share** | Should be admin + judge only — but not enforced | Test case leak compromises contest integrity | Enforce access policy: test cases only accessible to (3) Admin and (4) Judge Engine |
| **Retain** | Retained indefinitely in object storage | Unlimited accumulation of potentially sensitive data | Archive old test cases after contest ends; consider deletion after N years |
| **Delete** | No deletion policy | No lifecycle management | Define deletion: test cases deleted when problem is permanently retired |

---

## Task 4 — Adversarial Mindset

### Feature 1: New account registration

| 👷 Builder Mindset | 🔴 Attacker Mindset |
|-------------------|---------------------|
| A new user visits the registration page, fills in their username, email, and password, submits the form, receives a verification email, clicks the link, and their account is activated. | *"As a bot operator, I want to register thousands of fake accounts automatically so that I can inflate contest participation stats, use accounts for credential stuffing campaigns, or spam the scoreboard."* Asset: User DB (account pollution), Contest integrity. Harm: reputation damage, server load. |

### Feature 2: Submit a solution

| 👷 Builder Mindset | 🔴 Attacker Mindset |
|-------------------|---------------------|
| A contestant writes a solution, pastes it into the submission form, selects their language, clicks submit, and waits for the verdict to appear. | *"As a malicious contestant, I want to submit code containing system calls that escape the sandbox so that I can read other contestants' files, exfiltrate test cases, or cause the judge server to crash — gaining an unfair advantage or disrupting the contest."* Asset: Judge server, test cases, other submissions. Harm: RCE, data breach, contest disruption. |

### Feature 3: Password reset

| 👷 Builder Mindset | 🔴 Attacker Mindset |
|-------------------|---------------------|
| A user forgets their password, enters their email on the reset page, receives a reset link via email, clicks it, sets a new password, and logs in. | *"As an attacker, I want to probe the password reset endpoint with a large list of email addresses so that I can enumerate which accounts exist, then combine this list with breach databases to target specific users for account takeover."* Asset: Account list (privacy), user credentials. Harm: user enumeration enabling targeted account takeover. |

---

*Back to the lab: [labs/lab-4.1.md](../labs/lab-4.1.md)*
