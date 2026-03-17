# Lab 7.2 — Low-Level Flaws: Integer Overflow, Memory Safety & TOCTOU

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: CODING WAR codebase scenarios | Output: Vulnerability Analysis Report + Fixed Code

> [!NOTE]
> **OWASP ASVS v5.0.0:** ASVS V15.4.2 — *"Verify that checks on a resource's state are performed as close as possible to when it is used, and ideally atomically, to prevent TOCTOU bugs."* V15.4.1 — *"Verify that shared objects in multi-threaded code are protected using appropriate locking mechanisms."* V15.3.5 — *"Verify that variables are of the correct expected type before use."*

## Learning Objectives

- Identify integer overflow/underflow in Python — especially when `int` is used for scoring/quota calculations.
- Analyze length validation failures that lead to buffer over-read class bugs.
- Understand TOCTOU and apply atomic operations for filesystem operations.
- Map low-level bugs → assets → risk (3 axes analysis).

---

## Task 1 — Integer/Arithmetic Analysis

Study the vulnerable code in [`code/vulnerable/scoring.py`](../code/vulnerable/scoring.py). It contains three scenarios.

For each scenario, complete the analysis table and then study the fixed version in [`code/fixed/scoring.py`](../code/fixed/scoring.py).

| Scenario | Bug Type | Asset Affected | Risk Level | Why This Risk Level? | Fix Approach |
|----------|---------|---------------|-----------|---------------------|-------------|
| **A: Float precision** (`calculate_penalty_score`) | Implicit `int→float→int`; truncation asymmetry | Contest scores — HVA (prize validity) | High | Float imprecision in scoring can alter contest standings; asymmetric truncation systematically disadvantages certain contestants | Use `Decimal` type for all scoring calculations; `round()` with explicit rounding mode; test large penalty scenarios |
| **B: TOCTOU counter** (`increment_submission_count`) | Read-check-increment not atomic (race condition) | Submission quota — integrity invariant | High | Two concurrent requests can both pass the check and both increment → 11 submissions when limit is 10; ASVS V15.4.1 violation | Use Redis INCR atomically with Lua script: not GET→check→SET |
| **C: Negative exec time** (`is_within_time_limit`) | Missing lower-bound validation on trusted-enough input | Execution time limit enforcement | Medium-High | If judge result JSON is from a compromised judge service, negative `execution_ms` bypasses the time limit — all submissions appear fast | Validate: `0 <= execution_ms <= MAX_REASONABLE` |

**Exercise:** Read `code/fixed/scoring.py` and answer:
1. Why does Scenario A use `Decimal("20")` with quotes, not `Decimal(20.0)`?
2. Why is a Redis Lua script the right fix for Scenario B rather than a Python-level lock?
3. What is the value of `_MAX_REASONABLE_EXECUTION_MS` and what is the business justification?

---

## Task 2 — TOCTOU Analysis: Submission File Handling

Study the vulnerable code in [`code/vulnerable/submission_service.py`](../code/vulnerable/submission_service.py).

| Aspect | Analysis |
|--------|---------|
| **TOCTOU gap** | Between `os.path.exists()` check (T1) and `open()` write (T2) — attacker can replace path with a symlink pointing to `/etc/passwd` or `/judge/test_cases/*.txt` |
| **Asset at risk** | If symlink points to test case files → source_code overwrites test cases → contest integrity failure. If symlink points to judge config → arbitrary file write → potential RCE. |
| **Severity** | High — contest integrity at risk if judge has write access to test cases. Critical if symlink points to application config/secrets. |
| **ASVS violation** | V15.4.2: check and use not atomic. Also V5.1 (File Handling — no documentation of temp file handling). Also V5.3.1 (file path canonicalization). |
| **Fix principle** | Use `tempfile.NamedTemporaryFile(dir=SAFE_DIR, delete=False)` — runtime ensures atomic creation. NEVER use predictable temp file paths. |

Study [`code/fixed/submission_service.py`](../code/fixed/submission_service.py) and answer:
1. Why does `SUBMISSION_TEMP_DIR` matter? What attack does using `/tmp` enable?
2. Why does the fixed function return a `pathlib.Path` object instead of a `str`?
3. What does `delete=False` do, and who is responsible for deleting the file?

---

## Task 3 — ASVS V15.4 Safe Concurrency Compliance Check

| ASVS Control | Description | CODING WAR Status | Evidence / Gap |
|-------------|-------------|------------------|---------------|
| **15.4.1** | Shared objects in multi-threaded code protected by appropriate locking | Partial | Redis atomic Lua scripts for counters. Gap: `verdict_aggregate` in memory during bulk contest evaluation — needs audit. |
| **15.4.2** | Checks on resource state performed atomically (TOCTOU prevention) | Fail | TOCTOU in temp file creation (Task 2). TOCTOU in submission count check (Task 1 Scenario B). Fix: atomic patterns implemented in fixed code. |
| **15.4.3** | Locks used consistently to avoid thread starvation | Partial | Redis TTL on rate limit keys prevents indefinite lock. Gap: async DB transaction not always using `FOR UPDATE` — audit required for contest leaderboard updates. |
| **15.4.4** | Resource allocation policies prevent thread starvation | Partial | Max concurrent judges configured per instance. Gap: `asyncio.Semaphore` for judge queue not yet implemented. |
| \[Team adds\] | | | |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Integer/Arithmetic Analysis (3 scenarios) | **30** | Each scenario: bug type identified correctly (3 pts), asset + risk level explained via 3 axes (4 pts), fix approach specific (3 pts) |
| Fixed Code Analysis — Scenario A + B | **25** | Scenario A: explains Decimal vs float (10 pts); Scenario B: explains atomic Lua script necessity (15 pts). Analysis must show understanding, not just restate the code |
| TOCTOU Analysis (table + fixed code analysis) | **25** | TOCTOU gap explained with timing (5 pts); asset at risk identified (5 pts); fix explanation covers controlled directory + atomic creation + Path return type (15 pts) |
| ASVS V15.4 Compliance Check | **20** | 4 controls assessed honestly; Fail items have specific gap description; Partial items explain what is missing |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.2.md](../solutions/sol-7.2.md)*
