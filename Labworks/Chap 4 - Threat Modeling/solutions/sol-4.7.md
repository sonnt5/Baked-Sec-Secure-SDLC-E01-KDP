# Solution 4.7 — OWASP Full Threat Model Document

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — Document Assembly Checklist (Verified)

| § | OWASP Section | Status | Notes |
|---|--------------|--------|-------|
| 1 | Threat Model Information | ✓ | Lab 4.1, Task 1 — all 11 fields |
| 2 | External Dependencies | ✓ | Lab 4.2, Task 7 — 7 dependencies |
| 3 | Entry Points | ✓ | Lab 4.2, Task 5 — 10+ EPs with major.minor |
| 4 | Exit Points | ✓ | Lab 4.2, Task 6 — 8 XPs |
| 5 | Assets | ✓ | Lab 4.3, Task 1 — 10 assets with Trust Level cross-ref |
| 6 | Trust Levels | ✓ | Lab 4.2, Task 4 — 9 Trust Levels |
| 7 | Data Flow Diagrams | ✓ | Lab 4.2, Tasks 2–3 — DFD-0 and DFD-1 |
| 8 | STRIDE Threat Analysis | ✓ | Lab 4.4, Tasks 1–2 — STRIDE per element + DREAD table |
| 9 | Threat Trees | ✓ | Lab 4.4, Task 3 — Account Takeover tree |
| 10 | STRIDE Mitigation Techniques | ✓ | Lab 4.5, Task 1 |
| 11 | Misuse/Abuse Cases | ✓ | Lab 4.5, Task 2 — MC-01 through MC-04 |
| 12 | Threat Profile | ✓ | Lab 4.5, Task 3 — with summary table |
| 13 | Risk Register & Heatmap | ✓ | Lab 4.6, Tasks 1–2 |
| 14 | Mitigation Plan | ✓ | Lab 4.6, Task 3 — 4 threats × 3 strategies |
| 15 | Q4 Assessment | Partial | Lab 4.6, Task 4 — deferred threats section incomplete |
| 16 | Complementing Code Review | ✓ | Lab 4.7, Task 2 |
| 17 | Executive Summary | ✓ | Lab 4.7, Task 3 |
| App. A | Privacy Impact Assessment | ✓ | Lab 4.1, Tasks 2–3 |

**Issue noted:** Section 15 (Q4 Assessment) is incomplete — deferred/accepted threats lack justification. This must be addressed before the document is ready for SDR.

---

## Task 2 — Complementing Code Review (Completed)

| Code Component | Related Threats | Priority | Specific Patterns to Check | OWASP Testing Ref |
|---------------|----------------|----------|---------------------------|------------------|
| **AuthService — login()** | TH-01, AT-1.1 | CRITICAL | (1) Is login rate limiting implemented? Check Redis counter increment logic. (2) Is account lockout triggered after N failures? Check failed_attempt counter update. (3) Is password comparison timing-safe? Check `hmac.compare_digest()` vs. `==`. (4) Are all failed attempts logged with IP + timestamp? | WSTG-AUTHN-03, WSTG-AUTHN-04 |
| **SubmissionController — submit()** | TH-03, MC-02 | CRITICAL | (1) Is submission rate limiting applied (30/hour/user)? (2) Is code size validated before queue? (3) Is the message published to queue with schema validation? (4) Does the controller return 202 Accepted (async) not 200 with result? | WSTG-INPV-12, WSTG-BUSL-09 |
| **SubmissionController — getById()** | TH-02 (IDOR) | CRITICAL | (1) Is there a line checking `submission.user_id == current_user.id`? (2) Does the check happen before any DB query? (3) Is Admin access routed through a separate endpoint with audit? (4) Is the check present on ALL HTTP methods (GET, PUT, DELETE)? | WSTG-AUTHZ-01 (BOLA/IDOR) |
| **JudgeWorker — run()** | MC-02 (RCE) | CRITICAL | (1) Is sandbox configured with `--runtime=runsc` (gVisor)? (2) Is the seccomp profile applied? (3) Is outbound network blocked? Verify Docker network flags. (4) Are memory/CPU/time limits set and enforced? (5) Does the worker run as non-root (uid 65534)? | Infrastructure security review |
| **AdminService — all write methods** | TH-05 | HIGH | (1) Does every write method (create, update, delete) call `audit_logger.log()`? (2) Is the audit log write in the same transaction as the operation? (3) Can the audit log be deleted or modified by anyone? (4) Does each log entry include: who, what, when, from where? | WSTG-SESS-07, custom audit policy |
| **Error handler — all controllers** | TH-04 | MEDIUM | (1) Is there a global exception handler that sanitizes error messages? (2) Does any 500 error response include a stack trace? (3) Are internal paths, file names, or version strings stripped? (4) Is the internal error logged (for debugging) while only a generic message is returned to the client? | WSTG-ERRH-01, WSTG-ERRH-02 |
| **Password reset — /auth/password-reset** | MC-01 (Enumeration) | HIGH | (1) Does the response differ between "email found" and "email not found"? (Must be identical.) (2) Is the response time constant regardless of email lookup result? (3) Is the reset token a cryptographically random UUID, not a predictable sequence? (4) Is TTL ≤15 minutes enforced? | WSTG-AUTHN-09, WSTG-AUTHN-10 |

---

## Task 3 — Executive Summary

| Section | Content |
|---------|---------|
| **System Analyzed** | CODING WAR v1.0-beta — an automated online judge platform for university programming contests |
| **Scope of Analysis** | In scope: Web application, API server, automated judge, database, cache, and message queue. Out of scope: contestant's personal devices, the SMTP email provider, and external CDN. |
| **Key Findings** | (1) The system has **3 critical, unmitigated vulnerabilities** that allow attackers to take over accounts, view other contestants' code, and execute arbitrary code on the server. (2) There is **no audit trail** for any administrator action — it is currently impossible to determine who changed or deleted contest data. (3) Several security controls exist at the network layer (TLS, internal network isolation) but are absent at the application layer (rate limiting, authorization checks). |
| **Risk Summary** | Critical: 3 issues · High: 4 issues · Medium: 4 issues · Low: 1 issue |
| **Top 3 Risks (Business Language)** | **1.** An attacker can automatically submit thousands of login attempts and take over any contestant account — disrupting a live contest and exposing private code. **2.** A contestant can submit a program that breaks out of the sandbox and reads or destroys server data — including test cases for problems that haven't been published yet. **3.** Any logged-in contestant can view the source code of any other contestant's submission — enabling academic dishonesty and violating intellectual property. |
| **Privacy Concerns** | (1) IP addresses are logged on every submission with no defined retention limit. (2) Source code (intellectual property) is retained indefinitely with no deletion option. (3) There is no disclosure in the Terms of Service explaining how contestant data is used or retained. |
| **Recommended Actions — Top 5** | 1. Fix the IDOR vulnerability on the submission endpoint — add an ownership check (estimated: 1 day). 2. Enable gVisor sandbox on the judge execution environment — prevents server takeover (estimated: 1 sprint). 3. Implement login rate limiting and account lockout — prevents credential stuffing (estimated: 1 sprint). 4. Add an append-only audit log for all admin actions — restores non-repudiation (estimated: 1 sprint). 5. Sanitize all error messages — remove stack traces and system paths from API responses (estimated: 2 days). |
| **SDR Gate Recommendation** | \[ \] READY FOR SDR · **[✓] NEEDS MORE WORK** — the 2 non-mitigated critical vulnerabilities (IDOR and missing audit log) must be fixed, and the RCE via sandbox must be at least planned and tracked before design review approval. The document itself is complete; the system is not yet secure. |
| **Next Threat Model Review** | Trigger: (1) When the contest registration flow is redesigned. (2) When the authentication mechanism changes (e.g., adding OAuth/SSO). (3) When a new judge language is added. (4) After any critical security incident. Scheduled review: 6 months from today. |

---

*Back to the lab: [labs/lab-4.7.md](../labs/lab-4.7.md)*
