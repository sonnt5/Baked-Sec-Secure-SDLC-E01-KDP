# Lab 3.2 — Five Views: Architectural Design & Data Design

> **Chapter 3 · Software Architecture and Design**
> Input: SRS from Lab 2.3 | Output: Component diagram, ER diagram

## Learning Objectives

- Build an Architectural View: identify functional areas, choose an architectural style, define components and connectors.
- Build a Data View: design an ER diagram/data model, identify entities, attributes, relationships, and data constraints.
- Trace from Requirements (SRS Lab 2.3) to design elements using a Requirement-to-Design matrix.
- Understand how architectural choices impact coupling and cohesion within each component.

## Scenario

Following Lab 3.1 (which identified trade-offs and an ADR for the judging mechanism), the team moves into actual design. This lab focuses on two of the five views: **Architectural** and **Data**. These form the foundation on which the remaining views (Interface, Component, Deployment) will be built.

> [!NOTE]
> **Reminder:** Use the SRS from Lab 2.3 as the primary input. Pay particular attention to: Functional Requirements (FRs) that define each component's scope, Non-Functional Requirements (NFRs) that influence the architectural style, and Data Requirements (DRs) that form the basis for the Data View.

---

## Task 1 — Architectural Design

### Step 1: Identify Functional Areas

Group the FRs and UCs from SRS Lab 2.3 into natural functional areas. Complete the table below:

| Functional Area | Related FR / UC (from SRS) | Component Responsibility Description |
|----------------|---------------------------|--------------------------------------|
| **Authentication & User Management** | \[Fill in related FR, UC\] | \[Description\] |
| **Problem Management** | \[Fill in\] | \[Description\] |
| **Contest Management** | \[Fill in\] | \[Description\] |
| **Submission & Judging** | \[Fill in\] | \[Description\] |
| **Scoreboard & Reporting** | \[Fill in\] | \[Description\] |
| \[Add if needed\] | \[Fill in\] | \[Fill in\] |

### Step 2: Select an Architectural Style

Based on the identified NFRs and functional areas, choose the most appropriate architectural style for CODING WAR. Rate each option (`+` = good, `~` = neutral, `−` = poor):

| Evaluation Criterion | Monolith | Modular Monolith | Microservices | N-tier |
|----------------------|----------|-----------------|--------------|--------|
| Meets concurrent user NFR | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] |
| Easy initial deployment | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] |
| Independent service scaling | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] |
| Suitable for current team size | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] |
| Operational complexity | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] |
| Attack surface | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] | \[+/~/−\] |
| **✅ SELECTED STYLE** | \[ \] | \[ \] | \[ \] | \[ \] |

### Step 3: Draw a Component/Architecture Diagram

Based on the identified functional areas and chosen style, draw a Component Diagram (UML) or Architecture Diagram that clearly shows:
- (a) The main components/subsystems
- (b) Connectors and communication style (sync/async)
- (c) System boundaries with external actors/systems

> 📎 Insert diagram here (image file or link to Mermaid/draw.io/PlantUML/Lucidchart)
>
> Suggested tools: draw.io · PlantUML · Lucidchart · Mermaid.js

### Step 4: Requirement-to-Architecture Traceability Matrix

Complete the matrix below to ensure every important FR and NFR is covered by at least one component (✓):

| REQ ID | Summary | Auth Svc | Problem Svc | Contest Svc | Judge Svc | Scoreboard |
|--------|---------|----------|-------------|-------------|-----------|-----------|
| **FR-01** | User registration / login | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |
| **FR-0X** | Create / manage problems | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |
| **FR-0X** | Submit a solution | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |
| **FR-0X** | Create / manage contests | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |
| **FR-0X** | View scoreboard | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |
| **NFR-01** | 500 concurrent users | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |
| **NFR-0X** | Judging response ≤ 30s | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |

---

## Task 2 — Data Design

Design the Data View for CODING WAR based on the Data Requirements (DRs) from SRS Lab 2.3 and the Domain Class Diagram from Lab 2.2.

### Step 1: Identify Key Entities and Attributes

| Entity | Key Attributes | PK / FK | Data Constraints |
|--------|---------------|---------|-----------------|
| **User** | id, username, email, password_hash, role, created_at | PK: id | username UNIQUE, NOT NULL, 3–30 chars; email UNIQUE, valid format |
| **Problem** | id, title, description, difficulty, time_limit_ms, memory_limit_mb, created_by | PK: id, FK: created_by → User | title NOT NULL; time_limit 100–10000ms |
| **Submission** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **Contest** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **ContestProblem** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TestCase** | \[Fill in\] | \[Fill in\] | \[Fill in\] |

### Step 2: Draw an ER Diagram

Show: entities, key attributes, relationships (1:1, 1:N, N:M), cardinality, and important constraints.

> 📎 Insert ER Diagram here

### Step 3: Data Architecture Decisions

**Q1:** What type of database will the system use (relational, document, key-value)? Explain why.

> \[Team's answer\]

**Q2:** What data should be cached in Redis? Why? What caching strategy will be used?

> \[Team's answer\]

**Q3:** Should problem test cases be stored in the same database as problem metadata? Explain.

> \[Team's answer\]

**Q4:** If a Submission is deleted (if permitted), how should related records (TestResult) be handled? (CASCADE / RESTRICT / SET NULL)

> \[Team's answer\]

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Architectural Design — Component Diagram | **30** | Sufficient components, clear boundaries, logical connectors, external boundaries present |
| Architectural Style Selection — Justification | **15** | Complete comparison table, chosen style is well-reasoned and linked to NFRs |
| Requirement-to-Architecture Traceability | **15** | All FRs/NFRs have at least one responsible component; no orphaned requirements |
| Data Design — Entity Table + Constraints | **20** | ≥5 entities, correct PK/FK, specific and measurable data constraints |
| ER Diagram | **20** | Correct relationship types, clear cardinality, N:M relationships shown where applicable |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-3.2.md](../solutions/sol-3.2.md)*
