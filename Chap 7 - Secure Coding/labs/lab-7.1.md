# Lab 7.1 — Design Invariants & Code Contracts

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: Architecture artifacts + SDR from Chapters 3–6
> Output: Code Contract Document + Vulnerability Chain Analysis

## Learning Objectives

- Translate architectural design decisions into enforceable code invariants.
- Distinguish between a design assumption (documentation) and a code contract (enforcement).
- Analyse how individually minor weaknesses combine into high-severity vulnerability chains.
- Produce the Code Contract Document that Labs 7.2–7.7 will build on.

---

## Background

A design assumption says *what should be true*. A code contract says *what must be true, where, and how you would know if it was violated*. The difference is enforcement.

When the SDR from Chapter 6 says "all DB access goes through the repository layer," that is a design assumption — until someone specifies which file enforces it, which SAST rule detects violations, and which test confirms it. Only then does it become a code contract.

This lab translates the CODING WAR architecture into contracts concrete enough to survive a new engineer joining the team.

---

## Task 1 — Trust Boundary & Asset Map

Using your architecture artifacts from Chapters 3–6, produce:

**A. Trust Boundary Map**
For every point where data enters or crosses a trust boundary in CODING WAR, document: the entry point, what data it carries, the trust level assigned to that data, and what sinks it can reach. A sink is any operation that makes the data consequential — a database write, an OS call, a rendered template, a log entry, a Redis operation.

**B. High-Value Asset Register**
List every asset in CODING WAR whose compromise, corruption, or unavailability would cause significant impact. For each asset: describe it, identify which components handle it, and state what category of harm its loss would cause (integrity, confidentiality, availability, or a combination).

> No required format or minimum count. The map should be complete enough that a new team member could use it to identify which data is safe to log and which is not.

---

## Task 2 — Code Contract Document

Produce a Code Contract Document for CODING WAR based on your Task 1 analysis.

Each contract must specify:
- **The invariant** — what must always be true
- **The enforcement location** — a specific module or file path, not a layer name
- **The detection method** — a concrete check that a second engineer can run independently

Cover at minimum: all major data entry points from Task 1, the judging pipeline, authentication and authorisation enforcement, and logging.

> "The service layer validates all input" is a design assumption.
> "`app/schemas/submission.py` — Pydantic `SubmissionCreate` schema with `language: Literal['python','cpp','java']`; violation detected by `test_invalid_language_returns_422`" is a code contract.

---

## Task 3 — Vulnerability Chain Analysis

A vulnerability chain occurs when individually low-severity weaknesses combine into a significantly higher-severity impact.

Identify two vulnerability chains present in CODING WAR. For each chain:
- Walk through each step with its individual severity and what it enables next
- State the combined impact at the end and explain why it exceeds any single step
- Reference the code contracts from Task 2 that, if enforced, would break the chain

Then construct one chain of your own that is not derived from this document.

---

## Discussion

1. A new engineer is assigned to the submission endpoint. They haven't read the SDR. What does your Code Contract Document tell them that inline code comments cannot?

2. You have twelve code contracts. Two of them would take a full sprint to enforce. Which criteria do you use to decide which to enforce first?

3. A senior engineer ships a one-off direct database query in an API handler, bypassing the repository layer. Three weeks later, a security review finds it. What mechanism in your contract document should have caught this before it shipped?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Trust Boundary Map + Asset Register | **20** | Entry points and assets are complete; trust levels are justified, not assumed |
| Code Contract Document | **50** | Each contract: enforcement location is a specific file path; detection method is independently executable; invariant is falsifiable |
| Vulnerability Chain Analysis | **20** | Each chain: step-by-step escalation explained; combined severity exceeds individual steps with reasoning; own chain is original |
| Discussion | **10** | Answers show practical judgment, not textbook recitation |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.1.md](../solutions/sol-7.1.md) after completing the lab.*
