# Solution 7.3 — Injection Prevention

> [!WARNING]
> **Reference Solution** — Complete the lab on your own before consulting this.

---

## Task 2 — SQL Injection Analysis

**Q1: Why ORDER BY cannot be parameterized:**
SQL parameterization works by sending the query structure and the values separately to the database driver — the driver escapes the values and inserts them as literals. But `ORDER BY score` is not a value; it is part of the query structure (a column reference). You cannot tell the DB "ORDER BY $1" and pass "score" as $1 — the DB would interpret $1 as a string literal and execute `ORDER BY 'score'` (sorting by a constant), not by the column. So the fix must operate at the Python layer: validate the user input against an allowlist of known-safe column names, then embed the corresponding SQLAlchemy column object (not the string) into the query.

**Q2: `f"%{q}%"` inside `ilike()` vs inside `db.execute(f"... LIKE '{q}'")`:**
In `ilike(f"%{q}%")`, the `%{q}%` string is computed in Python and passed to SQLAlchemy as the value of a parameterized bind. SQLAlchemy generates `WHERE title ILIKE $1` and sends `%user_input%` as the bind variable — the DB driver handles escaping. The `%` wildcards are constants in the pattern, not user-controlled. In `db.execute(f"... LIKE '{q}'")`, the user's value is concatenated directly into the SQL string before it reaches the driver — any SQL metacharacter in `q` (single quote, percent, underscore) can alter the query.

**Q3: IS-06 example:**
`app/repositories/contest_repo.py` `get_contests_by_status()` — uses `db.execute(f"SELECT * FROM contests WHERE status = '{status}'")`where `status` comes from a query parameter. Fix: use `select(Contest).where(Contest.status == status)` with a `Literal['active','upcoming','ended']` Pydantic type on `status`.

---

## Task 3 — Command Injection: 5 Elements

| Element | Why necessary |
|---------|--------------|
| `shell=False` | Without this, the OS spawns a shell (`/bin/sh -c "..."`) that interprets metacharacters. With `shell=False`, each list element is a literal argument — no shell interpretation. |
| Absolute interpreter path | Without absolute path, the OS searches `$PATH`. If an attacker can manipulate `$PATH` (e.g., via environment injection), they can redirect `python` to a malicious binary. |
| `env={}` | An empty environment prevents `LD_PRELOAD`, `PYTHONPATH`, `PATH`, and other injectable variables. Without this, the judge subprocess inherits the app server's environment. |
| `cwd="/sandbox"` | Sets the working directory to the sandbox root. Any relative path operations by the executed code resolve within the sandbox, not the app server's working directory. |
| Language allowlist | Without this, a contestant could submit `language="python; rm -rf /"` — even with `shell=False`, this would be passed as a literal argument to the interpreter, which would likely fail but could produce unpredictable behavior. The allowlist maps user strings to `Path` objects, eliminating the string entirely. |

---

## Task 4 — ReDoS

**Q1: Backtracking trace for `r"([a-zA-Z]+)*"` on `"aaaaaaaaX"`:**
The regex tries to match `([a-zA-Z]+)*` against `"aaaaaaaaX"`. The outer `*` means "zero or more repetitions of the group". The inner `+` means "one or more letters". The engine explores: 8 letters in one group, then 7+1, then 7 letters then 1, then 6+2, 6+1+1, 5+3... the number of ways to partition 8 `a`s into groups of 1+ is exponential. When the `X` causes a final mismatch after all these attempts, the engine has explored 2^8 = 256 paths. At length 20, it's 2^20 = 1M. At length 30: 1 billion. This is catastrophic backtracking.

**Q2: Threading timeout limitation:**
The timeout wrapper cannot kill the thread — Python threads cannot be forcibly terminated. After the join timeout, the thread continues running in the background consuming CPU. In a high-request-rate scenario, many concurrent ReDoS requests can exhaust the thread pool. The fix is a runtime mitigation, not a prevention. Pre-compiled linear patterns are a true prevention because they eliminate the backtracking class of vulnerability entirely.

**Q3: Why `EXPECTED_VERDICT_PATTERN` is linear:**
`^(ACCEPTED|WRONG_ANSWER|TIME_LIMIT_EXCEEDED|MEMORY_LIMIT_EXCEEDED|RUNTIME_ERROR)$` has no nested quantifiers. Each alternative is a literal string (no `+`, `*`, or `?` inside). The regex engine needs at most one pass through the input to match or reject. The alternation uses a fixed set of known strings, so the engine can use Aho-Corasick or similar O(n) matching internally.

---

*Back to the lab: [labs/lab-7.3.md](../labs/lab-7.3.md)*
