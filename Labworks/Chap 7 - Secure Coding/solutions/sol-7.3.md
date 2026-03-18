# Solution 7.3 — Injection Prevention: SQL, Command & Regex

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. Your approach may differ and still be correct.

---

## Key Insights

### IS-01: Why ORDER BY cannot be parameterized

SQL parameterization works by separating the query structure from the data values. A parameter placeholder (`$1`, `?`, `:name`) tells the database driver: "this position holds a value." The database engine uses it as data — it never interprets it as SQL syntax.

`ORDER BY` sorts on a *column name*, which is part of the query structure — not a value. If you write `ORDER BY $1` with `$1 = 'score'`, the database sorts by the string `'score'` (a literal), not the column named `score`. The query runs, but the result is wrong and the sort order is meaningless.

The correct fix is an allowlist: a Python dict mapping user-supplied strings to SQLAlchemy column objects. The dict lookup happens before any SQL is constructed — if the key is not in the dict, a `ValueError` is raised before touching the database.

```python
ALLOWED_SORT_FIELDS = {
    'score': Submission.score,
    'penalty': Submission.penalty,
    'time': Submission.execution_time_ms,
    'submitted_at': Submission.submitted_at,
}
```

### IS-02: Why ilike() is safe and raw SQL is not

`Problem.title.ilike(f"%{q}%")` is safe because SQLAlchemy passes `q` as a bind variable. The `%{q}%` string is the *value* of the LIKE clause — it is passed to the database driver as a parameter, and the driver handles any special characters. The SQL that reaches the database engine is:

```sql
SELECT * FROM problems WHERE title ILIKE $1
-- with $1 = '%user search query%'
```

`db.execute(f"SELECT * FROM problems WHERE title LIKE '%{q}%'")` is unsafe because `q` is inserted directly into the SQL string before it reaches the database driver. The driver sees a complete SQL statement and executes it verbatim.

### IS-03: The five elements of safe subprocess execution

Each element closes a specific attack surface:

| Element | Attack it prevents |
|---------|-------------------|
| `shell=False` + list API | Shell metacharacters (`;`, `&&`, `|`, `$()`) are not interpreted — they are passed as literal arguments to the interpreter |
| Absolute interpreter path (`/usr/bin/python3`) | PATH hijacking — an attacker who can write to a directory in PATH cannot substitute a malicious binary |
| `env={}` (empty environment) | `LD_PRELOAD` injection, `PYTHONPATH` manipulation, and other environment-variable attacks |
| `cwd="/sandbox"` | Relative path traversal within the execution context |
| Validate `source_path.is_absolute()` | Ensures the file path was constructed by the application, not passed through from user input |

### IS-05: Timeout vs. linear pattern — when to use each

A timeout (Approach 1) is a circuit breaker — it limits the damage of a ReDoS but does not prevent the CPU spike. For the brief window before the timeout fires, a worker thread is saturated. Under sustained attack, this can still degrade service.

A pre-compiled linear pattern (Approach 2) runs in O(n) time regardless of input content — there is no backtracking, so no crafted input can cause exponential cost. This is the correct approach for any pattern the application controls (like verdict format validation).

Use Approach 1 only when patterns come from an external source and you cannot guarantee they are safe. Use Approach 2 whenever you can define the pattern yourself.

---

*Back to the lab: [labs/lab-7.3.md](../labs/lab-7.3.md)*
