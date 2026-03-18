# Lab 7.6 — Secure Coding Standard Profile & SAST/SCA Triage

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: Labs 7.1–7.5 artifacts + `code/semgrep-rules/coding-war-custom.yaml`
> Output: SCSP + Custom Semgrep Rules + SAST/SCA Triage Records

## Learning Objectives

- Write a Secure Coding Standard Profile that a team can actually use day-to-day.
- Write Semgrep rules that enforce specific code contracts — not just flag generic patterns.
- Apply structured triage to SAST and SCA findings, distinguishing exploitability from theoretical risk.

## Code Files

| File | Role |
|------|------|
| `code/semgrep-rules/coding-war-custom.yaml` | Reference rules — read to understand syntax and specificity expected, then write your own rules in a new file |

---

## Task 1 — Secure Coding Standard Profile

Write a Secure Coding Standard Profile for CODING WAR. This document would be given to every engineer who touches the codebase — it is a practical guide, not a compliance artifact.

It must cover:
- Which modules require heightened security review, with justification for each
- Rules developers must never violate in this codebase — with enough context that a new developer understands the *reason*, not just the directive
- How each rule is enforced automatically (tooling) versus what requires human judgment
- Remediation SLA for each severity level
- The process for requesting and approving exceptions

There is no required format or length. Write something a real team would find useful on a Monday morning.

---

## Task 2 — Custom Semgrep Rules

Read `code/semgrep-rules/coding-war-custom.yaml` to understand the syntax and the level of specificity expected in the rules. Then create your own rule file.

Write at least three rules that enforce code contracts you identified in Lab 7.1. Each rule must:
- Target a specific contract violation — not a generic pattern
- Include a `message` that tells a developer exactly what to fix and why
- Reference the relevant ASVS control and CWE

Test your rules against the CODING WAR codebase or synthetic test cases:
```bash
pip install semgrep --break-system-packages
semgrep scan --config your-rules.yaml app/
```

A rule that never fires is as useless as a rule that fires on everything. Document your test evidence.

---

## Task 3 — SAST Triage: Finding SF-001

You receive the following Semgrep finding:

```
Rule:     python.sqlalchemy.security.sqlalchemy-execute-raw-query
File:     app/repositories/submission_repo.py:147
Severity: ERROR
Code:     db.execute(f'SELECT * FROM submissions WHERE contest_id={contest_id} ORDER BY {sort_field} DESC')
```

Produce a complete triage record. Include:
- Your conclusion (True Positive, False Positive, or Not-Exploitable) with reasoning
- The severity of the issue and its justification
- The proposed remediation referencing your Lab 7.3 fix
- Closure criteria that a second engineer can verify independently — "the code has been fixed" is not a criterion

---

## Task 4 — SCA Triage: CVE-2024-33663

You receive the following `pip-audit` finding:

```
Package:     python-jose[cryptography] 3.3.0
CVE:         CVE-2024-33663
Severity:    HIGH
Description: Algorithm confusion attack — jwt.decode() is vulnerable to alg=none
             bypass if the algorithms parameter is not explicitly specified.
```

Produce a triage record. The critical part: assess whether this vulnerability is exploitable in CODING WAR's actual usage of the library. Examine how `jwt.decode()` is called in the codebase, not just what the CVE says in abstract.

---

## Task 5 — Security Exception

Account lockout — identified as a vulnerability chain step in Lab 7.1 — cannot be implemented this sprint because the Redis cluster architecture is being redesigned.

Write a Security Exception record for this deferred control. It must be written so that someone who was not in the original discussion can read it eighteen months later and understand: what risk is being accepted, why it cannot be fixed yet, what is being done to reduce the risk in the interim, and when the exception expires.

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| SCSP | **25** | Rules have context, not just directives; enforcement mechanism specified per rule; usable by a real team |
| Custom Semgrep rules | **35** | Each rule targets a specific contract; message is actionable; tested with evidence |
| SF-001 triage | **15** | Conclusion justified; closure criteria independently verifiable |
| CVE-2024-33663 triage | **15** | Exploitability assessed against actual call sites, not abstract CVE description |
| Security exception | **10** | Risk is quantified; compensating controls are real; expiration date present |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.6.md](../solutions/sol-7.6.md) after completing the lab.*
