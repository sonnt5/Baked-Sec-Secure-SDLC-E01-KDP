# Lab 4.7 — OWASP Full Threat Model Document

> **Chapter 4 · Threat Modeling and Risk-Driven Prioritization**
> Input: All Labs 4.1–4.6 | Output: Threat Model Document (OWASP format)

> [!NOTE]
> **New lab — OWASP Full Document:** Lab 4.7 is the sole synthesis exercise: teams assemble the complete output of Labs 4.1–4.6 into a finished OWASP-style Threat Model Document. This is the formal artifact submitted to the Software Design Review (SDR) gate. The document structure follows the OWASP Threat Modeling Process format exactly.

## Learning Objectives

- Synthesize all threat modeling artifacts into a single document following OWASP format.
- Understand how a Threat Model Document complements code review (OWASP: *"Complementing Code Review"*).
- Identify code review priorities derived from the threat model — this is the bridge between Threat Modeling and Security Testing.
- Practice writing an Executive Summary for non-technical stakeholders.

---

## Task 1 — Assemble the OWASP Threat Model Document

Complete each section below. Each section references a specific lab's output:

| § | OWASP Section | Content (pull from the corresponding lab) |
|---|--------------|------------------------------------------|
| **1** | **Threat Model Information** (from Lab 4.1, Task 1) | \[ \] Done → Application Name, Version, Description, Owner, Participants, Reviewer, Date, Methodology, Scope |
| **2** | **External Dependencies** (from Lab 4.2, Task 7) | \[ \] Done → DEP table: ≥5 dependencies with Trust Assumptions |
| **3** | **Entry Points** (from Lab 4.2, Task 5) | \[ \] Done → EP table with major.minor layering, Trust Level cross-ref |
| **4** | **Exit Points** (from Lab 4.2, Task 6) | \[ \] Done → XP table: ≥6 exit points with Potential Threats |
| **5** | **Assets** (from Lab 4.3, Task 1) | \[ \] Done → Asset table with Trust Level cross-ref and Priority ranking |
| **6** | **Trust Levels** (from Lab 4.2, Task 4) | \[ \] Done → Trust Level table with ID, Name, Description, Access Rights |
| **7** | **Data Flow Diagrams** (from Lab 4.2, Tasks 2–3) | \[ \] Done → DFD Level-0 + DFD Level-1 with trust boundaries annotated |
| **8** | **STRIDE Threat Analysis** (from Lab 4.4, Tasks 1–2) | \[ \] Done → STRIDE per element table; DREAD Qualitative scoring table |
| **9** | **Threat Trees** (from Lab 4.4, Task 3) | \[ \] Done → Account Takeover threat tree diagram + text representation |
| **10** | **STRIDE Mitigation Techniques** (from Lab 4.5, Task 1) | \[ \] Done → OWASP standard techniques applied to CODING WAR |
| **11** | **Misuse/Abuse Cases** (from Lab 4.5, Task 2) | \[ \] Done → MC-01 through MC-04 with full template |
| **12** | **Threat Profile** (from Lab 4.5, Task 3) | \[ \] Done → Non/Partially/Fully mitigated classification table + Summary |
| **13** | **Risk Register & Heatmap** (from Lab 4.6, Tasks 1–2) | \[ \] Done → Risk Register with L×I scoring; Risk Heatmap 5×5 |
| **14** | **Mitigation Plan** (from Lab 4.6, Task 3) | \[ \] Done → L/I/D strategies for Critical/High threats |
| **15** | **Q4 Assessment** (from Lab 4.6, Task 4) | \[ \] Done → Evidence checklist; scope assumptions; accepted/deferred threats |
| **16** | **Complementing Code Review** *(NEW — Task 2 below)* | \[ \] Done → Code review priorities derived from the threat model |
| **17** | **Executive Summary** *(NEW — Task 3 below)* | \[ \] Done → 1–2 page summary for non-technical stakeholders |
| **App. A** | **Privacy Impact Assessment** (from Lab 4.1, Tasks 2–3) | \[ \] Done → Privacy-by-Design lifecycle analysis |

---

## Task 2 — Complementing Code Review (OWASP)

> [!NOTE]
> **OWASP Note:** *"Threat modeling complements the security code review process. Inclusion of threat modeling early in the SDLC can help ensure applications are developed with appropriate security threat mitigations. This gives code reviewers a greater understanding of entry points and associated threats — promotes depth-first instead of breadth-first approach."*

Based on the CODING WAR Threat Model, identify Code Review priorities — which components need the deepest review:

| Code Component / Module | Related Threats | Review Priority (C/H/M) | Specific Code Patterns to Check | OWASP Testing Ref |
|------------------------|----------------|------------------------|--------------------------------|------------------|
| **AuthService — login() method** | TH-01 (Credential stuffing), AT-1.1 | CRITICAL | Rate limiting implementation, account lockout logic, password comparison (timing-safe?), failed attempt logging | OWASP WSTG-AUTHN-03 |
| **SubmissionController — submit()** | TH-03 (DoS), MC-02 (RCE) | CRITICAL | Resource limits enforcement, sandbox configuration, input size limits, code execution isolation | OWASP WSTG-INPV-12 |
| **SubmissionController — getById()** | TH-02 (IDOR) | CRITICAL | Authorization check: does code verify `submission.user_id == jwt.sub`? Is it missing? | OWASP WSTG-AUTHZ-01 |
| **AdminService — all methods** | TH-05 (Missing audit) | HIGH | Audit logging present for all admin actions? Append-only? Who can delete logs? | OWASP WSTG-SESS-07 |
| **Error handling — all controllers** | TH-04 (Verbose errors) | MEDIUM | Generic error messages to client? Stack traces suppressed? Internal paths hidden? | OWASP WSTG-ERRH-01 |
| **JudgeService — run()** | MC-02 (RCE chain) | CRITICAL | Sandbox config files, seccomp profiles, gVisor settings, network namespace rules | Infrastructure review |
| \[Add component\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Task 3 — Executive Summary

Write a 1–2 page Executive Summary for non-technical stakeholders (Product Manager, CISO, Business Owner):

| Section | Content |
|---------|---------|
| **System Analyzed** | CODING WAR v\[X.Y\] — \[1-sentence description\] |
| **Scope of Analysis** | \[Components in scope + out of scope — written concisely without technical jargon\] |
| **Key Findings — What We Found** | \[2–3 main points — e.g., *"The system has 3 critical vulnerabilities affecting..."*, *"There is no audit trail for..."*\] |
| **Risk Summary** | Critical: \[N\] issues · High: \[N\] issues · Medium: \[N\] · Low: \[N\] |
| **Top 3 Risks (Business Language)** | 1. \[Written as business impact, not technical — e.g., *"An attacker can take over any contestant's account via automated attack"*\] 2. \[Risk 2\] 3. \[Risk 3\] |
| **Privacy Concerns** | \[2–3 privacy points — for the Product/Legal team\] |
| **Recommended Actions — Top 5** | \[Ordered, written concisely: 1. Implement rate limiting and account lockout on login (1 sprint), 2. Fix IDOR vulnerability on submission API (1 day)...\] |
| **SDR Gate Recommendation** | \[ \] READY FOR SDR · \[ \] NEEDS MORE WORK — \[condition to proceed\]. Justification: \[2–3 sentences explaining the verdict\] |
| **Next Threat Model Review** | Trigger: when to update — \[e.g., when contest registration feature is added, when auth mechanism changes\] |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| OWASP Full Document Assembly (17 sections) | **40** | Each section: correct data from the correct lab (1.5 pts), completeness (1 pt), consistent with other sections (0.5 pts) |
| Complementing Code Review table | **30** | ≥6 components, specific patterns to check (not generic), OWASP Testing references included |
| Executive Summary (non-technical) | **30** | No jargon, business-impact language, Top 3 risks understandable by a PM, SDR verdict is justified |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-4.7.md](../solutions/sol-4.7.md)*
