# Lab 3.6 — Design Quality Review & Design Review Report

> **Chapter 3 · Software Architecture and Design**
> Input: Full design from Lab 3.1–3.5 | Output: Design Review Report with checklist

## Learning Objectives

- Evaluate design quality against Quality Attributes: Maintainability, Testability, Scalability, and Security.
- Practice the role of Design Reviewer: use a checklist to discover design issues.
- Write a complete Design Review Report following the Software Design Review (SDR) standard.
- Propose specific action items to improve the design based on review findings.
- Understand the link between Design Review and quality gates (SDR → Bug Bar → FSR) in the Secure SDLC.

## Scenario

After 4 design labs (3.1–3.5), the team has a complete set of design artifacts: Architecture Diagram, ER Diagram, API Specs, Class Diagram, Deployment Diagram, ADRs, and Pattern Map. The final step of Chapter 3 is to conduct a **Software Design Review (SDR)** session to assess overall design quality and plan improvements before moving into implementation.

> [!NOTE]
> **Note:** Lab 3.6 is a **synthesis exercise** — teams perform cross-reviews: one team reviews another team's design. If working individually, self-assess and compare against the Reference Solution in the `assets/` folder.

---

## Task 1 — Design Quality Rubric Assessment

Evaluate the CODING WAR design against a 4-attribute Quality Rubric. Each attribute is scored on a scale of **1–4** with specific evidence:

> **Scale:** 1 = Poor (clear violations) · 2 = Fair (significant issues) · 3 = Good (meets expectations) · 4 = Excellent (exceeds expectations, follows best practices)

### 1. Maintainability

| Criterion | Score (1–4) | Evidence / Specific Comments |
|-----------|------------|------------------------------|
| Are module boundaries clear? Does each component follow SRP? | \[ \] | \[Fill in evidence from design artifacts\] |
| Does the design allow unit testing of components in isolation? | \[ \] | \[Fill in evidence\] |
| Does the architecture support horizontal scaling of critical components? | \[ \] | \[Fill in evidence\] |
| Are there violations of the Law of Demeter / inappropriate intimacy? | \[ \] | \[Fill in evidence\] |
| **Maintainability Total** | **\[ /16\]** | \[Overall comments\] |

### 2. Testability

| Criterion | Score (1–4) | Evidence / Specific Comments |
|-----------|------------|------------------------------|
| Are there anti-patterns such as God Class or Circular Dependency? | \[ \] | \[Fill in evidence\] |
| Are interfaces stable and easy to mock/stub? | \[ \] | \[Fill in evidence\] |
| Is the data layer separated enough to scale independently? | \[ \] | \[Fill in evidence\] |
| What is the level of coupling between modules? | \[ \] | \[Fill in evidence\] |
| **Testability Total** | **\[ /16\]** | \[Overall comments\] |

### 3. Scalability

| Criterion | Score (1–4) | Evidence / Specific Comments |
|-----------|------------|------------------------------|
| Do ADRs document the rationale and trade-offs? | \[ \] | \[Fill in evidence\] |
| Is test data easy to set up (isolated DB, fixtures)? | \[ \] | \[Fill in evidence\] |
| Have SPOFs been addressed? | \[ \] | \[Fill in evidence\] |
| What is the level of cohesion within each module? | \[ \] | \[Fill in evidence\] |
| **Scalability Total** | **\[ /16\]** | \[Overall comments\] |

### 4. Modularity & Separation of Concerns

| Criterion | Score (1–4) | Evidence / Specific Comments |
|-----------|------------|------------------------------|
| \[Sub-criterion 1\] | \[ \] | \[Fill in evidence\] |
| \[Sub-criterion 2\] | \[ \] | \[Fill in evidence\] |
| \[Sub-criterion 3\] | \[ \] | \[Fill in evidence\] |
| **Modularity & SoC Total** | **\[ /12\]** | \[Overall comments\] |

---

## Task 2 — Design Review Checklist

Complete the consistency checklist across all design views:

| # | Check Question | ✓ / ✗ / N/A | Notes / Evidence |
|---|---------------|------------|-----------------|
| 1 | Every FR in SRS Lab 2.3 is mapped to at least one component in the Architecture Diagram? | \[ \] | \[Fill in\] |
| 2 | Every entity in the ER Diagram has a clear "owner" component in the Architecture? | \[ \] | \[Fill in\] |
| 3 | API contracts (Lab 3.3) are consistent with the ER Data Model (Lab 3.2) — field names and data types match? | \[ \] | \[Fill in\] |
| 4 | Deployment Diagram (Lab 3.4) covers all components in the Architecture Diagram (Lab 3.2)? | \[ \] | \[Fill in\] |
| 5 | No circular dependencies between components? | \[ \] | \[Fill in\] |
| 6 | Each component has a Single Responsibility — no "God Component"? | \[ \] | \[Fill in\] |
| 7 | Component interfaces are sufficient to implement without knowing internals? | \[ \] | \[Fill in\] |
| 8 | ADRs document key architectural decisions with context and trade-offs? | \[ \] | \[Fill in\] |
| 9 | No security anti-patterns: SQL injection risk, insecure direct object reference, missing auth checks on APIs? | \[ \] | \[Fill in\] |
| 10 | The design can scale to meet the concurrent user NFR? | \[ \] | \[Fill in\] |
| 11 | Pattern Application Map (Lab 3.5) is consistent with the actual design artifacts? | \[ \] | \[Fill in\] |
| 12 | Pseudocode (Lab 3.3) covers both the happy path and all error paths? | \[ \] | \[Fill in\] |

---

## Task 3 — Design Review Report (SDR)

Write a complete Design Review Report using the template below. This is the formal artifact for the **Software Design Review (SDR)** gate in the Secure SDLC:

| Section | Content |
|---------|---------|
| **System Name / Version** | CODING WAR v\[X.Y\] — Design Review Report |
| **Review Date** | \[Fill in date\] |
| **Reviewer(s)** | \[Team members acting as reviewers\] |
| **Design Artifacts Reviewed** | Architecture Diagram (Lab 3.2), ER Diagram (Lab 3.2), API Specs (Lab 3.3), Class Diagram (Lab 3.3), Deployment Diagram (Lab 3.4), ADRs, Pattern Map (Lab 3.5) |
| **Executive Summary** | \[2–3 sentences summarizing overall design quality: key strengths, key weaknesses, and verdict\] |
| **Quality Rubric Totals** | Maintainability: \[X/16\] · Testability: \[X/16\] · Scalability: \[X/16\] · Modularity: \[X/12\] · Total: \[X/60\] |
| **Critical Issues** *(must fix before implementation)* | \[List the most important issues. Each issue: ID, description, affected component, severity\] |
| **Major Issues** *(should fix soon)* | \[Issues that are significant but do not block implementation\] |
| **Minor Issues** *(improve later)* | \[Small issues, technical debt\] |
| **Design Strengths** | \[List good design decisions that can serve as reference patterns for the team\] |
| **Verdict** | \[ \] APPROVED · \[ \] APPROVED WITH CONDITIONS · \[ \] REJECTED (redesign required) |
| **Conditions for Approval** *(if not yet approved)* | \[List what the team must fix or add before the design is approved\] |

---

## Task 4 — Action Items & Traceability Closure

Based on the Design Review Report, create an Action Items table:

| ID | Required Change | Severity | Affected Artifact | Responsible | Deadline |
|----|----------------|----------|------------------|-------------|---------|
| AI-01 | \[Fill in required change\] | Critical / Major / Minor | \[Affected artifact\] | \[Name\] | \[Date\] |
| AI-02 | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| AI-03 | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Quality Rubric Assessment (4 attributes) | **28** | Each attribute: reasonable score (4 pts) + specific evidence from artifacts (3 pts) = 7 pts/attribute |
| Design Review Checklist (12 items) | **24** | Each item: correct ✓/✗/N/A (1 pt) + note with evidence (1 pt) |
| Design Review Report (SDR) | **30** | Clear executive summary (5 pts), issues correctly classified by severity (10 pts), justified verdict (5 pts), strengths identified (5 pts), approval conditions (5 pts) |
| Action Items | **18** | ≥3 action items, correct severity, specific affected artifact, deadline present |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-3.6.md](../solutions/sol-3.6.md)*
