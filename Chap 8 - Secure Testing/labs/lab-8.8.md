# Lab 8.8 — Penetration Testing: Scoping & Findings

> **Chapter 8 · Security Testing Strategy and Toolchain Integration**
> Input: CODING WAR staging environment
> Output: Rules of Engagement + Pentest Findings Report + Bug Bar Integration

> [!WARNING]
> All testing must target the **staging** environment with synthetic data only. Written authorization is required before any testing begins. Never test against production.

## Learning Objectives

- Write a Rules of Engagement document that bounds the test scope clearly enough to prevent accidents.
- Conduct targeted exploitation verification against CODING WAR's highest-risk areas.
- Write pentest findings that are reproducible by someone who was not present.
- Map findings to the Bug Bar and make a release readiness recommendation.

---

## Task 1 — Rules of Engagement Document

Write the RoE document for this pentest. It must be specific enough that an engineer reading it six months later can understand exactly what was and was not tested, and why.

The RoE must define: who authorised the test and what system it covers, the exact in-scope and out-of-scope targets (be specific — naming `/admin/*` as out-of-scope is not sufficient; explain what the risk of scanning it is), which testing methods are permitted and which are not, the emergency stop procedure if testing causes unexpected system behaviour, and how findings are handled and reported.

A weak RoE says "the admin console is out of scope." A strong RoE says "the admin console is excluded from ZAP active scanning because automated injection testing would corrupt contest data and because it requires MFA that ZAP cannot automate; it will be tested manually in a separate session."

---

## Task 2 — Targeted Pentest Execution

Focus on the highest-risk areas from your Coverage Matrix (Lab 8.1). For each target, document your approach, what you attempted, the result, and what the result means for the risk.

**Target 1: Judge Sandbox Isolation (TH-03)**
The judge sandbox is CODING WAR's highest-risk component — it executes arbitrary user code. Test the sandbox boundaries by submitting code that attempts to escape containment. Document each attempt and result carefully. A clean result (no escape) is positive evidence, not a null result.

**Target 2: Authentication Chain (VC-01 from Lab 7.1)**
The vulnerability chain from Lab 7.1 identified steps from user enumeration to account takeover. Test whether each step of the chain is actually blocked. If any step succeeds, document it as a finding even if the full chain requires other conditions.

**Target 3: Admin Access Controls (TH-05)**
Test the MFA enforcement on admin endpoints by attempting access with various token configurations. Document what each configuration produces and what that means for Code Contract CI-03.

For any additional high-risk areas you identify from your Coverage Matrix, test those as well.

---

## Task 3 — Findings Report

Write a professional pentest finding for each issue you discover. For each finding:

- **Title** — concise and descriptive
- **CVSS Score and Vector** — justify the score, not just state it
- **Description** — what was found and what it means in CODING WAR's context
- **Reproduction steps** — specific enough that another engineer can reproduce it without asking you any questions
- **Evidence** — the actual request/response, screenshot description, or test output
- **Business impact** — what an attacker could achieve, in non-technical terms
- **Recommended fix** — specific enough to implement without follow-up questions
- **References** — relevant CWE, ASVS control, or Lab 7.x finding

If the sandbox isolation test produces no escape (no vulnerability found), document this as a positive finding — evidence that the control works is also a finding.

Write at least three findings total.

---

## Task 4 — Bug Bar Integration and Release Readiness

Map each finding to the Bug Bar from your Security Test Plan (Lab 8.1). For each finding, state whether it blocks release and the criteria for that decision.

Then write a release readiness statement: given all findings from this pentest, would you recommend proceeding to production release? Your statement must be specific — name the findings, state what conditions would need to be met, and explain the residual risk if release proceeds with any open findings.

---

## Discussion

1. Your pentest finds that user enumeration is possible (different error messages for valid vs invalid emails). This was already identified as a bug in Lab 7.5. Should this be a new pentest finding? What does its presence tell you about the Lab 7.5 fix?

2. The sandbox isolation test shows no escape in 30 minutes of manual testing. Can you conclude the sandbox is secure? What would increase your confidence in that conclusion?

3. A junior developer says: "We have unit tests for all our security controls, so we don't need a pentest." What is the specific class of vulnerability that unit tests cannot detect and that a pentest can?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Rules of Engagement | **20** | In-scope and out-of-scope specific and justified; emergency stop defined; testing methods bounded |
| Pentest execution (3 targets) | **30** | Each target tested systematically; results documented regardless of pass/fail; clean results documented as positive evidence |
| Findings report (3+ findings) | **35** | Each finding: CVSS score justified; reproduction steps specific; evidence included; recommended fix actionable |
| Bug Bar integration + release readiness | **15** | Findings mapped to Coverage Matrix; release statement is specific and substantive |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-8.8.md](../solutions/sol-8.8.md) after completing the lab.*
