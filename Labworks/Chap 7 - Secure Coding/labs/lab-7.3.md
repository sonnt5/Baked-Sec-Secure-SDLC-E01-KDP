# Lab 7.3 — Injection Prevention: SQL, Command & Regex

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: `code/vulnerable/submission_repo.py`, `judge_service.py`, `code_validator.py`
> Output: Injection-Free Implementations + ASVS V1.2 Assessment

## Learning Objectives

- Identify injection sinks and trace the path from untrusted input to dangerous operation.
- Understand why some injection types cannot be solved with escaping or parameterization alone.
- Produce safe implementations and explain the security guarantees they provide.

## Code Files

| File | Role |
|------|------|
| `code/vulnerable/submission_repo.py` | Read before writing anything |
| `code/vulnerable/judge_service.py` | Read before writing anything |
| `code/vulnerable/code_validator.py` | Read before writing anything |
| `code/fixed/submission_repo.py` | Reference implementation — consult after finishing your own |
| `code/fixed/judge_service.py` | Reference implementation — consult after finishing your own |
| `code/fixed/code_validator.py` | Reference implementation — consult after finishing your own |

---

## Task 1 — Injection Sink Inventory

Read all three vulnerable files. Before writing any code, map every injection sink you find.

For each sink: identify the sink type (SQL, OS command, regex engine, template), the specific location in code, the untrusted source that reaches it, and the realistic exploit. Write the exploit as a concrete input value — not a generic description.

One of the SQL injection sinks in `submission_repo.py` is unusual: standard parameterization cannot fix it. Identify which one and explain why parameterization fails before you attempt the fix. This explanation is part of your answer.

---

## Task 2 — Fix `submission_repo.py`

Write corrected implementations of both functions.

For the sink where standard parameterization fails: document your chosen approach and the guarantee it provides. What input values would your fix reject, and how?

Verify with:
```python
# Must raise — or return an error — for injection attempts
get_submissions_by_contest(db, "cst_001", sort_by="'; DROP TABLE submissions; --")
get_submissions_by_contest(db, "cst_001", sort_by="CASE WHEN 1=1 THEN score ELSE 0 END")

# Must succeed
get_submissions_by_contest(db, "cst_001", sort_by="score")
search_problems(db, q="binary search")
```

---

## Task 3 — Fix `judge_service.py`

Write a corrected implementation of `run_in_sandbox`.

Your implementation must make the security properties explicit in the code itself — not in this document. A reviewer reading only your file should understand why it is safe.

---

## Task 4 — Fix `code_validator.py`

Write corrected implementations of `check_output_format` and `validate_verdict_format`.

There is more than one valid approach. Choose the approach most appropriate for each function's role in the judging pipeline, implement it, and explain in the code why you chose it. If you use different approaches for the two functions, explain why.

---

## Task 5 — ASVS V1.2 Assessment

Assess CODING WAR against these ASVS V1.2 controls after completing your fixes:

| Control | Description |
|---------|-------------|
| V1.2.4 | SQL queries use parameterized queries or ORM |
| V1.2.5 | Protected against OS command injection |
| V1.2.9 | ReDoS protection in place |

State Pass, Fail, or Partial for each, with evidence from your implementations. For anything that is not a full Pass, describe what remains unaddressed.

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Injection sink inventory | **20** | All sinks found; the special-case SQL sink is correctly diagnosed before fixing |
| `submission_repo.py` | **25** | Both sinks fixed; special-case reasoning is technically correct; verified inputs listed |
| `judge_service.py` | **25** | Command injection eliminated; security guarantees documented in code |
| `code_validator.py` | **20** | ReDoS addressed for both functions; approach choice explained in code |
| ASVS V1.2 assessment | **10** | Evidence is specific; partial/fail entries name the gap |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.3.md](../solutions/sol-7.3.md) after completing the lab.*
