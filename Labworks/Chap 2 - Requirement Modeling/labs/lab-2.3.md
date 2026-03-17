# Lab 2.3 — Writing the Software Requirements Specification (SRS)

> **Chapter 2 · Requirement Modeling**
> Input: Requirements Catalog (Lab 2.1) + Requirements Models (Lab 2.2)
> Output: SRS Document (.docx)

## Learning Objectives

- Synthesise Lab 2.1 and Lab 2.2 outputs into a **complete, professional SRS document**.
- Follow the IEEE 830 / IEEE 29148 structure.
- Ensure requirements meet the quality criteria: Clear, Complete, Consistent, Feasible, Verifiable.
- Practice writing System Features: description, stimulus/response, and requirement list.
- Write Non-functional Requirements with measurable acceptance criteria.

---

## Context

> [!NOTE]
> **This is the most important deliverable in Chapter 2.** The SRS you produce here will be used as input for every subsequent chapter: Chapter 3 (Secure Design), Chapter 4 (Threat Modeling), Chapter 5 (Security Patterns), Chapter 6 (Security Design Review), Chapter 7 (Secure Coding), and Chapter 8 (Security Testing). A weak SRS will cause compounding problems throughout the entire course. Invest the time to get it right.

**Deliverable:** Submit `Lab2.3_[TeamName]_CODING_WAR_SRS.docx` — a complete, professional SRS document that could realistically be handed to a development team.

---

## Required SRS Structure

You must include **all** sections below. You design the layout, formatting, and depth of content yourself.

| Section | Title | Required Content |
|---------|-------|-----------------|
| **1** | Introduction | 1.1 Purpose · 1.2 Document Conventions · 1.3 Intended Audience · 1.4 Product Scope · 1.5 References |
| **2** | Overall Description | 2.1 Product Perspective (context diagram) · 2.2 Product Functions (summary) · 2.3 User Classes & Characteristics · 2.4 Operating Environment · 2.5 Constraints · 2.6 Assumptions |
| **3** | System Features | ≥5 features, each with: 3.x.1 Description & Priority · 3.x.2 Stimulus/Response Sequences · 3.x.3 Functional Requirements (REQ-FR-xxx) with ≥3 FRs per feature |
| **4** | Non-functional Requirements | 4.1 Performance · 4.2 Security · 4.3 Availability · 4.4 Scalability · 4.5 Reliability · 4.6 Usability |
| **5** | Data Requirements | 5.1 Logical Data Model (Class Diagram from Lab 2.2) · 5.2 Data Dictionary · 5.3 Data Quality Rules |
| **6** | Interface Requirements | 6.1 User Interfaces · 6.2 Software/System Interfaces (Judge Engine, Email Service) · 6.3 Communication Interfaces |
| **7** | Business Rules | Table: BR-ID · Statement · Related Use Case(s). **Minimum 12 business rules.** |
| **App. A** | Use Case Diagrams | All diagrams from Lab 2.2 |
| **App. B** | State Machine Diagrams | All state machines from Lab 2.2 |
| **App. C** | Glossary | Definitions of all domain-specific terms |
| **App. D** | Revision History | Document change log |

---

## Requirement Quality Standards

Every requirement in the SRS must meet these standards:

**Format:**
```
[REQ-FR-008] [High] The system shall only permit code submissions in languages 
contained in the Admin-configured language whitelist.

Acceptance Criteria: 
  - Submitting Python 3, C++, or Java code returns HTTP 200 when the 
    whitelist contains those languages.
  - Submitting code in any other language returns HTTP 422 with error 
    code UNSUPPORTED_LANGUAGE.
  - Changing the whitelist takes effect on the next submission attempt 
    (no caching delay).
```

**Rules to follow for every requirement:**
1. One requirement = one concern. Never use "and" to chain two requirements into one sentence.
2. No vague words. Replace: "fast" → specific latency. "many users" → specific concurrent user count. "user-friendly" → specific usability metric.
3. Requirements with High or Critical priority must have measurable Acceptance Criteria.
4. Every FR must be testable — you must be able to write a test case that either passes or fails.
5. Subject must be explicit: "The system shall..." not "It shall..."

---

## Task 1 — Write Section 3: System Features

This is the core of the SRS. Structure your functional requirements into at least **5 System Features** drawn from your Requirements Catalog:

Suggested features (you may reorganise, merge, or split):
- **Feature 3.1: User Registration and Authentication** — account creation, email verification, login, password reset, session management
- **Feature 3.2: Problem Management** — problem authoring, test case management, Draft/Public lifecycle, Admin approval
- **Feature 3.3: Code Submission and Auto Judging** — submission pipeline, verdict types, real-time status, partial scoring, sandbox isolation
- **Feature 3.4: Contest Management** — contest creation, public/private access, Dry Run, scoreboard freeze, Admin verification
- **Feature 3.5: User Profile and Rankings** — profile management, submission history, global ranking, contest performance history

For each feature, use the **Stimulus/Response** format:
- **Stimulus:** What triggers this feature? (e.g., user submits a form, contest start time is reached, system timer fires)
- **Response:** What must the system do in response?

Include the **Use Case Description** references from Lab 2.2 in the appropriate feature sections.

---

## Task 2 — Write Section 4: Non-functional Requirements

Each NFR must include:
- A unique ID: `REQ-NFR-xxx`
- A category: Performance / Security / Availability / Scalability / Reliability / Usability
- A statement: *"The system shall..."*
- A **measurable Acceptance Criterion** — no vague assertions

**Examples of strong vs weak NFRs:**

| Weak (do not write like this) | Strong (required standard) |
|------------------------------|---------------------------|
| The system must be fast. | `[REQ-NFR-001] [High]` The system shall return judging results within 30 seconds of a successful submission for 95% of submissions under normal load (≤500 concurrent users). |
| Passwords must be secure. | `[REQ-NFR-005] [Critical]` The system shall store all passwords using Argon2id with a minimum memory cost of 64 MB; passwords shall never be stored in plaintext or reversibly encrypted form. |
| The system must be available. | `[REQ-NFR-008] [High]` The system shall maintain 99.5% uptime measured monthly, excluding scheduled maintenance windows (maximum 4 hours per month). |

**Minimum NFR coverage** — ensure you address each group:
- Performance: response time, throughput, concurrent users
- Security: authentication strength, password storage, sandbox isolation, encryption in transit
- Availability: uptime SLA, backup frequency and retention
- Scalability: ability to handle peak contest load
- Reliability: automatic retry, graceful degradation on judging failure

---

## Task 3 — Write Section 7: Business Rules

Business Rules define constraints and policies that requirements must respect. They are not requirements themselves but they govern how requirements are implemented.

Format for each rule:
```
BR-01: A problem must have at least one test case before it can be transitioned from Draft to Public status.
Related Use Cases: UC-02 (Create Problem), UC-03 (Publish Problem)

BR-02: Only Admin may transition a problem from Draft to Public status.
Related Use Cases: UC-03 (Publish Problem)
```

Write **at least 12 business rules** covering:
- User account management (registration, locking, banning)
- Problem lifecycle (Draft/Public states, test case requirement)
- Submission and judging (language whitelist, verdicts, partial scoring)
- Contest management (Dry Run requirement, freeze time behaviour, private vs public access)
- Sandbox constraints (what code may and may not do)

---

## Task 4 — Consistency Check

Before submitting, verify your SRS passes this internal consistency check:

| Check | What to verify |
|-------|---------------|
| **Cross-reference** | Every Use Case referenced in Section 3 appears in Appendix A |
| **Traceability** | Every FR can be traced back to at least one requirement in the Master Catalog (Lab 2.1) |
| **No contradictions** | No two requirements in Section 3 and 4 contradict each other |
| **Terminology** | The Glossary (App. C) defines every domain term used in the document |
| **Diagrams** | Class Diagram in Section 5 and State Machines in App. B are consistent with the data entities described in Section 3 |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| SRS Structure (7 sections + appendices) | **15** | All sections present, professional formatting, Table of Contents |
| System Features + Use Cases (Section 3) | **30** | ≥5 features; each with ≥3 FRs in standard format; priority assigned; Acceptance Criteria for High/Critical; UC descriptions integrated |
| Non-functional Requirements (Section 4) | **15** | Covers all required groups; each NFR has a measurable Acceptance Criterion; no vague language |
| Data Requirements + Business Rules (Sections 5 & 7) | **15** | Data Dictionary complete; ≥12 Business Rules linked to Use Cases |
| Diagrams integrated from Lab 2.2 | **15** | UC, Class, State Machine diagrams placed correctly with captions and cross-references |
| Overall quality | **10** | Consistent terminology; no contradictions; cross-references intact; professional document |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-2.3.md](../solutions/sol-2.3.md)*
