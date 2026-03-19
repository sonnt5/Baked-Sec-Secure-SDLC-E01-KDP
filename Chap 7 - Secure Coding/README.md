# Chapter 7 — Secure Coding Foundations

> **Bake Security into Modern Software Development**
> Lab Works — OWASP ASVS v5.0.0 Aligned
> Case study system: **CODING WAR** — Online Judge System

## Chapter Objectives

Chapter 7 shifts from *writing correct code* to *writing secure code* — not by memorising a list of vulnerabilities, but by building a mindset: every coding decision has a threat model behind it. The three questions you will learn to ask about every function you write or review:

1. Who controls the data entering this code?
2. What asset does this code protect or process?
3. What must always be true about this code's behaviour?

## Lab Roadmap

| Lab | Topic | Learning Objectives | Input | Main Artifact |
|-----|-------|---------------------|-------|--------------|
| [7.1](labs/lab-7.1.md) | Design Invariants → Code Contracts | Identify design assumptions from Ch.3–6; translate to verifiable code invariants; analyze vulnerability chains | Architecture + SDR Ch.3–6 | Code Contract Document + Invariant Map |
| [7.2](labs/lab-7.2.md) | Low-Level Flaws: Integer, Memory, TOCTOU | Analyze integer overflow, TOCTOU race condition; write correct replacements (ASVS V15.4) | `code/vulnerable/scoring.py`, `submission_service.py` | Vulnerability Analysis Report + Fixed Code |
| [7.3](labs/lab-7.3.md) | Injection Prevention: SQL, Command & Regex | Identify injection sinks; produce safe implementations; ASVS V1.2 assessment | `code/vulnerable/submission_repo.py`, `judge_service.py`, `code_validator.py` | Injection-Free Code + ASVS V1.2 Assessment |
| [7.4](labs/lab-7.4.md) | XSS, CSRF & Browser Security Headers | XSS output encoding across contexts; CSRF analysis; implement security headers and secure cookies (ASVS V3) | `code/vulnerable/security_headers.py`, `cookie_config.py` | Secure Web Code + ASVS V3 Assessment |
| [7.5](labs/lab-7.5.md) | Error Handling, Logging & Dependencies | Safe error model; privacy-safe log schema; dependency audit (ASVS V16, V15.2) | `code/vulnerable/error_handlers.py` | Safe Error Handler + Log Schema + Dep. Audit |
| [7.6](labs/lab-7.6.md) | Secure Coding Standard Profile & SAST Triage | Write SCSP; write custom Semgrep rules; complete SAST/SCA triage records (ASVS V15.1) | Ch.5–7 artifacts + `code/semgrep-rules/` | SCSP + Custom Semgrep Rules + Triage Records |
| [7.7](labs/lab-7.7.md) | Checklist, Code Review Minutes & Test Matrix | Vulnerability-class checklist; Code Review Minutes for PR-241; Security Test Matrix | Labs 7.1–7.6 findings | Review Checklist + Review Minutes + Test Matrix |

> [!NOTE]
> **Continuous scenario:** CODING WAR FastAPI/Python backend. Each lab takes real code scenarios from CODING WAR and applies secure coding analysis. The outputs of all 7 labs together form the evidence package for Security Testing (Ch.8).

## Directory Structure

```
chapter-07/
├── README.md
├── labs/
│   ├── lab-7.1.md   ← Design Invariants → Code Contracts
│   ├── lab-7.2.md   ← Integer Overflow, Memory Safety, TOCTOU
│   ├── lab-7.3.md   ← Injection Prevention
│   ├── lab-7.4.md   ← XSS, CSRF, Browser Security Headers
│   ├── lab-7.5.md   ← Error Handling, Logging, Dependencies
│   ├── lab-7.6.md   ← SCSP & SAST/SCA Triage
│   └── lab-7.7.md   ← Checklist, Code Review Minutes, Test Matrix
├── solutions/
│   └── sol-7.1.md … sol-7.7.md
├── code/
│   ├── vulnerable/
│   │   ├── scoring.py            ← float precision + atomic counter bug (Lab 7.2)
│   │   ├── submission_service.py ← TOCTOU temp file bug (Lab 7.2)
│   │   ├── submission_repo.py    ← SQL injection IS-01 + IS-02 (Lab 7.3)
│   │   ├── judge_service.py      ← Command injection IS-03 (Lab 7.3)
│   │   ├── code_validator.py     ← ReDoS IS-05 (Lab 7.3)
│   │   ├── security_headers.py   ← Missing security headers (Lab 7.4)
│   │   ├── cookie_config.py      ← Insecure cookie config (Lab 7.4)
│   │   └── error_handlers.py     ← Stack trace leakage + user enumeration (Lab 7.5)
│   ├── fixed/
│   │   ├── scoring.py            ← Decimal arithmetic + atomic Redis Lua script
│   │   ├── submission_service.py ← NamedTemporaryFile atomic write
│   │   ├── submission_repo.py    ← ORDER BY allowlist + ORM parameterization
│   │   ├── judge_service.py      ← shell=False + absolute paths + empty env
│   │   ├── code_validator.py     ← Regex timeout + linear patterns
│   │   ├── security_headers.py   ← SecurityHeadersMiddleware (CSP, HSTS, ...)
│   │   ├── cookie_config.py      ← HttpOnly + Secure + SameSite
│   │   └── error_handlers.py     ← Safe error handler + login enumeration fix
│   └── semgrep-rules/
│       └── coding-war-custom.yaml  ← Custom Semgrep rules (Lab 7.6)
└── assets/
    └── README.md
```

## How to Use This Chapter

### Reading `code/vulnerable/`

Each vulnerable file contains intentionally broken code with annotated bugs. Read the relevant file **before writing anything** for that lab. Understanding why the code is dangerous is more important than the fix itself.

### Writing your implementation

There is no starter code. You create your own files from scratch. Name them appropriately for the CODING WAR codebase structure (`app/services/`, `app/repositories/`, etc.).

### Consulting `code/fixed/`

Open these **only after you have written your own solution**. Your implementation does not need to match the reference — there is rarely a single correct approach. Use `fixed/` to compare reasoning, spot gaps, and calibrate your confidence.

### Consulting `solutions/`

Reference answers to the lab write-up questions. Attempt the lab fully before reading these. A reference solution reflects one valid perspective — yours may be equally valid or better suited to a specific context.

> The value of these labs is in the thinking, not the answers.

---

## OWASP ASVS v5.0.0 Coverage

| ASVS Chapter | Key Controls | Labs |
|-------------|-------------|------|
| V1 Encoding & Sanitization | V1.2 Injection Prevention (SQL, Command, ReDoS) | 7.3 |
| V2 Validation & Business Logic | V2.2 Input Validation | 7.1, 7.3 |
| V3 Web Frontend Security | V3.3 Cookies, V3.4 Headers, V3.5 CSRF | 7.4 |
| V11 Cryptography | V11.4 Password hashing | 7.2 |
| V15 Secure Coding & Architecture | V15.1 SCSP, V15.2 Dependencies, V15.4 Concurrency | 7.2, 7.5, 7.6 |
| V16 Logging & Error Handling | V16.2 Log redaction, V16.5 Error responses | 7.5 |

## Self-Assessment Checklist

When you have completed all seven labs, you should be able to answer yes to every question below.

| # | Question | Lab |
|---|----------|-----|
| 1 | Can you explain what makes a design assumption a code invariant — and what makes it not one? | 7.1 |
| 2 | Can you identify a vulnerability chain and explain why its combined severity exceeds any individual step? | 7.1 |
| 3 | Can you explain why floating-point arithmetic is inappropriate for scoring calculations? | 7.2 |
| 4 | Can you explain the TOCTOU gap and what property of your fix eliminates it? | 7.2 |
| 5 | Can you explain why ORDER BY cannot be parameterized, and what the correct alternative is? | 7.3 |
| 6 | Can you list the elements required for safe subprocess execution and why each matters? | 7.3 |
| 7 | Can you explain why XSS encoding is context-dependent and what differs between HTML and JS contexts? | 7.4 |
| 8 | Can you explain why Bearer JWT is inherently CSRF-safe and under what conditions it would not be? | 7.4 |
| 9 | Can you design an error response that provides a correlation ID without exposing internals? | 7.5 |
| 10 | Can you explain why login errors must be identical for valid and invalid users — including timing? | 7.5 |
| 11 | Can you write a Semgrep rule that targets a specific code contract violation? | 7.6 |
| 12 | Can you distinguish a True Positive from a Not-Exploitable SAST finding with justification? | 7.6 |
| 13 | Can you write a security test with a pass/fail criterion that another engineer can evaluate independently? | 7.7 |