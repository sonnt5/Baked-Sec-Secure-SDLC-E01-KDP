# Solution 7.2 — Low-Level Flaws: Integer, Memory, TOCTOU

> [!WARNING]
> **Reference Solution** — Complete the lab on your own before consulting this.

---

## Task 1 — Fixed Code Analysis Questions

**Q1: Why `Decimal("20")` with quotes, not `Decimal(20.0)`?**
`Decimal(20.0)` converts the float `20.0` first, inheriting its binary representation imprecision: `Decimal(20.0)` gives `Decimal('20')` here but `Decimal(0.1)` gives `Decimal('0.1000000000000000055511151231257827021181583404541015625')`. Always initialize `Decimal` from a string to guarantee exact representation.

**Q2: Why Redis Lua script rather than a Python-level lock?**
A Python-level lock (e.g., `asyncio.Lock`) only works within a single process. CODING WAR runs multiple FastAPI workers (and possibly multiple hosts). A lock in worker 1 is invisible to worker 2. The Redis Lua script runs atomically inside Redis itself — the single Redis server serializes all operations regardless of how many app workers are calling it simultaneously. This is the correct tool for distributed atomic operations.

**Q3: `_MAX_REASONABLE_EXECUTION_MS = 60_000` — business justification:**
No competitive programming problem has a legitimate time limit exceeding 60 seconds (most are 1–5 seconds). Any value above 60,000ms is either a bug in the judge or a manipulation attempt. The bound is a defense-in-depth check: even if the judge process is compromised and returns a fabricated time, this validation prevents the fabricated value from propagating through business logic.

---

## Task 2 — TOCTOU Fixed Code Analysis

**Q1: Why `SUBMISSION_TEMP_DIR` matters?**
Using `/tmp` allows any process on the system (including other contest submissions running concurrently) to pre-create a symlink at the predictable path `/tmp/submission_{id}.py` before the write. A dedicated directory owned by the judge service (mode 700) means only the judge process can write there — an attacker running as a different user cannot pre-place a symlink.

**Q2: Why `pathlib.Path` instead of `str`?**
`Path` objects make path-traversal bugs harder. You can't accidentally concatenate a `Path` with a user-supplied string using `+`. Operations like `.is_absolute()`, `.parent`, `.suffix` work correctly without string manipulation. It's a type-level guardrail that makes the code's intent explicit.

**Q3: `delete=False` and cleanup responsibility:**
`delete=False` means the file persists after the `with` block closes. Without this, the file is deleted when the context manager exits — before the judge has a chance to read it. The caller (JudgeService) is responsible for calling `path.unlink()` after the judge completes (or fails). This should be done in a `finally` block to ensure cleanup even on exceptions.

---

## Code References

| File | Role | Link |
|------|------|------|
| Vulnerable scoring logic | Float precision + TOCTOU counter bugs | [`code/vulnerable/scoring.py`](../code/vulnerable/scoring.py) |
| Fixed scoring logic | Decimal + atomic Redis Lua script | [`code/fixed/scoring.py`](../code/fixed/scoring.py) |
| Vulnerable submission service | TOCTOU temp file bug | [`code/vulnerable/submission_service.py`](../code/vulnerable/submission_service.py) |
| Fixed submission service | NamedTemporaryFile atomic | [`code/fixed/submission_service.py`](../code/fixed/submission_service.py) |

---

*Back to the lab: [labs/lab-7.2.md](../labs/lab-7.2.md)*
