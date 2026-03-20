# Lab 2.5 — Requirements Traceability Matrix (RTM)

> **Chapter 2 · Requirement Modeling**
> Input: SRS from Lab 2.3 + Business Drivers | Output: RTM (.xlsx) + Gap Analysis

## Learning Objectives

- Build an end-to-end **Requirements Traceability Matrix** linking Business Drivers → Business Requirements → Functional/Non-functional Requirements → Use Cases → Test Cases.
- Understand why traceability is critical in a **Secure SDLC**: it ensures no requirement is "lost" as the project moves from phase to phase.
- Perform **forward and backward traceability** gap analysis.
- Practice identifying orphan requirements and uncovered business goals.

---

## Context

Traceability answers two fundamental questions:

- **Forward:** *"For every business goal, is there a requirement that addresses it? And for every requirement, is there a test that verifies it?"*
- **Backward:** *"For every requirement, can we trace it back to a business need? For every test, is there a requirement it is testing?"*

A gap in either direction is a risk: a missing forward link means a business goal might not be built; a missing backward link means a requirement might be gold-plating (built with no business justification).

**Deliverable:** Submit `Lab2.5_[TeamName]_RTM.xlsx` — a multi-sheet Excel file with a structure you design yourself.

---

## Task 1 — Build the RTM

Using your SRS from Lab 2.3, build an RTM with at least the following sheets:

### Sheet 1: Business Drivers

List the four Business Drivers from the Customer Brief (BD-01 to BD-04) plus any additional ones you identified. For each BD:

| Field | Content |
|-------|---------|
| BD-ID | BD-01, BD-02... |
| Statement | Full description of the business driver |
| Priority | Critical / High / Medium |
| Owner | Which stakeholder "owns" this driver |

### Sheet 2: Business Rules

All 12+ Business Rules from SRS Section 7, with their BR-ID, statement, and related use case references.

### Sheet 3: Business Requirements

High-level business requirements (BRQ-01 to BRQ-xx) derived from the Business Drivers. These sit above the FR/NFR level — they describe *what the business needs*, not yet *how the system should behave*.

Example:
- `BRQ-01` links to `BD-01`: The organisation needs an automated code evaluation process that replaces manual grading.
- `BRQ-02` links to `BD-03`: The organisation must retain full ownership and control of all contest data and results.

### Sheet 4: Functional Requirements

All FRs from your SRS, each linked to:
- The BRQ it satisfies
- The Use Case(s) it relates to
- A test case ID (even if just a placeholder)

### Sheet 5: Non-functional Requirements

All NFRs from your SRS, each linked to:
- The BRQ it satisfies
- A test case ID

### Sheet 6: Traceability Matrix (Master)

The main RTM sheet — one row per requirement. Columns must include:

| Column | Description |
|--------|-------------|
| BD-ID | Business Driver(s) |
| BRQ-ID + Statement | Business Requirement |
| Priority | H/M/L |
| REQ-ID | FR or NFR ID |
| Requirement Type | FR / NFR / DR / IR |
| Statement | Requirement content (abbreviated) |
| UC-ID | Use Case(s) related |
| UC Name | |
| Status | Covered / Not Covered / Deferred |
| Test Case ID(s) | Mapping to test cases |
| Test levels | Columns for: ST (System Test), SIT, UAT, NFR Test |

**Minimum: 18 requirements fully mapped.**

---

## Task 2 — Write Preliminary Test Cases

For each FR and NFR in the RTM, write at least **one Test Case ID** and a brief description (1–2 sentences) of what that test will verify. This is not yet a detailed test case — just enough to prove the requirement is **testable**.

Example:

| REQ-ID | TC-ID | Test Case Description |
|--------|-------|-----------------------|
| REQ-FR-003 | TC-003 | Verify that submitting code in a language not on the whitelist returns HTTP 422 with error code `UNSUPPORTED_LANGUAGE`. |
| REQ-NFR-001 | TC-P-001 | Under simulated load of 500 concurrent users, verify that 95% of judging responses are returned within 30 seconds. |

---

## Task 3 — Gap Analysis

After completing the RTM, perform **4 types of gap analysis**. Document findings in a dedicated "Gap Analysis" sheet.

### 3a. Forward Gap
*Business Driver → Requirements coverage*

Is there any Business Driver (BD-01 to BD-04, plus your additions) that has no requirement in the RTM addressing it? If yes: list the BD, explain the gap, and propose which requirement(s) should be added.

### 3b. Backward Gap
*Requirements → Business Driver traceability*

Is there any requirement in the RTM that cannot be linked to any Business Driver? These are potential **orphan requirements** (gold-plating). List them and explain whether they should be: (a) removed, (b) linked to a BD if a link was missed, or (c) kept with explicit stakeholder justification.

### 3c. Test Coverage Gap
*Requirements → Test Cases*

Which requirements have no test case mapped? For 2 of these:
- Explain why it is difficult to test (if it is)
- Propose a concrete test approach that would make it testable
- If the requirement itself is untestable, rewrite it to make it so

### 3d. Feasibility Gap
*Requirements → Testability*

Are there any requirements where the acceptance criterion cannot realistically be verified? For example, "The system shall be available 99.99% uptime" — can this actually be tested within the project? Propose a more feasible version.

---

## Task 4 — Compare with the Sample RTM

Open `Coding_War_Traceability_Matrix.xlsx` (provided in Lab Materials). Analyse:

1. **Structure comparison:** How is the sample RTM structured compared to yours? List 3 structural differences and evaluate: which approach is more useful for a development team, and why?

2. **Coverage metric:** Look at the Status column in the sample. What percentage of requirements are "Covered"? What does that percentage tell you about the quality of the requirements set? Is a 100% coverage rate always desirable?

3. **What the sample has that yours does not (and vice versa):** Identify at least 2 elements present in the sample that your RTM is missing, and at least 1 element in your RTM that improves on the sample.

---

## Discussion Questions

**Q1:** A requirement is marked "Not Covered" in the RTM (no test case exists). A manager says: *"It's fine — we'll write tests for it later."* What is the risk of this approach? Use the **Boehm cost-of-defects** principle to explain why "later" is expensive.

**Q2:** You find a requirement in your RTM that cannot be linked to any Business Driver. The developer who wrote it says it's an important technical constraint. Is this a valid reason to keep the requirement? What is the correct process for handling an orphan requirement?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| RTM — completeness (≥18 requirements mapped) | **40** | All 6 sheets present; each requirement has all columns filled; professional formatting |
| Preliminary Test Cases | **15** | Each requirement has ≥1 TC ID + description; demonstrates the requirement is testable |
| Gap Analysis (4 types) | **25** | Each gap type clearly analysed; concrete proposals for resolution; not generic observations |
| Sample RTM comparison | **20** | Specific structural observations; coverage metric analysis; substantive improvements identified |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-2.5.md](../solutions/sol-2.5.md)*
