# Lab 7.7 — Code Review Checklist, Review Minutes & Security Test Matrix

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: Labs 7.1–7.6 findings
> Output: Code Review Checklist + Review Minutes + Security Test Matrix

## Learning Objectives

- Build a checklist that reflects what you have learned, not what a template provides.
- Write code review findings the way they would appear in a real engineering process.
- Define security tests concretely enough that another engineer can run them.

---

## Task 1 — Vulnerability-Class Checklist

Build a secure coding checklist for the CODING WAR project. This checklist will be used by reviewers for every PR.

The calibration test: could you replace "CODING WAR" with another project name and have every item still make sense unchanged? If yes, the item is too generic. Each item must reference something observable — a specific module, pattern, decorator, or tooling output.

Include categories that reflect the vulnerability classes from Labs 7.2–7.6. Add any categories you consider important that those labs did not cover.

---

## Task 2 — Code Review Minutes: PR-241

PR-241 adds a contest leaderboard endpoint:
```
GET /api/v1/contests/{contest_id}/leaderboard?sort=score&order=desc&page=1
```
Files changed: `app/api/contests.py`, `app/repositories/submission_repo.py`, `app/schemas/leaderboard.py`

Write the security review minutes for this PR as they would appear in your team's engineering records. Find at least three security findings.

One finding is already known from Lab 7.3: the ORDER BY injection in `submission_repo.py`. Find two more by reasoning about what this endpoint exposes and what could go wrong — IDOR, data leakage, missing rate limiting, pagination without bounds, response schema exposure.

For each finding: state the location, the vulnerability class, the severity and reasoning, the required remediation, and the specific criterion that must be met before the PR can merge. The closure criterion must be verifiable by a second engineer who has not seen your fix.

---

## Task 3 — Security Test Matrix

Build a security test matrix for the CODING WAR submission pipeline.

For each test, specify:
- The threat or abuse case being tested
- The control that should prevent it and its location in the code
- The test type (unit, integration, security/penetration)
- A concrete test case with specific inputs
- A pass/fail criterion that another engineer can evaluate without reading your implementation

Cover at least seven distinct threats. Include at least one threat from each vulnerability chain you identified in Lab 7.1.

The pass/fail criterion is the hardest part to get right. "Security is maintained" is not a criterion. "Response status is 403 and the body does not contain the field `source_code`" is.

---

## Discussion

1. Your checklist includes an item a senior developer considers unnecessary process overhead. How do you evaluate their argument? What evidence would change your position?

2. PR-241's review minutes list three findings. The developer fixes one and argues the other two are acceptable given the sprint deadline. What is the correct response, and what documentation would you produce?

3. One test in your matrix fails intermittently — it passes eight times out of ten. What does this tell you about the underlying security control, and how do you respond?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Checklist | **30** | Every item is CODING WAR-specific and observable; no generic items |
| PR-241 review minutes | **30** | Three findings with location, severity, remediation, and independently verifiable closure criteria |
| Security test matrix | **30** | Seven tests; each has specific inputs and an observable pass/fail criterion |
| Discussion | **10** | Answers show practical engineering judgment |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.7.md](../solutions/sol-7.7.md) after completing the lab.*
