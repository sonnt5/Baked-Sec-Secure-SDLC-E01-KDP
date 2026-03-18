# Lab 7.2 — Integer Precision, Race Conditions & TOCTOU

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: `code/vulnerable/scoring.py`, `code/vulnerable/submission_service.py`
> Output: Vulnerability Analysis + Fixed Implementations

## Learning Objectives

- Diagnose arithmetic precision and atomicity bugs in production Python code.
- Reason about the security impact of low-level implementation choices — not just correctness.
- Produce fixed implementations and explain why each fix eliminates the vulnerability.

## Code Files

| File | Role |
|------|------|
| `code/vulnerable/scoring.py` | Read before writing anything |
| `code/vulnerable/submission_service.py` | Read before writing anything |
| `code/fixed/scoring.py` | Reference implementation — consult after finishing your own |
| `code/fixed/submission_service.py` | Reference implementation — consult after finishing your own |

---

## Task 1 — Diagnose the Vulnerabilities

Read both vulnerable files. Before writing any code, document your findings.

For each bug you identify: describe the root cause, construct a realistic attack or failure scenario (not a theoretical one — describe what an attacker or a race condition would actually do), identify which CODING WAR asset is affected, and connect it to the code contracts you defined in Lab 7.1.

The vulnerable files contain three distinct bugs in `scoring.py` and one in `submission_service.py`. Find them all.

---

## Task 2 — Fix `scoring.py`

Write a corrected implementation of the three functions in `scoring.py`.

Your implementations will be assessed on whether they actually solve the vulnerability — not whether they match the reference in `code/fixed/`. If you choose a different approach, document your reasoning and what property your approach guarantees.

After writing your implementation, verify it against at least these inputs:

```python
# calculate_penalty_score
assert calculate_penalty_score(1000, 3, 20) == 940
assert calculate_penalty_score(100, 5, ...) == 99   # what penalty gives 98.5 before rounding?
assert isinstance(calculate_penalty_score(500, 0, 20), int)

# is_within_time_limit
assert is_within_time_limit(5000, 10000) == True
assert is_within_time_limit(-1, 10000) raises ValueError  # negative must be rejected
```

---

## Task 3 — Fix `submission_service.py`

Write a corrected implementation of `save_and_verify_submission`.

Your implementation must eliminate the TOCTOU gap. In your code — either as a docstring or inline comments — explain:
- Why the original check-then-act sequence is exploitable
- What property of your fix makes exploitation impossible

---

## Task 4 — ASVS V15.4 Assessment

After completing your fixes, assess CODING WAR against these ASVS V15.4 controls. For each, state Pass, Fail, or Partial — and for anything that is not a full Pass, state the specific remaining gap.

| Control | Description |
|---------|-------------|
| V15.4.1 | Shared objects in concurrent code are protected by appropriate locking |
| V15.4.2 | Checks on resource state are performed atomically (TOCTOU prevention) |
| V15.4.3 | Locks are used consistently across all access paths to avoid starvation |
| V15.4.4 | Resource allocation policies prevent quota exhaustion |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Vulnerability diagnosis | **25** | All four bugs found; each has a realistic scenario; asset impact connects to Lab 7.1 contracts |
| `scoring.py` | **35** | All three functions correct; reasoning documented where approach differs from the obvious path |
| `submission_service.py` | **30** | TOCTOU gap eliminated; explanation in code is technically accurate |
| ASVS V15.4 assessment | **10** | Honest assessment; Partial/Fail entries name the specific gap |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.2.md](../solutions/sol-7.2.md) after completing the lab.*
