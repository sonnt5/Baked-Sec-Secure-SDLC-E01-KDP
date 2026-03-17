# Chapter 7 — Secure Coding Foundations

> **Bake Security into Modern Software Development**
> Lab Works — OWASP ASVS v5.0.0 Aligned
> Case study system: **CODING WAR** — Online Judge System

> [!NOTE]
> **OWASP ASVS v5.0.0:** Chapter 7 labs map directly to OWASP ASVS v5.0.0: V1 Encoding & Sanitization, V2 Validation, V3 Web Frontend Security, V15 Secure Coding & Architecture, V16 Security Logging & Error Handling. Each lab produces a real artifact: Code Contract Document, Vulnerability Analysis Report, SAST/SCA Triage Record, Secure Coding Standard Profile, Code Review Minutes, Security Test Matrix.

## Chapter Objectives

Chapter 7 shifts from *"writing correct code"* to *"writing secure code"* — not by memorizing a list of vulnerabilities, but by building a mindset: every coding decision has a threat model behind it. Three axes: Data Flow & Untrusted Input, Assets & Risk, Design Invariants → Code Contracts.

## Lab Roadmap

| Lab | Topic | Learning Objectives | Input | Main Artifact |
|-----|-------|---------------------|-------|--------------|
| [7.1](labs/lab-7.1.md) | Design Invariants → Code Contracts | Identify design assumptions from Ch.3–6; translate to verifiable code invariants; analyze vulnerability chains | Architecture + SDR Ch.3–6 | Code Contract Document + Invariant Map |
| [7.2](labs/lab-7.2.md) | Low-Level Flaws: Integer, Memory, TOCTOU | Analyze integer overflow, buffer over-read, TOCTOU; refactor unsafe code (ASVS V15.4) | CODING WAR codebase scenarios | Vulnerability Analysis Report + Fixed Code |
| [7.3](labs/lab-7.3.md) | Injection Prevention: SQL, Command, Template, ReDoS | Identify injection sinks; apply parameterization; ASVS V1.2 compliance checklist | Submission pipeline code | Injection-Free Code + ASVS V1.2 Checklist |
| [7.4](labs/lab-7.4.md) | Web Issues: XSS, CSRF & Secure Cookies | XSS output encoding for 3 contexts; CSRF protection; cookie flags design (ASVS V3) | Auth + Scoreboard endpoints | Secure Web Code + ASVS V3 Assessment |
| [7.5](labs/lab-7.5.md) | Error Handling, Logging & Dependency Management | Safe error model; privacy-safe logging; dependency audit + SCA (ASVS V16, V15.2) | CODING WAR error/log code | Error Model Spec + Log Schema + Dep. Audit |
| [7.6](labs/lab-7.6.md) | Secure Coding Standard Profile & SAST/SCA Triage | SCSP document for CODING WAR; run SAST simulation; triage records (ASVS V15.1) | Ch.5–7 artifacts | Secure Coding Standard Profile + SAST/SCA Records |
| [7.7](labs/lab-7.7.md) | Checklist, Code Review Minutes & Test Matrix | Vulnerability-class checklist; Code Review Minutes for PR; Security Test Ideas Matrix | Labs 7.1–7.6 findings | Secure Code Review Checklist + Review Minutes + Test Matrix |

> [!NOTE]
> **Continuous scenario:** CODING WAR FastAPI/Python backend. Each lab takes real code scenarios from CODING WAR and applies secure coding analysis. The output of all 7 labs together = evidence package for Security Testing (Ch.8) and Bug Bar (Ch.8/9).

## Directory Structure

```
chapter-07/
├── README.md
├── labs/
│   ├── lab-7.1.md   ← Design Invariants → Code Contracts
│   ├── lab-7.2.md   ← Integer Overflow, Memory Safety, TOCTOU
│   ├── lab-7.3.md   ← Injection Prevention
│   ├── lab-7.4.md   ← XSS, CSRF, Secure Cookies
│   ├── lab-7.5.md   ← Error Handling, Logging, Dependency Management
│   ├── lab-7.6.md   ← SCSP & SAST/SCA Triage
│   └── lab-7.7.md   ← Checklist, Code Review Minutes, Test Matrix
├── solutions/
│   └── sol-7.1.md … sol-7.7.md
├── code/
│   ├── vulnerable/
│   │   ├── scoring.py              ← float precision + TOCTOU counter bugs (Lab 7.2)
│   │   └── submission_service.py   ← TOCTOU temp file bug (Lab 7.2)
│   ├── fixed/
│   │   ├── scoring.py              ← Decimal + atomic Redis Lua script
│   │   ├── submission_service.py   ← NamedTemporaryFile atomic
│   │   ├── submission_repo.py      ← SQL injection fix (allowlist + ORM)
│   │   ├── judge_service.py        ← Command injection fix (shell=False)
│   │   ├── code_validator.py       ← ReDoS fix (timeout)
│   │   ├── security_headers.py     ← SecurityHeadersMiddleware
│   │   ├── cookie_config.py        ← Secure cookie config
│   │   └── error_handlers.py       ← Safe error handler
│   └── semgrep-rules/
│       └── coding-war-custom.yaml  ← Custom Semgrep rules (Lab 7.6)
└── assets/
```

## OWASP ASVS v5.0.0 Coverage

| ASVS Chapter | Key Controls | Labs | Coverage |
|-------------|-------------|------|---------|
| V1 Encoding & Sanitization | V1.2 Injection Prevention (SQL, Command, Template, ReDoS, CSV) | Lab 7.3 | Full (IS-01–IS-05) |
| V2 Validation & Business Logic | V2.1 Documentation, V2.2 Input Validation, V2.3 Business Logic | Labs 7.1, 7.3, 7.7 | Full |
| V3 Web Frontend Security | V3.2 XSS, V3.3 Cookie setup, V3.4 Security headers, V3.5 CSRF | Lab 7.4 | Full |
| V9 Self-contained Tokens | V9.1 Token integrity (alg=none prevention), V9.2 Token content | Labs 7.5, 7.6, 7.7 | Full |
| V11 Cryptography | V11.2 Secure implementation, V11.4 Password hashing, V11.5 CSPRNG | Labs 7.2, 7.7 | Full |
| V15 Secure Coding & Architecture | V15.1 SCSP, V15.2 Dependencies, V15.3 Defensive coding, V15.4 Safe concurrency | Labs 7.2, 7.5, 7.6 | Full |
| V16 Security Logging & Error Handling | V16.2 General logging, V16.3 Security events, V16.5 Error handling | Lab 7.5 | Full |

## Self-Assessment Checklist — Chapter 7

| # | Criterion | Lab |
|---|-----------|-----|
| 1 | Code Contract Document: each invariant has an enforcement location with a specific file path — not "should be enforced" | 7.1 |
| 2 | Vulnerability Chain: the severity of the full chain is higher than any individual bug in the chain | 7.1 |
| 3 | Integer fix: uses `Decimal` type (not `float`) for scoring calculations | 7.2 |
| 4 | TOCTOU fix: uses `NamedTemporaryFile` with a controlled directory — not `os.path.exists` + `open` | 7.2 |
| 5 | SQL Injection fix (IS-01): EXPLAINS why `ORDER BY` cannot be parameterized — not just writing an allowlist | 7.3 |
| 6 | Command injection fix: `shell=False` AND absolute interpreter path AND empty env — all 3 elements | 7.3 |
| 7 | XSS fix: distinguishes HTML text context from JavaScript context — `json.dumps()` vs HTML entity encoding | 7.4 |
| 8 | CSRF analysis: Bearer JWT authentication is inherently CSRF-safe — NOT cookies | 7.4 |
| 9 | Error handler: user-not-found and wrong-password return IDENTICAL response (content + timing) | 7.5 |
| 10 | Log schema: "Never Log" column includes raw IP address (PII) — not just "passwords and tokens" | 7.5 |
| 11 | Dependency audit: `passlib` identified as effectively EOL (no updates since 2022) | 7.5 |
| 12 | SCSP: security-sensitive modules listed (ASVS V15.1.3) — not generic "all security code" | 7.6 |
| 13 | SAST Triage: closure criteria includes SAST re-run — not just "fix the code" | 7.6 |
| 14 | Security Exception: acceptance conditions BOUND the exception — not permanent | 7.6 |
| 15 | Test Matrix: pass/fail criteria are OBSERVABLE — "return 422" not "security verified" | 7.7 |
| 16 | Code Review Minutes: CWE references present for each finding | 7.7 |
| 17 | Evidence chain traceable: SCSP (7.6) → Checklist (7.7) → Review Minutes (7.7) → Test Matrix (7.7) | All |