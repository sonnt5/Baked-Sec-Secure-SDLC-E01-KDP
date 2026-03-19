# Solution 8.3 — SAST: Semgrep + Bandit + Custom Rules

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. The approach shown here is one valid path.

---

## Key Insights

### Why custom rules find what built-in rules miss

Built-in Semgrep rules target generic patterns: `subprocess.run(shell=True)`, `db.execute(...)`, `hashlib.md5(...)`. They do not know that CODING WAR has a Code Contract that `subprocess.run(shell=True)` is only permitted inside `sandbox_runner.py`. A generic rule fires everywhere; the custom rule fires only on the violation — the gap between what is allowed and what is actually in the code.

SF-004 was caught by the custom CI-03 rule from Ch.7. A generic rule for "admin endpoint" would require knowing CODING WAR's routing convention. A built-in rule cannot know that `/admin/` routes require `Depends(require_admin_mfa)`. This is the coverage gap that custom rules fill.

### The False Positive — SF-002

SF-002 (`subprocess.run()` in `judge_service.py`) is the False Positive. The rule fires on any `subprocess.run()` detected, but `judge_service.py` is the only permitted location per CI-04. The fixed version already uses `shell=False`, absolute paths, and empty `env={}`. The correct action is to suppress with `# nosemgrep: coding-war.ci04.subprocess-shell-true` with a comment referencing CI-04.

The justification must be specific: not "this is fine" but "this is the permitted location per CI-04; the code uses `shell=False`, absolute interpreter path from `ALLOWED_LANGUAGES`, empty `env={}`, and `cwd='/sandbox'` — all five required elements are present."

### SF-006 blocks merge

`pickle.loads()` on data from Redis is Remote Code Execution if the Redis key can be poisoned. An attacker who can write to Redis (via SSRF, compromised service, or mis-configured network policy) can inject a pickle payload that executes arbitrary Python on deserialization. There is no safe way to use `pickle.loads()` on data from an external source. The fix is `json.loads()` — JSON deserialization cannot execute code.

### CI analysis — diff scan vs full scan

The PR diff scan misses files that were not changed in the current PR. A hardcoded secret added three months ago would not appear in the diff of a PR that touches unrelated code. The nightly full scan catches accumulated issues that no individual PR introduced — they exist because no PR ever changed those files.

The `--error` flag makes Semgrep exit non-zero when findings exist. `continue-on-error: true` means the CI job shows as failed (alerting) but does not block the branch. This is the correct behaviour for nightly scans: you want visibility and alerting, not a branch block from findings that may have existed for weeks.

---

*Back to the lab: [labs/lab-8.3.md](../labs/lab-8.3.md)*
