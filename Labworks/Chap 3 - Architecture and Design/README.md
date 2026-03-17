# Chapter 3 — Software Architecture and Design

> **Bake Security into Modern Software Development**
> Case study system: **CODING WAR** — Online Judge System

## Chapter Objectives

Chapter 3 focuses on software design — the transition from *"what the system must do"* (requirements) to *"how the system will be built"* (architecture & design). Students will practice core concepts: abstraction, modularity, information hiding, coupling/cohesion, separation of concerns; design using the Five Views framework; selecting and evaluating design patterns; and assessing design quality.

## Lab Roadmap

| Lab | Topic | Learning Objectives | Input | Main Output |
|-----|-------|---------------------|-------|-------------|
| [3.1](labs/lab-3.1.md) | Concept Review & Trade-offs | Analyze 5 core concepts and design trade-offs | Descriptive scenarios | Analysis table, ADR draft |
| [3.2](labs/lab-3.2.md) | Five Views — Architecture & Data | Design Architectural View and Data View | SRS from Lab 2.3 | Component diagram, ER diagram |
| [3.3](labs/lab-3.3.md) | Five Views — Interface & Component | Design Interface and Component View | Output from Lab 3.2 | API specs, Class diagram |
| [3.4](labs/lab-3.4.md) | Deployment Design | Design Deployment View and select architecture pattern | Output from Lab 3.2 + 3.3 | Deployment diagram, ADR |
| [3.5](labs/lab-3.5.md) | Design Patterns | Identify and apply appropriate patterns | Output from Lab 3.2–3.4 | Pattern mapping table, refactored diagram |
| [3.6](labs/lab-3.6.md) | Design Quality Review | Evaluate design quality and write a Design Review Report | Full design from Lab 3.1–3.5 | Design Review Report with checklist |

> [!NOTE]
> **Continuous scenario:** All labs in Chapter 3 build upon the CODING WAR system from Chapter 2. The SRS and requirements produced in Lab 2.3 serve as the primary input. Each lab's output becomes the next lab's input, giving students a continuous experience from requirements → architecture → detailed design → review.

## Directory Structure

```
chapter-03/
├── README.md
├── labs/
│   ├── lab-3.1.md   ← Concept Review & Trade-offs
│   ├── lab-3.2.md   ← Five Views: Architecture & Data
│   ├── lab-3.3.md   ← Five Views: Interface & Component
│   ├── lab-3.4.md   ← Deployment Design
│   ├── lab-3.5.md   ← Design Patterns
│   └── lab-3.6.md   ← Design Quality Review
├── solutions/
│   ├── sol-3.1.md
│   ├── sol-3.2.md
│   ├── sol-3.3.md
│   ├── sol-3.4.md
│   ├── sol-3.5.md
│   └── sol-3.6.md
└── assets/
    ├── CODING_WAR_Architecture_Reference.pdf   ← Reference Architecture Diagram
    ├── CODING_WAR_API_Spec.yaml                ← OpenAPI 3.0 spec
    └── Anti_Pattern_Examples.pdf               ← Anti-patterns reference
```

## Self-Assessment Checklist — Chapter 3

After completing this chapter, verify the following:

| # | Criterion | Lab |
|---|-----------|-----|
| 1 | Can explain the difference between Requirement (WHAT) and Design (HOW) using concrete CODING WAR examples | 3.1 |
| 2 | Each component in the Architecture Diagram has a Single Responsibility and does not overlap with others | 3.2 |
| 3 | Architecture Diagram traces back to SRS Lab 2.3 — no orphaned FRs | 3.2 |
| 4 | ER Diagram shows correct cardinality and has measurable data constraints (not just "valid") | 3.2 |
| 5 | API Contracts include: error codes, preconditions, postconditions, and request/response schema with types | 3.3 |
| 6 | Class Diagram demonstrates Information Hiding (private attributes, public methods) without exposing internals | 3.3 |
| 7 | JudgeService.judge() pseudocode covers: happy path + CE / TLE / MLE / RE / WA error paths | 3.3 |
| 8 | Deployment Diagram includes all nodes, artifacts, and communication protocols with no missing components | 3.4 |
| 9 | Identified at least 3 SPOFs and proposed practical (not just "add redundancy") solutions | 3.4 |
| 10 | Correctly identified at least 5 patterns and explained why each is used in the CODING WAR context | 3.5 |
| 11 | Detected all 4 anti-patterns and the proposed refactoring does not introduce new problems | 3.5 |
| 12 | Design Review Report contains a clear Verdict — not vague praise | 3.6 |
| 13 | Action Items include Severity + Affected Artifact + Responsible Person — not just general descriptions | 3.6 |

## Lab Materials

| File | Description | Used In |
|------|-------------|---------|
| `assets/CODING_WAR_Architecture_Reference.pdf` | Reference Architecture Diagram (Modular Monolith variant) | Lab 3.2, 3.6 |
| `assets/CODING_WAR_API_Spec.yaml` | Full OpenAPI 3.0 spec for all endpoints | Lab 3.3 |
| `assets/Anti_Pattern_Examples.pdf` | Common anti-patterns with explanations | Lab 3.5 |
