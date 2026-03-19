# Lab 6.1 — Evidence-Based Design: CAE Chain & Assumption Register

> **Chapter 6 · Security Design and Review**
> Input: SRS Ch.2 + Threat Model Ch.4 | Output: CAE Table + Assumption Register

> [!NOTE]
> **Artifacts for this lab:** (1) CAE Table — linking Claim → Argument → Evidence for 5 security requirements. (2) Assumption Register — recording assumptions, verification methods, fallbacks, and owners. These two artifacts are the traceability backbone for all of Chapter 6.

## Learning Objectives

- Understand and apply the Claim-Argument-Evidence (CAE) model — why *"security claims"* without argument and evidence are meaningless.
- Build a CAE chain from security requirements → design mechanisms → verifiable evidence.
- Identify and document design assumptions — what the team *"believes to be true"* but has not yet verified.
- Understand why a wrong assumption can invalidate an entire risk assessment.

## Context

In security design, saying *"the system has been secured"* is insufficient. An SDR requires: a specific security **claim**, an **argument** explaining why the mechanism satisfies the claim, and **evidence** proving the mechanism is working. The CAE model creates a *"traceability backbone"* from requirements to implementation to proof — security is no longer a black box.

---

## Task 1 — Understanding the CAE Model Through a CODING WAR Example

Analyze the following sample CAE entry and answer the questions below:

| CAE Element | Content (sample — CODING WAR) |
|------------|-------------------------------|
| **Claim (What)** | CODING WAR prevents an attacker from gaining access to another contestant's submission data through the API (IDOR prevention). |
| **Argument (Why)** | Every `GET /api/v1/submissions/{id}` request passes through `SubmissionController.verify_submission_owner()`, which queries the DB to verify `submission.user_id == jwt.sub` of the requester. Only admins (role='admin') are exempt. Trust boundary B2 enforces this before business logic runs. Patterns applied: Least Privilege + Complete Mediation. |
| **Evidence (Proof)** | ① `tests/test_idor.py::test_contestant_a_cannot_read_contestant_b_submission` — pytest verifies 403 is returned. ② `tests/test_idor.py::test_admin_can_read_any_submission` — verifies admin exception. ③ Code review checklist item #7: "All object endpoints have owner verification." ④ Log sample: audit_log shows rejected cross-user access attempt. |

**Questions:**

1. If Evidence ① (the pytest test) does not exist, can this claim be approved by the SDR? Why?

2. The Argument references patterns "Least Privilege + Complete Mediation." If there is an internal admin script that queries the DB directly without going through `verify_submission_owner()`, which pattern does this violate? Is the claim still valid?

3. The current Evidence has 4 items. Which items are MUST HAVE (claim fails without them) and which are NICE TO HAVE? Explain your reasoning.

---

## Task 2 — Build the CAE Table (Main Artifact)

Build a CAE Table for 5 of CODING WAR's most important security requirements. Draw from the MRS in Lab 6.2 (preview if needed) or identify 5 requirements from the Threat List in Ch.4.

> [!NOTE]
> **A strong CAE entry:** Claim is specific and bounded (not "the system is secure"), Argument links the mechanism to a pattern, Evidence is a testable artifact — not "plan to test." A weak entry: vague Claim, Argument only says "uses authentication," Evidence is "will write test later."

### CAE-01: Credential Stuffing Prevention — POST /auth/login

| CAE Element | Content |
|------------|---------|
| **Claim (What — specific, bounded, testable)** | |
| **Argument (Why — mechanism + pattern link)** | |
| **Evidence (Proof — testable artifacts, test IDs, log samples, config files)** | |

### CAE-02: IDOR Prevention — /submissions/{id}

| CAE Element | Content |
|------------|---------|
| **Claim (What)** | |
| **Argument (Why)** | |
| **Evidence (Proof)** | |

### CAE-03: Code Execution Isolation — Judge Sandbox

| CAE Element | Content |
|------------|---------|
| **Claim (What)** | |
| **Argument (Why)** | |
| **Evidence (Proof)** | |

### CAE-04: Audit Trail Integrity — Admin Actions

| CAE Element | Content |
|------------|---------|
| **Claim (What)** | |
| **Argument (Why)** | |
| **Evidence (Proof)** | |

### CAE-05: \[Team's choice — from Threat List\]

| CAE Element | Content |
|------------|---------|
| **Claim (What)** | |
| **Argument (Why)** | |
| **Evidence (Proof)** | |

---

## Task 3 — Assumption Register

Design assumptions are *"truths"* the team assumes to be correct when designing. If an assumption is wrong, the design may fail. Identify ≥6 important assumptions in the CODING WAR design and complete the Assumption Register:

> [!WARNING]
> **Context:** Example of a dangerous assumption: *"Only internal services call the JudgeService API"* — if this is wrong (an attacker can reach JudgeService directly because a firewall is misconfigured), the entire security model of the Judge Sandbox collapses. Assumptions must be verified, not just assumed.

| # | Assumption | Verification Method | Fallback if Wrong | Owner | Metric / Evidence | Status |
|---|-----------|--------------------|--------------------|-------|------------------|--------|
| **1** | Only internal services (Auth Service, Judge Service) can call internal APIs — internet has no direct access | mTLS certificates required; firewall allowlist; network policy test | Deny non-mTLS traffic; alert and quarantine source; switch to read-only mode | Infra/DevOps | 0% unauthenticated calls in prod logs; 100% endpoints enforce mTLS | Unverified |
| **2** | JWT signing key has not leaked into source code or logs | Git secret scanning (gitleaks) in CI; KMS audit log; log redaction check | Immediately rotate key; invalidate all active sessions; incident response | Security/DevOps | 0 key occurrences in git history; KMS access log clean | Unverified |
| **3** | gVisor sandbox completely isolates contestant code from the host OS | Sandbox escape test (CIS benchmark); seccomp profile review; network isolation test | Block submissions; escalate to infrastructure team; temporary manual judging | DevOps | 0 successful sandbox escapes in penetration test | Unverified |
| **4** | \[Fill in assumption about database access control\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | Unverified |
| **5** | \[Fill in assumption about third-party dependencies\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | Unverified |
| **6** | \[Fill in assumption about admin account security\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | Unverified |

**After completing the table, answer:**

4. Which assumption has the most severe consequences if wrong? Explain using a specific attack scenario.

5. Why does an Assumption Register with unverified entries (status: Unverified) still have value in an SDR? What does it provide compared to having nothing?

6. When should an assumption be *"escalated"* to a verified constraint rather than just documented?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| CAE analysis (3 questions) | **15** | Answers demonstrate understanding of CAE mechanics, not just definitions |
| CAE Table — 5 entries | **50** | Each entry: Claim is bounded (2 pts), Argument has mechanism + pattern (4 pts), Evidence is testable (4 pts). Vague Claims or Evidence of "plan to test" do not earn full marks |
| Assumption Register — ≥6 rows | **25** | Each row: Verification method is specific (2 pts), Fallback is realistic (1.5 pts), Metric is measurable (1.5 pts) |
| 3 analysis questions at the end | **10** | Answers include reasoning, not just yes/no |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-6.1.md](../solutions/sol-6.1.md)*
