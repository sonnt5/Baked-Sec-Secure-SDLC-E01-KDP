# Lab 6.7 — Full SDR Practice: From Design to Verdict

> **Chapter 6 · Security Design and Review**
> Input: CODING WAR design artifacts | Output: Complete SDR Report with Issue Log, Verdict, and Action Items

> [!NOTE]
> **Artifact for this lab:** Complete SDR Report — includes: (1) Issue Log (Table 6-8 style) with ≥8 issues, (2) 4-Questions Assessment, (3) Verdict with justification, (4) Action Items with owners and due dates, (5) Disagreement Log if applicable. This is the most important artifact of Chapter 6 — input for the Bug Bar (Ch.8/9).

## Learning Objectives

- Practice a complete SDR session: apply all 6 steps, apply the 4-question framework.
- Distinguish severity levels (Critical/High/Medium/Low) based on business impact — not just "sounds scary."
- Write an Issue Log following the standard format from the Chapter 6 SDR example.
- Issue a Verdict with justification — not APPROVED when CRITICAL issues exist.
- Manage disagreements constructively: document, not escalate prematurely.

## Context

Lab 6.7 is the convergence point of all of Chapter 6: all artifacts from Labs 6.1–6.6, plus artifacts from Ch.3–5, are brought into a real SDR session. The Reviewer (one team member, or the instructor) plays the Reviewer role; the rest form the Design Team.

> [!NOTE]
> **SDR Lens:** An SDR is not a test. The Reviewer is not trying to fail the design team. The goal is to find structural weaknesses before code is written, not after. Tone: analytical adversarialism with cooperative conduct.

---

## Task 1 — Apply the 4 Questions Framework

Before writing the Issue Log, apply the 4-Questions Framework to structure your thinking:

| Question | Answer for CODING WAR |
|----------|----------------------|
| **Q1: What are we working on?** (Scope, value, what must be protected, unnecessary features?) | System: CODING WAR — online competitive programming platform. In Scope: Authentication, Submission API, Judge Engine, Contest Management, Scoreboard, Admin Console. High Value Assets: Test cases (contest integrity), JWT signing key (auth bypass), User credentials, Verdict records. Out of Scope: Payment processing (no payments in v1.0), Mobile app (web only). Underprotected features: \[Fill in — based on your artifact review\] |
| **Q2: What can go wrong?** (Top threats, consequences, which risks are acceptable?) | Top 5 threats (from Risk Register Ch.4 + Interface Catalogue Ch.6.3): ① Credential Stuffing on /auth/login → Account takeover (Critical); ② IDOR on /submissions/{id} → Contestant IP theft (High); ③ RCE via Judge Sandbox escape → Host compromise (Critical); ④ Admin abuse without 2-person approval → Contest result manipulation (High); ⑤ Test case exfiltration via side-channel → Contest integrity loss (High). Accepted risk (with justification): \[Fill in at least 1\]. Risks NOT acceptable: \[Fill in — these are blocking conditions for SDR approval\] |
| **Q3: What are we going to do about it?** (Mitigations sufficient? Anything insufficient?) | Sufficient mitigations: ✓ TLS everywhere (SR-C01 — verified via nginx config) ✓ Envelope Encryption for submissions (SR-C02 — CDR-002 decided) ✓ gVisor sandbox (Lab 5.2 — assumption verified?). Insufficient / Missing: ✗ Account lockout NOT YET IMPLEMENTED (TH-01 CRITICAL gap) ✗ 2-person approval for admin bulk ops NOT YET IMPLEMENTED ✗ Evidence for audit log tamper-evidence not yet provided. \[Fill in more based on artifact review\] |
| **Q4: Did we do a good job?** (Overall verdict — Approved / Conditions / Rejected?) | \[Fill in after completing Issue Log — verdict must reference specific issues\]. Draft: APPROVED WITH CONDITIONS — conditions to be listed in Issue Log. Blocking conditions (must resolve before coding begins): ① \[Fill in CRITICAL issue 1\] ② \[Fill in CRITICAL issue 2\]. Non-blocking (must resolve before release, tracked in Bug Bar): ③ \[Fill in HIGH issues\] |

---

## Task 2 — SDR Issue Log (Main Artifact)

Complete the Issue Log using the Chapter 6 SDR format. Need ≥8 issues from the CODING WAR design review. Each issue must have a Pattern/Anti-pattern reference.

> [!WARNING]
> **Severity criteria:** CRITICAL = must fix before design is approved (architectural flaw, blocks SDR). HIGH = must fix before release (significant risk, tracked in Bug Bar). MEDIUM = should fix in next sprint (moderate risk). LOW = recommendation/improvement. Severity must be justified — do not raise or lower without reasoning.

| # | Area / Endpoint | Issue (Current State & Impact) | Pattern / Anti-pattern | Severity / Status | Notes & Actions |
|---|----------------|-------------------------------|----------------------|------------------|----------------|
| **1** | Auth Service POST /auth/login | Missing account lockout — no protection against credential stuffing after rate limit bypass via distributed IPs. IP-based rate limit alone is insufficient: attacker with 1M IP botnet can attempt 5M passwords/hour. | Violates: Fail Securely (should deny after N failures). Violates: Defense in Depth (single control layer only) | **CRITICAL Fail** | Implement per-email account lockout: 5 failures/10min → 15min lock (exponential backoff). Add monitoring: alert when single email has >10 failures/hour. Test: `test_account_lockout_after_5_failures` must pass before design approved. |
| **2** | Submission API GET /submissions/{id} | IDOR — object-level authorization not explicitly verified in code design. Architecture doc shows `verify_submission_owner()` but code review not confirmed. If missing: attacker iterates IDs to read all submissions. | Violates: Complete Mediation (side door exists if ownership check missing). Violates: Least Privilege | **CRITICAL Fail** | Code review mandatory before SDR close: verify `Depends(verify_submission_owner)` present on ALL GET/PUT/DELETE submission endpoints. Add negative test: contestant A cannot read contestant B submission. Evidence required. |
| **3** | Admin Console /admin/* | No 2-person approval for destructive operations (bulk cancel, user data export, verdict override). Single admin account can manipulate an entire contest. UI hides links but backend RBAC not enforced (Security by Obscurity). | Violates: Separation of Privilege. Anti-pattern: Security by Obscurity | **CRITICAL Fail** | Design 2-person approval workflow for: bulk ops >50 records, data export, verdict modification. Implement backend RBAC (not UI-only). MFA for all admin sessions. Due: before construction sprint 1. |
| **4** | Judge Sandbox Interface I6 | gVisor sandbox assumed to provide isolation but assumption not verified (Assumption Register: status=Unverified). If assumption wrong, RCE escape possible. Contestant code runs with unknown privilege level. | Assumption Register: ASS-03 unverified. Risk: Confused Deputy (JudgeService executes with elevated privilege based on untrusted input) | **HIGH Fail (Conditional)** | Mandatory: run CIS Docker Benchmark against judge container config. Verify seccomp profile blocks fork bombs + outbound network. Test: attempt sandbox escape with known bypass techniques. Result must be documented as evidence before release. |
| **5** | JWT Implementation Auth Service | JWT signing uses HS256 (symmetric) in current CDR draft. HS256 requires same secret in all services that verify JWT — if one service is compromised, can forge tokens for all services. | Crypto Decision: CDR-003 should specify ES256 over HS256 for multi-service architecture. Reluctance to Trust: symmetric secret shared across trust boundaries weakens isolation | **HIGH Fail** | Update CDR-003: choose ES256 (ECDSA P-256). Justification: public key verification only — compromised service cannot forge tokens. Implement key rotation plan. Due: CDR update before first code commit. |
| **6** | Assumption Register — 4 Unverified Assumptions | 4 of 6 assumptions in Assumption Register remain "Unverified." Design validity depends on these assumptions. If any is wrong, security model may collapse. | Design Assumption: unverified assumptions are latent risks. Transparent Design: security should not depend on hoped-for environment properties | **MEDIUM Fail** | Assign owner and deadline for each unverified assumption. Critical assumptions (mTLS enforcement, JWT secret not in code) must be verified before release. Others: documented acceptance + monitoring plan. Track in backlog. |
| **7** | Password Reset POST /auth/password-reset | Response time difference between existing vs non-existing email allows user enumeration. Attacker can determine if email is registered by measuring response latency. | Violates: Avoid Predictability (behavioral pattern reveals information). Violates: Least Information | **MEDIUM Fail** | Implement constant-time response: both "user exists" and "user not found" return identical message AND response time (`dummy_verify()` + `time.sleep(max_time - actual_time)`). Test: timing attack test must show <5ms variance. |
| **8** | Audit Log — Admin Actions | Audit log append-only claim not verified by evidence. Claim: admin cannot delete own audit trail. Implementation: not confirmed. If admin CAN delete audit log, non-repudiation is broken. | Violates: Transparent Design (security depends on implementation correctness not verified). CAE-04 evidence gap: no test confirming DELETE on audit_log returns 403 for app user | **HIGH Fail (Conditional)** | Add test: attempt DELETE on `audit_log` table as app service account → must return permission denied. Verify: audit_log DB user has INSERT only, no DELETE/UPDATE. Add to CAE-04 evidence list. |
| \[9\] | \[Team adds\] | \[Fill in issue\] | \[Pattern/Anti-pattern\] | \[Severity\] | \[Actions\] |
| \[10\] | \[Team adds\] | \[Fill in\] | \[Pattern\] | | |

---

## Task 3 — SDR Verdict & Action Plan

| Section | Content |
|---------|---------|
| **SDR Verdict** | \[ \] APPROVED · \[ \] APPROVED WITH CONDITIONS · \[ \] REJECTED. \[Choose one — CODING WAR currently has 3 CRITICAL issues → cannot be APPROVED unconditionally\] |
| **Blocking Conditions** *(must resolve before design is approved)* | List the CRITICAL issues that block approval: 1. \[Issue #, description, required resolution\] 2. \[Issue #, description, required resolution\] 3. \[Issue #, description, required resolution\] |
| **Non-Blocking Requirements** *(must resolve before release — tracked via Bug Bar)* | List HIGH issues: 1. \[Issue #, description, sprint target\] 2. ... \[MEDIUM issues tracked as Technical Debt\] |
| **Strengths (acknowledged)** | \[2–3 things the design does well — an SDR is not only about finding problems. Example: TLS config is thorough; Envelope Encryption design is sound; Interface Catalogue shows security thinking from the start\] |
| **Next SDR Trigger** | \[When should a follow-up SDR be triggered? E.g.: "After CRITICAL issues resolved — mini-SDR to verify resolution. Full re-SDR if auth mechanism changes significantly."\] |
| **Executive Summary** *(for non-technical stakeholders)* | \[2–3 sentences: what was reviewed, key finding, recommendation — written as if sending to CTO\]. Example template: "CODING WAR design was reviewed on [date] covering auth, submission pipeline, and admin interfaces. Three critical design issues were identified affecting account security, data isolation, and admin controls. Design approval is deferred until these issues are resolved, estimated [timeframe]." |

---

## Task 4 — Managing Disagreements

**Roleplay scenario:** Designer disagrees with Reviewer about the severity of Issue #4 (Judge Sandbox). Designer argues: *"gVisor is industry standard — verification is a waste of time."* Reviewer maintains: severity HIGH.

Complete the Disagreement Log and simulate resolution:

| | | |
|---|---|---|
| **Disagreement about** | **Designer's Position** | **Reviewer's Position** |
| Issue #4 severity: is gVisor sandbox verification required? | gVisor is industry standard, Kubernetes-backed project, dozens of major companies use it. Verification is unnecessary and wastes engineering time. | Standard ≠ correctly configured. Assumption: gVisor config is correct for CODING WAR's specific use case. One misconfigured seccomp rule = sandbox escape. HIGH severity until verified. |

| Areas of Agreement | Options | Resolution (or Escalation Path) |
|-------------------|---------|--------------------------------|
| gVisor is the appropriate technology choice. The goal is the same: safe execution environment. | Option A: Accept HIGH severity, add verification test to sprint (2-day effort). Option B: Reduce to MEDIUM, add monitoring for anomalous syscall patterns (faster). Option C: Document as accepted risk with business justification. | \[Fill in: which option the team agreed on, or escalation path if no agreement\] |

**Analysis question:** Why does recording a disagreement (even when unresolved) still have value in an SDR?

> \[Fill in: ≥3 reasons why documented disagreement is valuable — traceability, future accountability, incident learning...\]

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| 4-Questions Framework answers | **20** | Q3 and Q4 must reference specific issues and evidence — not generic statements |
| Issue Log — ≥8 issues × 5 fields | **50** | Each issue: current state + impact clear (3 pts), pattern/anti-pattern correct (2 pts), severity justified (2 pts), actions are actionable (3 pts). Severity inflation/deflation without justification = deduction |
| SDR Verdict + Action Plan | **20** | Verdict is non-trivial (not "APPROVED" for design with 3 CRITICAL issues); blocking conditions are specific and verifiable; executive summary is non-technical |
| Disagreement analysis | **10** | ≥3 reasons why documented disagreement is valuable; demonstrates SDR maturity |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-6.7.md](../solutions/sol-6.7.md)*
