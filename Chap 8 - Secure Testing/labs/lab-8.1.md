# Lab 8.1 — Design-Driven Test Planning

> **Chapter 8 · Security Testing Strategy and Toolchain Integration**
> Input: Threat Model from Ch.4 + SDR from Ch.6 + Code Contracts from Ch.7
> Output: Security Test Plan + Coverage Matrix

## Learning Objectives

- Build a test plan from the threat model — not from a generic checklist.
- Reason about which test technique is appropriate for each category of threat.
- Distinguish hygiene checks (every commit) from deep tests (nightly or pre-release) and understand why that distinction matters.
- Produce a Coverage Matrix that serves as the living document tracking security test posture throughout Ch.8.

---

## Background

A Coverage Matrix is not a list of tests. It is a mapping from risk to evidence: for each threat in your threat model, what artifact proves that threat is mitigated? If a row in the matrix has no evidence column, the control is assumed but not verified.

The Coverage Matrix you produce in this lab will be the reference for every subsequent lab in Ch.8. Each lab that produces a test artifact should trace back to a row in this matrix.

---

## Task 1 — Security Test Plan

Write a Security Test Plan for CODING WAR. It must be specific enough that another engineer joining the team could use it to understand what testing is done, when, why, and by whom.

The plan must address: what is being tested and what is out of scope, which environments are used and why each choice is safe, what the acceptance thresholds are at each pipeline stage, and how findings flow into the bug tracking and release process.

Do not copy a generic template. Every field must reflect CODING WAR's actual architecture, threat model, and constraints.

---

## Task 2 — 4-Questions Applied

Apply the 4-Questions framework to CODING WAR:
1. **What are we testing?** — define the system and its high-value assets
2. **What can go wrong?** — map specific threats from the Ch.4 threat model
3. **What do we do about it?** — map each threat to the control that addresses it (use Code Contracts from Ch.7 where applicable)
4. **Did we do a good job?** — define what evidence satisfies each control

The answers to Q3 and Q4 drive the Coverage Matrix. If you cannot name a specific control and a specific evidence artifact for a threat, the threat is not covered.

---

## Task 3 — Security Test Coverage Matrix

Produce the Coverage Matrix. Each row must represent a specific threat from your threat model. Each row must have: the threat, the control addressing it, the test technique appropriate for that threat type, the pipeline stage, the frequency, and the evidence artifact ID that will be produced.

The test technique column is where most coverage matrices are too weak — "unit test" is not a technique, it is a level. State what property is being tested and how the test would detect a control failure.

Your Coverage Matrix must cover all threats from Ch.4. Add any additional rows for risks you identify that were not in the original threat model.

---

## Task 4 — Prioritised Test Schedule

Define the three-tier test schedule for CODING WAR:

**Hygiene (every PR):** fast, deterministic, blocking on failure. State each check, why it must run at this frequency, what it costs in CI time, and whether it blocks merge or only alerts.

**Scheduled (nightly/weekly):** deeper, slower, non-blocking but alerting. State each check, why this frequency is sufficient, and what would be missed if the check ran less often.

**Deep (pre-release):** manual or destructive, requiring staging environment. State each activity, why it cannot be automated, and what it contributes that the other tiers cannot.

---

## Discussion

1. Your Coverage Matrix has a row for TH-03 (sandbox escape). You assign it to the pre-release pentest tier. A developer argues it should also have a unit test. What would that unit test actually verify, and is there a meaningful unit test for sandbox isolation?

2. The Coverage Matrix is described as a "living document." What events should trigger an update to the matrix — not just the addition of new tests, but the removal or deprecation of existing rows?

3. A finding emerges from DAST (Lab 8.6) that maps to a threat already covered by a unit test in Lab 8.2. Both tests were passing. What does this tell you about the relationship between SAST/unit test coverage and runtime behaviour?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Security Test Plan | **20** | Specific to CODING WAR; environments justified with safety reasoning; acceptance thresholds reference Ch.7 SCSP SLA |
| 4-Questions application | **20** | Q2 names specific threats from Ch.4 threat model; Q3 links to specific Code Contracts; Q4 defines observable evidence |
| Coverage Matrix | **40** | All Ch.4 threats covered; test technique describes the property being tested; evidence IDs are traceable |
| Test schedule | **10** | Three tiers correctly distinguished; blocking/alerting decisions justified |
| Discussion | **10** | Answers show practical judgment |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-8.1.md](../solutions/sol-8.1.md) after completing the lab.*
