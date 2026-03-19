# Solution 8.7 — Fuzzing: Hypothesis + Atheris

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. The approach shown here is one valid path.

---

## Key Insights

### Security property vs correctness property

A correctness property: "for input (1000, 3, 20), the result is 940." A security property: "for *any* valid input, the result is always an `int` and never increases when `wrong_attempts` increases." The second property would catch a float precision bug that occasionally rounds differently, or an arithmetic path where adding a penalty accidentally increased the score due to signed integer behaviour. Example-based testing would only catch these if someone happened to write the specific example that triggers them. Hypothesis finds them automatically.

### The information leakage property — why 3 patterns is not enough

A list of `["traceback", "sqlalchemy", "postgresql"]` catches the obvious leaks. But CODING WAR's stack includes asyncpg (async PostgreSQL driver), pydantic (model validation framework), uvicorn (ASGI server), alembic (migration tool), and the jwt library. An error that leaks `asyncpg.exceptions.UniqueViolationError` tells an attacker the database is PostgreSQL with asyncpg, the table has a unique constraint, and the constraint name (which may reveal the column name). The test must cover the full stack, not just the first three things that come to mind.

### Testing through the API vs testing the generator directly

A unit test of `generate_submission_id()` verifies that the function returns a non-integer string. It does not verify that the value makes it through the full request pipeline without being transformed. A middleware, an ORM mapper, a serializer, or a schema could cast the ID to an integer before it reaches the response. Only testing through the API catches this. Property-based testing through the API also surfaces concurrency issues — if two concurrent requests generate colliding IDs, the API response (not the generator function) is where you would observe the symptom.

### Why catch exceptions and only re-raise on "FUZZ BUG"

Pydantic's `ValidationError` is the expected outcome for the vast majority of fuzz inputs — random bytes are almost never valid submissions. If the harness re-raised every exception, the fuzzer would stop on the first invalid input and report a "crash" that is correct behaviour. This would consume the entire fuzzing budget on a single non-bug input. Only re-raising on `"FUZZ BUG"` means the fuzzer continues exploring inputs even when most of them are rejected, and only stops when an actual invariant is violated.

### Why clamp input values for arithmetic functions

Without clamping, the fuzzer generates `base_score = 2**63` and `wrong_attempts = 2**63`. Python's arbitrary-precision arithmetic means this computation is valid but takes a very long time. The fuzzer would spend its entire budget waiting for one computation to complete, exercising the same "very large numbers" code path repeatedly and never exploring the interesting boundary conditions around the scoring logic. Clamping to `10_000_000` keeps computations fast and directs the fuzzer's coverage guidance toward branches that affect business logic.

### Discussion answers

**Q1 — Nan/Infinity from Decimal strategy:** Exclude both. `Decimal('NaN')` and `Decimal('Infinity')` are valid Decimal values but cannot be converted to `int`. The function's contract specifies finite penalty values — a penalty of infinity is not a real business case. Including them would generate `ValueError: cannot convert NaN to integer` on every such case, making the test report a "failure" that is actually correct boundary behaviour. This would overwhelm the test output and hide real failures.

**Q2 — Sandbox isolation test — no crash:** A clean 30-second run cannot conclude the sandbox is secure. It can conclude that the specific test cases attempted did not escape. Meaningful confidence requires: a longer run with diverse seed inputs, coverage measurement to verify the sandbox's code paths were actually exercised, and periodic re-testing after gVisor version updates. A 30-second run is a smoke test, not a security assessment.

**Q3 — CI retention criteria by severity:** Crash inputs that cause RCE or data leakage block release — they represent critical security vulnerabilities regardless of when they were introduced. Crash inputs that cause DoS (unhandled exception, resource exhaustion) should block release if they are reachable from untrusted input. Crashes that require already-privileged access or complex preconditions can go to the bug backlog. All crash inputs should be retained until the fix is deployed and verified — they become regression tests.

---

*Back to the lab: [labs/lab-8.7.md](../labs/lab-8.7.md)*
