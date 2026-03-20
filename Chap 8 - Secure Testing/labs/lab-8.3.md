# Lab 8.3 — SAST: Semgrep + Bandit + Custom Rules

> **Chapter 8 · Security Testing Strategy and Toolchain Integration**
> Input: CODING WAR source code + `code/semgrep-rules/custom-coding-war.yml`
> Output: SAST Report + Custom Rules + Triage Records

## Learning Objectives

- Run Semgrep and Bandit on a real codebase and interpret the output.
- Write custom Semgrep rules that enforce specific Code Contracts from Ch.7 — not patterns that duplicate built-in rules.
- Triage findings with technical justification, distinguishing exploitability from theoretical risk.
- Integrate SAST into CI with thresholds appropriate to the CODING WAR risk profile.

## Code Files

| File | Role |
|------|------|
| `code/semgrep-rules/custom-coding-war.yml` | Ch.7 reference rules — read for syntax and specificity before writing your own |
| `code/.github/workflows/sast.yml` | CI integration for analysis in Task 4 |

---

## Task 1 — Run the Tools

```bash
pip install semgrep bandit --break-system-packages

semgrep scan \
  --config p/python \
  --config p/fastapi \
  --config p/owasp-top-ten \
  --config code/semgrep-rules/custom-coding-war.yml \
  --json -o semgrep-results.json \
  --severity WARNING \
  app/

bandit -r app/ -l -f json -o bandit-results.json --skip B101
```

If you do not have the full application codebase, use the simulated findings below for Tasks 3 and 4. Do not skip Task 2 — the rules you write are independent of whether you can run them against the full app.

| ID | Tool | Rule | File:Line | Description | Severity |
|----|------|------|-----------|-------------|----------|
| SF-001 | Semgrep | `sqlalchemy-execute-raw-query` | `submission_repo.py:147` | `db.execute()` with f-string containing user-controlled `sort_field` | HIGH |
| SF-002 | Semgrep | `subprocess-without-shell-false` | `judge_service.py:89` | `subprocess.run()` detected | MEDIUM |
| SF-003 | Bandit | B105 hardcoded-password | `config.py:12` | `JWT_SECRET = 'coding_war_secret'` | HIGH |
| SF-004 | Semgrep | `coding-war.ci03.admin-endpoint-missing-mfa` | `admin/contests.py:34` | Admin endpoint missing `Depends(require_admin_mfa)` | HIGH |
| SF-005 | Bandit | B324 hashlib | `legacy_hash.py:8` | `hashlib.md5(password)` | HIGH |
| SF-006 | Semgrep | `insecure-deserialization` | `cache.py:45` | `pickle.loads()` on data from Redis | CRITICAL |

---

## Task 2 — Write Custom Semgrep Rules

Read `code/semgrep-rules/custom-coding-war.yml` before writing anything. The existing rules demonstrate the level of specificity expected: each rule targets a violation of a named Code Contract, not a generic pattern.

Write rules that enforce Code Contracts from your Lab 7.1 document that are not already covered by the reference rules. Each rule must target a specific contract violation, include a message that tells a developer exactly what to fix and why, and reference the relevant ASVS control and CWE.

Test your rules:
```bash
semgrep scan --config your-rules.yaml app/
semgrep --test your-rules.yaml
```

A rule that never fires is as useless as one that fires on everything. Provide evidence — either test output or inline `# ruleid:` / `# ok:` annotations — that your rules match the intended patterns and do not match safe patterns.

---

## Task 3 — Triage All Findings

Apply the triage rubric to all 6 findings. For each: state your conclusion, justify it technically, specify the required action, and define closure criteria. The closure criteria must be independently verifiable — a second engineer who has not seen your fix must be able to confirm them.

One finding is a False Positive. Identify it and justify the conclusion with specific technical reasoning — not "it doesn't look exploitable" but why the vulnerable pattern is not reachable or not dangerous in CODING WAR's specific usage.

One finding must block merge. Identify it and explain why the severity warrants that gate.

SF-004 was caught by a rule in `code/semgrep-rules/custom-coding-war.yml` — a domain-specific rule, not a generic built-in. What does this demonstrate about the coverage gap between generic rulesets and project-specific rules?

---

## Task 4 — CI Integration Analysis

Review `code/.github/workflows/sast.yml` and answer:

1. The PR check uses a diff scan; the nightly job runs a full scan. What category of finding would each approach miss? Give a concrete example from CODING WAR — not a generic answer.
2. The nightly job has both `--error` and `continue-on-error: true`. These appear contradictory. Explain why both are present and what each controls.
3. SARIF output is uploaded to the GitHub Security tab. What does this provide that a JSON artifact in the workflow run does not?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| SAST run + findings | **15** | Tools run or simulation used; all 6 findings present |
| Custom rules | **40** | Each rule targets a specific contract not already in reference rules; message is actionable; tested with evidence |
| Triage (6 findings) | **30** | False Positive identified with specific technical justification; blocking finding identified; closure criteria are independently verifiable |
| CI analysis | **15** | 3 questions answered with correct technical reasoning specific to CODING WAR |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-8.3.md](../solutions/sol-8.3.md) after completing the lab.*
