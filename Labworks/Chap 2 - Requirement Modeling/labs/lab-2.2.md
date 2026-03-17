# Lab 2.2 — Requirements Modeling (3 Views)

> **Chapter 2 · Requirement Modeling**
> Input: Requirements Catalog from Lab 2.1 | Output: Requirements Models (.docx)

## Learning Objectives

- Practice **Scenario-based modeling**: draw a Use Case Diagram and write detailed Use Case Descriptions.
- Practice **Class-based modeling**: build a Domain Class Diagram with attributes, methods, and relationships.
- Practice **Behaviour-based modeling**: draw State Machine Diagrams for three entities with complex lifecycles.
- Understand why the three modeling views are **complementary** — each reveals aspects the others cannot.

---

## Context

Your Requirements Catalog from Lab 2.1 defines what the system must do. Lab 2.2 turns those requirements into three types of models, each answering a different question:

| Model Type | Question answered | Primary technique |
|-----------|-------------------|------------------|
| Scenario-based | *Who interacts with the system and how?* | Use Case Diagram + UC Descriptions |
| Class-based | *What data does the system manage?* | Domain Class Diagram |
| Behaviour-based | *How do key entities change over time?* | State Machine Diagrams |

**Deliverable:** Submit `Lab2.2_[TeamName]_Requirement_Models.docx`. You may use any modeling tool (Draw.io, PlantUML, StarUML, Visio, or even hand-drawn and photographed) — but diagrams must be legible and use correct UML notation.

---

## Task 1 — Scenario-Based Modeling

### 1a. Actor Analysis

Identify **all actors** that interact with CODING WAR — both **primary** (initiate use cases) and **secondary** (respond to or support the system).

For each actor:
- Describe their role
- List the use cases they participate in
- Clarify whether they are human or system actors

> [!NOTE]
> Not all actors are human. The **Judge Engine** that compiles and executes code is a secondary system actor — it receives requests from the system and returns results. The **Email Service** is another. Think carefully about what triggers what.

### 1b. Use Case Diagram

Draw a **complete Use Case Diagram** for the entire CODING WAR system.

Requirements:
- Include all use cases identified in your Requirements Catalog
- Show all actors (primary and secondary)
- Model relationships correctly: `«include»`, `«extend»`, and generalisation where appropriate
- Organise into packages or subsystems: Authentication, Problem Management, Submission & Judging, Contest

> [!TIP]
> `«include»` = a use case that is always part of the base (mandatory sub-flow). `«extend»` = a use case that conditionally extends the base (optional/exceptional flow). Do not overuse — only add these relationships where they genuinely improve clarity.

### 1c. Use Case Descriptions (at least 4)

Write a full Use Case Description for **each of the following 4 Use Cases**. You design your own template, but each description **must** include:

| Field | Required |
|-------|---------|
| UC ID | Yes |
| UC Name | Yes |
| Primary Actor | Yes |
| Secondary Actors | Yes (if any) |
| Description | One paragraph summary |
| Preconditions | Conditions that must be true before the UC begins |
| Postconditions (Success) | System state after successful completion |
| Main Flow | Numbered steps — at least 6 steps |
| Alternative Flows | At least 1 (use alphanumeric label: A1, A2...) |
| Exception Flows | At least 1 (use alphanumeric label: E1, E2...) |
| Business Rules | List the business rules that apply |

**The 4 required Use Cases:**

**UC-01: User Registration** *(Actor: Anonymous User)*
Consider: email verification flow, duplicate username handling, password constraints.

**UC-02: Submit Solution** *(Actor: Contestant — note the interaction with Judge Engine)*
Consider: the submission pipeline (queue → compile → run → result), real-time status updates, multiple verdict types, partial scoring.

**UC-03: Create Contest** *(Actor: Contest Organiser / Admin)*
Consider: Dry Run requirement, public vs private, freeze time configuration, Admin verification step.

**UC-04: Participate in Contest & View Scoreboard** *(Actor: Contestant)*
Consider: join activation timing, freeze scoreboard behaviour, restriction on viewing others' solutions during contest.

---

## Task 2 — Class-Based Modeling

Build a **Domain Class Diagram** for CODING WAR.

### Step 1: Identify Domain Classes

Extract the main entities from your Requirements Catalog. Each class must have:
- Class name
- Attributes (name + data type)
- Key operations/methods

> [!NOTE]
> From the Customer Brief and User Stories, you should identify at minimum: `User`, `Problem`, `Submission`, `TestCase`, `Contest`, `ContestParticipation`, `ScoreboardEntry`. A strong diagram needs **at least 8 classes**. Look carefully for entities that are implied but not explicitly named — for example, what stores the programming language whitelist?

### Step 2: Model Relationships

Draw all relationships between classes:
- **Association** (with multiplicity on both ends)
- **Aggregation** / **Composition** (be precise: is the child's existence dependent on the parent?)
- **Inheritance** (where a class hierarchy genuinely exists)

### Step 3: Data Constraints

Add constraint annotations to important attributes. At minimum document:
- Uniqueness constraints (e.g., username must be unique)
- Not-null fields
- Format constraints (e.g., email format validation)
- Value ranges (e.g., time_limit_ms between 100 and 10000)
- Foreign key relationships

---

## Task 3 — Behaviour-Based Modeling

Draw a **State Machine Diagram** for each of these three entities:

### 3a. Entity: Submission

Model the complete lifecycle of a code submission from creation to final result.

Required states to include: `Queued`, `Compiling`, `Running`, intermediate/final verdict states (`AC`, `WA`, `TLE`, `MLE`, `CE`, `RE`).

Each transition must show: trigger/event, guard condition (if any), and action (if any).

> [!WARNING]
> Note from the Customer Brief: *"Submission status updates sequentially: Queued → Compiling → Running → Result."* Your diagram must be consistent with this business rule. Additionally, `CE` is a terminal state reached during compilation — it must not be confused with runtime errors.

### 3b. Entity: Contest

Model the lifecycle of a contest from creation to completion.

Required states: `Draft`, `Pending Verification`, `Verified (Ready)`, `Running`, `Frozen` (scoreboard freeze), `Ended`.

Ensure your diagram captures: the Admin verification step, the automatic freeze at `freeze_time`, and the transition to `Ended` at `end_time`.

### 3c. Entity: User Account

Model the lifecycle of a user account from registration to possible deactivation.

Required states: `Registered (Unverified)`, `Active`, `Locked` (wrong password lockout), `Banned`, `Deactivated`.

Ensure your diagram captures: email verification, the temporary vs permanent lock distinction, and the difference between Admin-banned and user-deactivated.

> [!TIP]
> Each State Machine must have: an initial pseudo-state (black dot), at least one final state (circled black dot) for entities that have a lifecycle end, all transitions labelled with `trigger [guard] / action`.

---

## Discussion Questions

Before submitting, answer these questions in your document:

1. In the Use Case Diagram, `Submit Solution` uses `«include»` to link to the auto-judging process. Could this relationship be `«extend»` instead? Explain the semantic difference and justify which is correct.

2. In the Domain Class Diagram, what is the multiplicity between `Contest` and `Problem`? Is this an Association, Aggregation, or Composition? Justify your choice.

3. Looking at your State Machine for `Submission`: if a submission reaches the `CE` state, can it ever transition to any other state? What does this imply about how the system should handle resubmission?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Actor Analysis | **10** | All actors identified (including secondary/system actors); roles described accurately |
| Use Case Diagram | **15** | All use cases covered; `«include»`/`«extend»`/generalisation used correctly; packages/subsystems organised |
| Use Case Descriptions (4 UCs) | **25** | All required fields present; Main Flow ≥6 steps; at least 1 Alternative + 1 Exception flow each; Business Rules listed |
| Domain Class Diagram | **25** | ≥8 classes; multiplicity correct on all associations; data constraints annotated; correct relationship types |
| State Machine Diagrams (3) | **25** | All required states present; transitions have trigger/guard/action; initial and final states present; consistent with business rules |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-2.2.md](../solutions/sol-2.2.md)*
