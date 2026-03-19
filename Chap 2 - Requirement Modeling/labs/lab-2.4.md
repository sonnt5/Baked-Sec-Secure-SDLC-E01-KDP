# Lab 2.4 — Requirements Quality Gate

> **Chapter 2 · Requirement Modeling**
> Input: SRS from another team (or sample) + Set of flawed requirements
> Output: Quality Review Report (.docx)

## Learning Objectives

- Build a reusable **Requirements Quality Gate Checklist** of your own.
- Act as a Requirements Reviewer: find and classify defects in a real SRS.
- Apply the **cost of defects** principle: understand why finding requirements errors early saves far more than finding them during testing.
- Detect, classify, and rewrite defective requirements to the correct standard.

---

## Context

> [!TIP]
> **The reviewer's mindset:** When reviewing requirements, you are not looking for things you disagree with — you are looking for requirements that cannot be implemented correctly, cannot be tested, contradict something else, or are missing essential information. Every finding should be specific and actionable.

**Deliverable:** Submit `Lab2.4_[TeamName]_Quality_Review_Report.docx`

---

## Defect Type Reference

Use these defect classifications throughout the lab:

| Type | Definition |
|------|-----------|
| **Ambiguous** | Can be interpreted in more than one way |
| **Non-testable** | Cannot write a test case that definitively passes or fails |
| **Incomplete** | Missing boundary conditions, error handling, actor, or constraint |
| **Contradictory** | Conflicts with another requirement or business rule |
| **Gold-plating** | Feature added without any stakeholder requesting it |
| **Mixed concerns** | Multiple distinct requirements bundled into one sentence |
| **Non-feasible** | Cannot be implemented given technical, time, or budget constraints |
| **Missing actor/subject** | Unclear who performs the action ("The system shall allow viewing reports" — who?) |

---

## Task 1 — Build a Quality Gate Checklist

Before reviewing any SRS, you need your own review tool. Build a **Requirements Quality Gate Checklist** with at least **15 items**, grouped by quality dimension:

**Clarity / Unambiguity**
- Is the requirement written so it can only be interpreted in one way?
- Does it avoid words like "fast", "easy", "many", "often", "normally"?
- Is every technical term defined in the Glossary?

**Completeness**
- Is there enough information to implement and test this requirement?
- Are boundary conditions specified (e.g., minimum/maximum values)?
- Is error handling described?

**Consistency**
- Does this requirement conflict with any other requirement?
- Is the same terminology used consistently throughout?

**Verifiability / Testability**
- Can you write a specific test case that passes or fails?
- Does it include a measurable criterion (time, quantity, percentage)?

**Feasibility**
- Is this achievable given the project constraints (team size, timeline, budget)?

**Traceability**
- Can this requirement be linked to a business goal or stakeholder need?
- Does it have a unique, stable ID?

**Atomicity (Single Concern)**
- Does this requirement address exactly one thing?
- Are "and", "or", "also" signals of mixed concerns?

**Correct Actor / Subject**
- Is it clear who performs the action or who benefits from it?
- Is the subject explicit ("The system shall..." not "shall...")?

> [!NOTE]
> This checklist will be reused in every subsequent chapter when reviewing architecture decisions, code, and security controls. Build it to be genuinely useful — not just a homework submission.

---

## Task 2 — Peer SRS Review

Receive the SRS of another team (or use the sample `CODING_WAR_SRS.docx` if no peer SRS is available). Conduct a thorough review and write a **Review Report** with these sections:

### 2a. Executive Summary

- Total defects found
- Distribution by severity: Critical / Major / Minor / Cosmetic
- Distribution by defect type
- Overall quality assessment (1 paragraph)

### 2b. Detailed Findings

For each defect found, document:

| Field | Description |
|-------|-------------|
| **Finding ID** | RF-001, RF-002... |
| **REQ ID** | Which requirement has the defect |
| **Defect Type** | From the classification table above |
| **Description** | Explain specifically why this is a defect (not just "it's ambiguous") |
| **Severity** | Critical / Major / Minor / Cosmetic |
| **Proposed Fix** | Write the corrected version of the requirement |

> [!TIP]
> **Critical** = blocks implementation or testing; will cause the wrong system to be built. **Major** = significant risk if not fixed before development. **Minor** = reduces clarity or introduces small risk. **Cosmetic** = formatting, spelling, style.

### 2c. Structural Review

Evaluate the SRS structure:
- Are all required sections present?
- Are diagrams correct and legible?
- Are cross-references consistent (e.g., use cases referenced in Section 3 exist in Appendix A)?
- Is terminology used consistently throughout?

### 2d. Coverage Review

Compare the SRS to the Customer Brief:
- Are any features from the Customer Brief missing from the SRS?
- Are any requirements present in the SRS that cannot be traced to the Customer Brief or User Stories? (potential gold-plating)

### 2e. Top 5 Recommendations

List the five most important issues to fix, in priority order, with a short rationale for each.

---

## Task 3 — Detect and Fix Flawed Requirements

The following 10 requirements were written by a junior analyst for an **online banking system** (different from CODING WAR). Each contains **at least one defect**. Your task: identify the defect(s), classify them, explain why they are defects, and write a corrected version.

| REQ ID | Original Requirement |
|--------|---------------------|
| **REQ-01** | The system must be fast. |
| **REQ-02** | Users can view their account balance. |
| **REQ-03** | The system interface must be attractive, modern, and user-friendly. |
| **REQ-04** | Admin can view and delete any customer's transactions at any time. |
| **REQ-05** | The application must be user-friendly and easy to use. |
| **REQ-06** | The system must be able to handle many transactions simultaneously. |
| **REQ-07** | The system must automatically send an email notification and simultaneously log the event whenever a new transaction occurs. |
| **REQ-08** | The system must log all transactions and retain logs permanently. |
| **REQ-09** | If a transfer transaction fails, the system may automatically retry or notify the user. |
| **REQ-10** | The system must comply with current software quality standards. |

For each requirement, create a table row with:

| REQ ID | Defect Type(s) | Why it is a defect | Corrected Version |
|--------|--------------|-------------------|-----------------|
| REQ-01 | Non-testable | "Fast" has no measurable criterion — there is no test that could pass or fail. A test team cannot determine compliance. | `[REQ-01] [High]` The system shall process any financial transaction and return a confirmation response within 3 seconds under normal load (≤200 concurrent users). |
| REQ-02 | | | |
| REQ-03 | | | |
| ... | | | |

---

## Discussion Questions

Answer these three questions in your report:

**Q1:** Among the 10 requirements above, which defect type would cause the highest cost if discovered during the testing phase (rather than the requirements phase)? Explain using **Boehm's cost-of-defect curve** (the principle that fixing a defect becomes 10–100× more expensive with each phase it survives).

**Q2:** REQ-04 says "Admin can delete transactions." Analyse whether this is a valid business requirement for a banking system. Explain the difference between *deleting* a transaction and *cancelling / marking it as invalid*. How does this relate to the **Audit Trail** principle in security (the requirement that all financial actions must be traceable and non-repudiable)?

**Q3:** If you were the test engineer responsible for this banking system, which requirement would be hardest to write a test case for? Rewrite that requirement in a form that is testable, then write 2 specific test cases for it (test case title + expected result — you do not need detailed test steps yet).

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Quality Gate Checklist (≥15 items) | **15** | Covers all quality dimensions; items are actionable; could be used in a real project |
| SRS Review Report | **35** | ≥5 defects with severity + type + proposed fix; structural review has substance; coverage review identifies real gaps |
| Detect and fix defects (10 REQs) | **30** | Each REQ: correct defect type (2 pts) + explanation (1 pt) = 3 pts/req. Corrected versions must be specific and testable. |
| Discussion questions (3 questions) | **20** | Q1: references Boehm's curve with concrete reasoning. Q2: correctly distinguishes delete vs cancel and links to Audit Trail. Q3: 2 concrete test cases. |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-2.4.md](../solutions/sol-2.4.md)*
