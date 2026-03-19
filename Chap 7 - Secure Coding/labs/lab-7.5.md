# Lab 7.5 — Error Handling, Logging & Dependency Management

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: `code/vulnerable/error_handlers.py`
> Output: Safe Error Handler + Privacy-Safe Log Schema + Dependency Audit

## Learning Objectives

- Design error responses that give users enough information to act without exposing internals.
- Design a logging schema that enables forensic investigation without creating new privacy risks.
- Conduct a dependency audit and reason about exploitability in context — not just CVE existence.

## Code Files

| File | Role |
|------|------|
| `code/vulnerable/error_handlers.py` | Read before writing anything |
| `code/fixed/error_handlers.py` | Reference implementation — consult after finishing your own |

---

## Task 1 — Diagnose the Vulnerabilities

Read `code/vulnerable/error_handlers.py`. It contains two distinct security problems.

For each problem: identify the root cause, describe what an attacker can do with it, and explain what information is exposed that should not be.

---

## Task 2 — Implement the Error Handler

Write a production-quality error handler for CODING WAR.

What your implementation must accomplish:
- Users receive enough information to understand what happened and what to do
- No internal system details reach the client response under any circumstances
- Every unhandled exception produces a short correlation reference that appears in both the internal log and the external response — enabling an operator to locate the full detail without the client knowing any of it
- Login errors must not reveal whether a given email address exists in the system

How you accomplish these things is your decision. Document your approach in the code.

---

## Task 3 — Privacy-Safe Logging Schema

Design a logging schema that an incident responder could use to reconstruct an attack sequence from logs alone — without referring to application code or the database.

Define the schema for at least five event categories relevant to CODING WAR. For each:
- The event name and when it fires
- Every field that is logged, with its type and source
- Every field that must never appear in logs under any circumstances, with the reason

Your schema will be evaluated on two dimensions: does it enable forensic investigation, and does it avoid creating new risk through the logs themselves?

---

## Task 4 — Dependency Audit

Audit the CODING WAR direct dependencies listed below. Assess each for security risk.

| Package | Version |
|---------|---------|
| `fastapi` | 0.109.2 |
| `python-jose[cryptography]` | 3.3.0 |
| `passlib[argon2]` | 1.7.4 |
| `cryptography` | 42.0.2 |
| `sqlalchemy[asyncio]` | 2.0.27 |

For each issue you find: assess whether the vulnerability is actually exploitable given CODING WAR's specific usage of the library, and propose a concrete remediation with a realistic timeline. Do not just list CVE IDs — the output should read like a brief to an engineering lead who needs to decide what to fix this sprint.

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Vulnerability diagnosis | **15** | Both bugs identified; attack scenarios are concrete, not generic |
| Error handler implementation | **35** | No internals in response; correlation ID bridges log and response; login enumeration prevented |
| Logging schema | **30** | Five categories defined; forensic reconstruction enabled; "never log" fields have specific reasons |
| Dependency audit | **20** | Exploitability assessed against actual CODING WAR usage; remediation is actionable with timeline |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.5.md](../solutions/sol-7.5.md) after completing the lab.*
