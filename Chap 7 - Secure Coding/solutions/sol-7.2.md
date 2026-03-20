# Solution 7.2 — Integer Precision, Race Conditions & TOCTOU

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. The approach shown here is one valid path. Your solution may differ and still be correct.

---

## Key Insights

### Why `float` is wrong for scoring — not just imprecise

Python's `float` uses IEEE 754 binary floating point. The value `20.0` cannot be represented exactly in binary. Over many operations or with certain fractional penalties, the accumulated error changes the result of `int()` truncation — one contestant scores 939 where the correct answer is 940. In a contest context, this is not a rounding error — it is a fairness failure.

Using `Decimal` with explicit `ROUND_HALF_UP` eliminates both problems: exact representation and symmetric rounding. The type annotation (`Decimal` rather than `float`) makes the intent visible in the API.

### Why `asyncio.Lock()` does not fix the Redis race condition

`asyncio.Lock()` serialises access within a single Python process. In a production deployment, multiple worker processes handle concurrent requests. Two requests arriving at the same time will be handled by different processes — each holding its own lock, neither aware of the other.

The correct fix runs the check-and-increment atomically inside Redis using a Lua script. Redis is single-threaded for script execution — no interleaving is possible. This is the same guarantee `MULTI/EXEC` provides, but Lua scripts are preferred for check-and-modify patterns because they run as a single operation.

### Why `is_within_time_limit` missing a lower bound is a security issue

If `execution_ms` comes from a judge result JSON (an untrusted source), a value of `-1` always passes the time check — every submission appears to run instantly. This matters if an attacker can influence the judge result (e.g., by compromising a worker or replaying a crafted message). The validation is a trust boundary check, not just defensive programming.

### The TOCTOU gap explained

```
Thread A (attacker)                 Thread B (application)
                                    T1: os.path.exists("/tmp/sub_X") → False
create symlink: /tmp/sub_X → /etc/passwd
                                    T2: open("/tmp/sub_X", "wb") → writes to /etc/passwd
```

The gap between T1 and T2 is real — even on a single-core system, the OS can schedule a context switch between the two operations. The fix is to use `tempfile.NamedTemporaryFile()`, which calls `open()` with `O_CREAT | O_EXCL` internally — a single atomic OS call that both creates and opens the file, with no window for interference.

Using `/var/submissions/tmp/` instead of `/tmp/` eliminates the sticky-bit attack: on `/tmp`, any user can create files and race against the application. A dedicated directory with restricted permissions closes this path entirely.

### ASVS V15.4 — honest assessment

| Control | Status | Note |
|---------|--------|------|
| 15.4.1 | Pass (after fix) | Redis Lua script provides atomicity for the counter |
| 15.4.2 | Pass (after fix) | NamedTemporaryFile eliminates TOCTOU gap |
| 15.4.3 | Partial | The application has no other shared locking patterns currently; this should be revisited if additional shared resources are added |
| 15.4.4 | Partial | The submission quota limit exists; process-level resource limits (CPU, memory) for the judge are separate and depend on sandbox configuration |

---

## Reference Implementation Notes

See `code/fixed/scoring.py` and `code/fixed/submission_service.py` for one valid implementation. Key differences from naive approaches:

- `calculate_penalty_score`: `Decimal` throughout; `ROUND_HALF_UP` via `.quantize()`; `wrong_attempts >= 0` check raises `ValueError`, not silently corrects
- `increment_submission_count_atomic`: Lua script via `redis.eval()`; key format `sub_count:{user_id}:{contest_id}` scopes per-user per-contest
- `save_submission`: `NamedTemporaryFile` with `delete=False` (caller deletes after judge completes); `dir=` set to controlled directory, not `/tmp`

---

*Back to the lab: [labs/lab-7.2.md](../labs/lab-7.2.md)*
