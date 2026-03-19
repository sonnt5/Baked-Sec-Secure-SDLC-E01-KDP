# Lab 7.4 — XSS, CSRF & Browser Security Headers

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: `code/vulnerable/security_headers.py`, `code/vulnerable/cookie_config.py`
> Output: Secure Web Implementations + ASVS V3 Assessment

## Learning Objectives

- Reason about XSS output encoding as context-dependent, not a single rule.
- Analyse CSRF risk in the context of CODING WAR's authentication architecture.
- Implement browser security controls and document what each one prevents.

## Code Files

| File | Role |
|------|------|
| `code/vulnerable/security_headers.py` | Read before writing anything |
| `code/vulnerable/cookie_config.py` | Read before writing anything |
| `code/fixed/security_headers.py` | Reference implementation — consult after finishing your own |
| `code/fixed/cookie_config.py` | Reference implementation — consult after finishing your own |

---

## Task 1 — XSS Context Analysis

CODING WAR renders user-supplied content in several places. The required encoding depends entirely on where in the HTML document the data appears.

Analyse these three rendering contexts:

1. A problem title displayed inside `<div>{{ problem.title }}</div>`
2. A submission status embedded in an HTML attribute: `<span class="status-{{ status.value }}">`
3. A user's score assigned inside a `<script>` block: `var score = {{ user.score }};`

For each context: describe the attack payload that would succeed if the output is not encoded, and what encoding or protection is required to prevent it.

Then identify at least two additional rendering contexts in CODING WAR that you consider higher risk than these three, and explain why.

One question to answer before moving on: CODING WAR uses Jinja2. When is its auto-escaping sufficient, and when is it not?

---

## Task 2 — CSRF Analysis

CODING WAR's API uses Bearer JWT tokens in the `Authorization` header. A developer proposes adding CSRF tokens to all POST endpoints as a precaution.

Write a technical analysis — not a table, not a checklist — that addresses:
- Whether the proposal is necessary given Bearer JWT authentication and why
- Under what specific conditions CSRF protection would become necessary in CODING WAR
- What the correct mechanism would be in each scenario you identify

---

## Task 3 — Implement `security_headers.py`

Write a corrected implementation of the middleware.

Your implementation must set all headers required for ASVS V3.4 compliance. For any header where you have design decisions to make — especially Content-Security-Policy — document the security reasoning in the code itself. A reviewer reading your file should understand what each header does and why you configured it the way you did.

---

## Task 4 — Implement `cookie_config.py`

Write a corrected implementation of the cookie configuration.

The three attributes that are missing in the vulnerable version are each missing for a different reason with a different consequence. Document each attribute and the specific attack it prevents in your implementation — not in this document.

---

## Task 5 — ASVS V3 Assessment

Assess CODING WAR against these ASVS V3 controls after completing your implementations:

| Control | Description |
|---------|-------------|
| V3.2.1 | X-Content-Type-Options header present |
| V3.3.1 | Session cookies have Secure attribute |
| V3.3.2 | Session cookies have HttpOnly attribute |
| V3.3.3 | Session cookies use SameSite attribute |
| V3.4.1 | Content-Security-Policy header present with meaningful policy |
| V3.4.2 | Strict-Transport-Security header present |
| V3.5.1 | CSRF defences appropriate to the authentication architecture |

State Pass, Fail, or Partial with evidence. For anything not a full Pass, state what remains unaddressed.

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| XSS context analysis | **20** | Three contexts correct; additional contexts identified and justified; Jinja2 limitations addressed |
| CSRF analysis | **20** | Technically correct; conditions for needing protection are specific; appropriate mechanism for each scenario |
| `security_headers.py` | **30** | All ASVS V3.4 headers present; design decisions documented in code |
| `cookie_config.py` | **20** | All three attributes present; each one's purpose documented in code |
| ASVS V3 assessment | **10** | Evidence is specific; honest about gaps |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.4.md](../solutions/sol-7.4.md) after completing the lab.*
