# Lab 2.6 — Security Requirements Elicitation

> **Chapter 2 · Requirement Modeling**
> Input: SRS (Lab 2.3) + RTM (Lab 2.5) + Threat Landscape
> Output: Security-Augmented SRS + Updated RTM

> [!NOTE]
> **This lab is the bridge between Chapter 2 and Chapter 3.** It is where you begin to "bake security in" — embedding security at the requirements stage, rather than bolting it on at the end. The security requirements you write here will be directly referenced in Chapter 4 (Threat Modeling) and Chapter 8 (Security Testing).

## Learning Objectives

- Perform **Attack Surface Analysis** for CODING WAR.
- Identify and classify assets by sensitivity level.
- Elicit ≥15 Security NFRs covering the CIA Triad and AAA framework.
- **Embed** Security NFRs into the SRS — not as a separate document, but as part of Section 4.
- Update the RTM with security requirements and security-specific test case IDs.
- Reflect on the financial and security cost of discovering these issues at testing vs at requirements.

---

## Context: Why Security Requirements at This Stage?

Consider this scenario: the CODING WAR system is built and deployed. During a penetration test before launch, the tester discovers that contestant source code is stored unencrypted in the database, and that a crafted submission can escape the sandbox and read other users' files.

Fixing these issues at this stage means:
- Redesigning the storage encryption scheme (architectural change)
- Redesigning the sandbox isolation mechanism (infrastructure change)
- Rewriting the judging engine (major code change)
- Retesting the entire system

If these had been captured as **Security NFRs in the SRS**, they would have been designed into the architecture from day one — at a fraction of the cost.

This is the "bake security in" principle in practice.

---

## Deliverables

Two files:
1. `Lab2.6_[TeamName]_Security_Augmented_SRS.docx` — your Lab 2.3 SRS with Security Requirements added to Section 4 and Business Rules updated in Section 7.
2. `Lab2.6_[TeamName]_Updated_RTM.xlsx` — your Lab 2.5 RTM with Security NFRs mapped and a Security Category column added.

---

## Task 1 — Attack Surface Analysis

Before writing security requirements, you must understand the system's **attack surface** — every place where an attacker can interact with the system.

**1a. Entry Point Inventory**

List every entry point where an attacker could send input to the system. For each entry point:

| Entry Point | Input Type | Accessible by | Trust Level |
|------------|-----------|--------------|-------------|
| `/api/auth/login` (POST) | Username + password | Anyone (unauthenticated) | Untrusted |
| `/api/submissions` (POST) | Source code, language, problem ID | Authenticated contestants | Untrusted |
| Problem creation form | Problem statement, test case files | Problem Setters | Low-trust |
| Scoreboard API | (read-only) | Anyone | — |
| ... | | | |

Identify at least **8 distinct entry points**.

**1b. Asset Classification**

List all valuable assets in the system and classify their sensitivity:

| Asset | Description | Sensitivity Level |
|-------|-------------|------------------|
| User credentials (password hashes) | Stored in DB; used for authentication | Restricted |
| Test cases (input/output) | Secret during contests; defines correct answer | Confidential |
| Contestant source code | Submitted solutions | Internal |
| Contest results / verdicts | Determines rankings and prizes | Confidential |
| Judge Engine binary/config | Runs contestant code | Restricted |
| ... | | |

Sensitivity levels: **Public** (can be shared freely), **Internal** (within organisation), **Confidential** (specific need-to-know), **Restricted** (highest sensitivity, minimal access).

**Add this analysis to your SRS** as a new subsection — either in Section 4 (Non-functional Requirements) or as a new Appendix.

---

## Task 2 — Elicit Security Requirements

Based on your attack surface analysis, write **at least 15 Security NFRs**. You must independently determine which requirements are needed — the table below shows the groups to cover, not the requirements themselves.

| Group | CIA/AAA Category | Scope | Questions to ask yourself (not requirements) |
|-------|----------------|-------|----------------------------------------------|
| **Authentication** | Authentication | Login, Registration, Password Reset, Session | How does the system verify identity? How are passwords stored? How are sessions managed and invalidated? |
| **Authorization** | Authorization | RBAC, API access, Contest access | Who can do what? How is it enforced? How do we prevent a contestant from accessing another's submission? |
| **Input Validation** | Integrity | Code submission, Problem creation, All forms | How do we prevent SQL Injection, XSS, Command Injection via source code? What is validated and where? |
| **Sandbox Security** | Integrity + Availability | Judge Engine | How is contestant code prevented from affecting the server? What resource limits exist? What file system access is permitted? |
| **Data Protection** | Confidentiality | User data, Test cases, Submissions | What data is encrypted at rest? What data is encrypted in transit? Who may access what? |
| **Audit & Logging** | Accounting (Audit) | Admin actions, Login events, Submissions | What events are logged? How long are logs retained? Who may access logs? |
| **Communication Security** | Confidentiality | All client-server traffic, Email | Is all traffic over HTTPS? Are email reset tokens time-limited and single-use? |
| **Availability** | Availability | Full system, especially during contests | What is the SLA? How is the system protected against denial of service? What happens if the Judge Engine fails? |

**Format for each Security NFR:**

```
[NFR-SEC-001] [Critical] Authentication — The system shall store all user 
passwords using Argon2id with a minimum memory cost of 64 MB, a time cost 
of 3 iterations, and a parallelism factor of 4. Passwords shall never be 
stored in plaintext or using reversible encryption.

CIA/AAA Category: Authentication / Confidentiality
Related Entry Points: /api/auth/login, /api/auth/register
Acceptance Criteria:
  - Automated scan of the database confirms no plaintext passwords exist.
  - Argon2id parameters are verified against configuration: memory ≥ 64MB, 
    time ≥ 3, parallelism ≥ 4.
  - Penetration test: brute-force attack against a sample of 10,000 hashes 
    does not recover any password within 24 hours using standard hardware.
Priority: Must Have
```

---

## Task 3 — Integrate into the SRS

Update your SRS with the security requirements:

1. Add a sub-section **"4.x Security Requirements"** within Section 4 of the SRS. Group NFRs by the categories from Task 2.
2. Ensure Security NFRs are **inside** the SRS — not in a separate security document. Security is a quality attribute, not an afterthought.
3. Add **cross-references** from each Security NFR to the relevant Use Case or System Feature (e.g., NFR-SEC-001 → Section 3.1 User Authentication Feature).
4. Add **Business Rules** to Section 7 for security constraints that apply system-wide (e.g., "BR-13: All API endpoints that modify state must require authentication. No state-changing operation may be performed by an unauthenticated user.").

---

## Task 4 — Update the RTM

Add all Security NFRs to your RTM from Lab 2.5:

1. Each Security NFR must link to at least one **Business Requirement** (BRQ).
2. Each Security NFR must have at least one **Test Case ID** (to demonstrate it is testable).
3. Add a **"Security Category"** column (CIA/AAA) to the NFR sheet and the master Traceability Matrix sheet.
4. Calculate: what percentage of your total requirements are security-related? Record this metric in a summary cell.

---

## Task 5 — "Bake Security In" Reflection

Write a reflection of **300–500 words** answering these questions:

1. **What was missing?** Compare your original SRS (before Lab 2.6) with the security-augmented version. Which security requirements would have been completely absent if you had not done this lab? List at least 3 and explain the potential consequence of each being missing.

2. **Cost of delay.** Using Boehm's cost-of-defect curve: if the sandbox isolation requirement (NFR-SEC-xxx) had not been captured until the testing phase, what rework would be required? Estimate the relative cost compared to capturing it at the requirements phase.

3. **Highest-risk component.** Which component of CODING WAR has the largest attack surface? Justify your answer by referencing your entry point inventory from Task 1.

---

## Discussion Questions

**Q1:** A developer argues: *"We don't need to write security requirements now. We'll use a security framework later and it will handle everything."* What is the flaw in this reasoning? Give two specific examples from CODING WAR where a security framework alone would be insufficient.

**Q2:** NFR-SEC-xxx requires that *"no one, including Admin, may read another user's password."* This implies Argon2id one-way hashing. But what does this mean for a "forgot password" flow? Does it require changing the password reset design? Explain.

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Attack Surface Analysis | **15** | ≥8 entry points identified and described; assets classified with correct sensitivity levels |
| Security NFRs (≥15) | **30** | Cover all 8 required groups; each NFR has measurable Acceptance Criteria; correct CIA/AAA category; written to standard format |
| Integration into SRS | **15** | Security NFRs embedded correctly in Section 4; cross-references present; Business Rules updated |
| Updated RTM | **25** | All Security NFRs mapped; TC IDs present; Security Category column added; coverage metric calculated |
| Reflection (300–500 words) | **15** | Specific examples of what would have been missing; Boehm's curve applied correctly; highest-risk component justified |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-2.6.md](../solutions/sol-2.6.md)*
