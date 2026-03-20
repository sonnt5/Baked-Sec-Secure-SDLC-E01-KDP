# Chapter 8 — Security Testing Strategy and Toolchain Integration

> **Bake Security into Modern Software Development**
> Lab Works — Hands-On with Real Security Tools
> Case study system: **CODING WAR** — Online Judge System

## Chapter Objectives

Chapter 8 transforms security testing from theory into practice. Each lab runs real tools on the CODING WAR codebase — not learning *about* the toolchain, but *running* it, interpreting output, triaging findings, and integrating everything into CI/CD. Evidence from all 8 labs feeds into the Bug Bar and FSR in Chapter 9.

## Lab Roadmap

| Lab | Topic | Input | Main Artifact |
|-----|-------|-------|--------------|
| [8.1](labs/lab-8.1.md) | Design-Driven Test Planning | Threat Model Ch.4 + SDR Ch.6 | Security Test Plan + Coverage Matrix |
| [8.2](labs/lab-8.2.md) | Security Unit Testing (pytest) | CODING WAR FastAPI application | pytest security test suite |
| [8.3](labs/lab-8.3.md) | SAST: Semgrep + Bandit + Custom Rules | CODING WAR source code | SAST Report + Custom Rules + Triage Records |
| [8.4](labs/lab-8.4.md) | Supply Chain: SCA + Container + Secrets | requirements.txt + Dockerfile | SCA Report + SBOM + Secrets Scan Report |
| [8.5](labs/lab-8.5.md) | IaC Security: Trivy + Checkov | k8s/*.yaml + Dockerfile | IaC Scan Report + Misconfig Findings |
| [8.6](labs/lab-8.6.md) | DAST: OWASP ZAP API Scan | CODING WAR staging env + openapi.json | DAST Scan Report + Dedup Log |
| [8.7](labs/lab-8.7.md) | Fuzzing: Hypothesis + Atheris | Submission validator + score calculator | Fuzz Harnesses + Crash Reports |
| [8.8](labs/lab-8.8.md) | Penetration Testing: Scoping & Findings | CODING WAR staging env | Pentest RoE + Findings Report |

---

## Directory Structure

```
chapter-08/
├── README.md
├── labs/
│   ├── lab-8.1.md
│   ├── lab-8.2.md
│   ├── lab-8.3.md
│   ├── lab-8.4.md
│   ├── lab-8.5.md
│   ├── lab-8.6.md
│   ├── lab-8.7.md
│   └── lab-8.8.md
├── solutions/
│   ├── sol-8.1.md
│   ├── sol-8.2.md
│   ├── sol-8.3.md
│   ├── sol-8.4.md
│   ├── sol-8.5.md
│   ├── sol-8.6.md
│   ├── sol-8.7.md
│   └── sol-8.8.md
├── code/
│   │
│   ├── .github/
│   │   └── workflows/
│   │       ├── security-tests.yml          ← Lab 8.2: pytest -m security on every PR
│   │       ├── sast.yml                    ← Lab 8.3: Semgrep (PR diff) + Bandit (nightly)
│   │       ├── supply-chain.yml            ← Lab 8.4: pip-audit + detect-secrets + Trivy image
│   │       ├── iac-scan.yml                ← Lab 8.5: Trivy config + Checkov on k8s/Dockerfile
│   │       └── dast.yml                    ← Lab 8.6: ZAP baseline (nightly) + active (weekly)
│   │
│   ├── config/
│   │   ├── trivy-config.yaml               ← Labs 8.4, 8.5: Trivy severity thresholds + ignore format
│   │   └── zap-config.yaml                 ← Lab 8.6: ZAP rules, active-scan-paths, exclude-paths
│   │
│   ├── semgrep-rules/
│   │   └── custom-coding-war.yml           ← Lab 8.3: 8 custom rules (syntax reference + SF-001–SF-006)
│   │
│   └── reference/                          ← Open ONLY after finishing your own implementation
│       ├── tests/
│       │   ├── conftest.py                 ← Lab 8.2: fixtures, markers, token helpers
│       │   ├── fixtures/
│       │   │   └── payloads.py             ← Lab 8.2: SQL injection, XSS, boundary payloads
│       │   └── security/
│       │       ├── test_authentication.py  ← Lab 8.2: TC-Auth-001 to 005
│       │       ├── test_authorization.py   ← Lab 8.2: TC-IDOR-001 to 003
│       │       ├── test_rate_limiting.py   ← Lab 8.2: TC-RateLimit-001 to 002
│       │       ├── test_crypto.py          ← Lab 8.2: TC-Crypto-001 to 003
│       │       └── test_input_validation.py ← Lab 8.2: TC-Input-001 (parametrized)
│       └── fuzz/
│           ├── test_hypothesis.py          ← Lab 8.7: Hypothesis property-based tests
│           └── fuzz_submission.py          ← Lab 8.7: Atheris coverage-guided fuzz harness
└── assets/
```

---

## How to Use This Chapter

### Labs 8.1, 8.3–8.6, 8.8 — analysis and tooling labs

These labs are completed with write-up answers and tool output. No code files need to be created. The `code/` folder provides configuration files and CI workflows to read, run, and analyse.

### Labs 8.2 and 8.7 — coding labs

These labs require you to write code from scratch:

- **Lab 8.2:** Write your own pytest security test suite. Create your own `conftest.py` and test files — do not copy from `code/reference/tests/`.
- **Lab 8.7:** Write your own Hypothesis property tests and Atheris fuzz harness — do not copy from `code/reference/fuzz/`.

### `code/reference/` — consult after finishing

Open `code/reference/` only after you have completed your own implementation. Your approach may differ and still be correct. Use the reference to compare reasoning, identify gaps, and calibrate your confidence.

### `solutions/` — consult after finishing the lab

Reference answers to the write-up questions in each lab. Attempt the lab fully before reading.

> The value of these labs is in running the tools and reasoning about the output — not in producing the expected answer.

---

## Toolchain Summary

| Tool | Labs | What it tests |
|------|------|--------------|
| pytest + httpx | 8.2 | Security unit tests — authentication, IDOR, rate limiting, crypto, input validation |
| Semgrep | 8.3 | SAST — Code Contract violations, injection patterns, hardcoded secrets |
| Bandit | 8.3 | SAST — Python-specific security antipatterns |
| pip-audit | 8.4 | SCA — CVEs in Python dependencies |
| Trivy | 8.4, 8.5 | Container image CVEs + IaC misconfigurations |
| detect-secrets | 8.4 | Hardcoded secrets in source and history |
| Checkov | 8.5 | IaC policy violations in Kubernetes + Dockerfile |
| OWASP ZAP | 8.6 | DAST — runtime API behaviour, injection, headers |
| Hypothesis | 8.7 | Property-based testing — security invariants |
| Atheris | 8.7 | Coverage-guided fuzzing — crash finding |

## OWASP ASVS v5.0.0 Coverage

| ASVS Chapter | Key Controls | Labs |
|-------------|-------------|------|
| V2 Validation | V2.2 Input validation testing | 8.2 |
| V6 Authentication | V6.3 Credential stuffing prevention | 8.2, 8.6 |
| V8 Authorization | V8.3.1 IDOR prevention | 8.2 |
| V11 Cryptography | V11.2, V11.4 Crypto implementation | 8.2 |
| V13 API | V13.2 RESTful verification | 8.6 |
| V14 Configuration | V14.2 Dependency management | 8.4 |
| V15 Secure Coding | V15.1 SCSP, V15.2 Dependencies | 8.3, 8.4 |
| V16 Logging | V16.5 Error handling | 8.2, 8.7 |

## Self-Assessment Checklist

| # | Question | Lab |
|---|----------|-----|
| 1 | Can you build a Coverage Matrix linking each threat to a specific test technique and evidence artifact? | 8.1 |
| 2 | Can you state the security oracle for a test — what adverse behaviour it prevents? | 8.2 |
| 3 | Can you write a Semgrep rule enforcing a specific Code Contract from Ch.7? | 8.3 |
| 4 | Can you distinguish a True Positive from a False Positive SAST finding with technical justification? | 8.3 |
| 5 | Can you assess whether a CVE is exploitable in CODING WAR's specific usage of a library? | 8.4 |
| 6 | Can you triage an IaC misconfiguration against the actual deployment context? | 8.5 |
| 7 | Can you explain why CSRF (DF-001) is a False Positive given Bearer JWT authentication? | 8.6 |
| 8 | Can you write a Hypothesis property encoding a security invariant, not just a correctness check? | 8.7 |
| 9 | Can you write a pentest finding with CVSS score, reproduction steps, and evidence? | 8.8 |
| 10 | Can you trace every Coverage Matrix row to an actual test artifact? | All |