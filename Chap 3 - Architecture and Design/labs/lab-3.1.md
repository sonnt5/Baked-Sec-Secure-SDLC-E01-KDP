# Lab 3.1 — Core Concept Analysis & Design Trade-offs

> **Chapter 3 · Software Architecture and Design**
> Input: SRS from Lab 2.3 | Output: Analysis table, ADR draft

## Learning Objectives

- Clearly distinguish between Requirement Modeling and Software Design.
- Apply and identify the 5 core design concepts — Abstraction & Refinement, Modularity, Information Hiding, Coupling & Cohesion, Separation of Concerns — in real-world scenarios.
- Analyze trade-offs in design decisions and draft an Architecture Decision Record (ADR).
- Link design decisions to requirements established in Chapter 2.

## Scenario

The CODING WAR development team has just received the completed SRS from Lab 2.3. Before beginning technical design, the team lead requires all members to conduct a *"design readiness review"* to: (1) confirm a clear boundary between **what** (requirements) and **how** (design), and (2) analyze several proposed preliminary design decisions.

---

## Task 1 — Distinguishing Requirements from Design Decisions

The following 10 statements about the CODING WAR system are mixed together. Classify each as a **Requirement (R)** or a **Design Decision (D)**, and provide a brief justification.

| # | Statement | Type (R/D) | Brief Justification |
|---|-----------|-----------|---------------------|
| 1 | The system must allow contestants to submit solutions written in C++, Java, or Python. | \[ R / D \] | \[Fill in\] |
| 2 | The judging service will use Docker containers to isolate the execution environment for each submission. | \[ R / D \] | \[Fill in\] |
| 3 | Judging results must be returned within 30 seconds of a successful submission. | \[ R / D \] | \[Fill in\] |
| 4 | SubmissionService and JudgeService will communicate via a message queue (RabbitMQ). | \[ R / D \] | \[Fill in\] |
| 5 | Admins must be able to create and manage programming problems in the system. | \[ R / D \] | \[Fill in\] |
| 6 | User data will be stored in PostgreSQL; session tokens will be stored in Redis. | \[ R / D \] | \[Fill in\] |
| 7 | The system must support at least 500 concurrent users during peak hours. | \[ R / D \] | \[Fill in\] |
| 8 | Authentication will be based on JWT with a 1-hour access token and a 7-day refresh token. | \[ R / D \] | \[Fill in\] |
| 9 | Contestants may only view the results of their own submissions, not those of others. | \[ R / D \] | \[Fill in\] |
| 10 | Test cases for each problem will be stored on S3-compatible object storage rather than in the database. | \[ R / D \] | \[Fill in\] |

---

## Task 2 — Identifying Violations of the 5 Core Concepts

The following 6 design descriptions contain problems taken from CODING WAR's initial draft. For each, **(a)** identify which core concept is violated, **(b)** explain why it is a violation, and **(c)** propose the correct design.

### Scenario A

`ContestController` receives an HTTP request → validates input → queries the database for the problem list → calculates ranking scores → sends a contest-end notification email → returns a JSON response. All logic resides in a single class.

| | |
|---|---|
| **Concept violated** | \[Fill in\] |
| **Explanation of violation** | \[Fill in\] |
| **Proposed correct design** | \[Fill in\] |

### Scenario B

`UserService` exposes the method `getUserByIdWithPasswordHashAndFailedAttempts()` so that other services can retrieve user information including the password hash whenever they need to check authentication.

| | |
|---|---|
| **Concept violated** | \[Fill in\] |
| **Explanation of violation** | \[Fill in\] |
| **Proposed correct design** | \[Fill in\] |

### Scenario C

The `Utils` module contains: `formatDate()`, `sendEmail()`, `calculateScore()`, `validateUsername()`, `compressFile()`, `generatePDF()`. All are grouped together because they are *"shared utility functions"*.

| | |
|---|---|
| **Concept violated** | \[Fill in\] |
| **Explanation of violation** | \[Fill in\] |
| **Proposed correct design** | \[Fill in\] |

### Scenario D

`JudgeService` directly reads the global variable `CONFIG.MAX_EXECUTION_TIME` instead of receiving this value through a constructor parameter or config injection.

| | |
|---|---|
| **Concept violated** | \[Fill in\] |
| **Explanation of violation** | \[Fill in\] |
| **Proposed correct design** | \[Fill in\] |

### Scenario E

`SubmissionService` directly instantiates a concrete implementation: `new PostgreSQLSubmissionRepository()` instead of depending on the `ISubmissionRepository` interface.

| | |
|---|---|
| **Concept violated** | \[Fill in\] |
| **Explanation of violation** | \[Fill in\] |
| **Proposed correct design** | \[Fill in\] |

### Scenario F

`ProblemService` handles: retrieving the problem list, validating submissions, auto-grading, and exporting statistics reports — all in one service, designed this way for *"convenience of management"*.

| | |
|---|---|
| **Concept violated** | \[Fill in\] |
| **Explanation of violation** | \[Fill in\] |
| **Proposed correct design** | \[Fill in\] |

---

## Task 3 — Drafting an Architecture Decision Record (ADR)

The development team is debating the following decision:

> *"Should the CODING WAR judging system be designed using a **Synchronous** architecture (contestant submits → waits for result returned immediately) or an **Asynchronous** architecture (contestant submits → receives a job_id → uses polling or WebSocket to receive the result)?"*

Write a complete ADR using the template below. Clearly demonstrate your understanding of the trade-offs involved.

| Field | Content |
|-------|---------|
| **ADR-001** | \[(Decision title)\] |
| **Date / Author** | \[Team fills in\] |
| **Context** | \[Describe the situation, constraints, and forces leading to this decision. Reference relevant NFRs from SRS Lab 2.3.\] |
| **Decision** | \[The chosen option and the rationale for selecting it.\] |
| **Positive Consequences** | \[List at least 3 benefits of the chosen decision.\] |
| **Negative Consequences / Trade-offs** | \[List at least 2 costs or accepted risks.\] |
| **Alternatives Considered** | \[Describe the rejected option and why it was ruled out.\] |
| **Review Trigger** | \[Under what conditions would this decision be reconsidered?\] |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Requirement vs. Design distinction (10 statements) | **30** | Each statement: correct classification (2 pts) + valid justification (1 pt) |
| Violation identification (6 scenarios) | **42** | Each scenario: correct concept identified (3 pts) + explanation (4 pts) |
| Complete, high-quality ADR | **28** | Clear context (8 pts), specific trade-offs (10 pts), well-reasoned rejected alternative (10 pts) |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-3.1.md](../solutions/sol-3.1.md)*
