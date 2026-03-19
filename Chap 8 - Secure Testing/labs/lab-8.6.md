# Lab 8.6 — DAST: OWASP ZAP API Scan

> **Chapter 8 · Security Testing Strategy and Toolchain Integration**
> Input: CODING WAR staging environment + `openapi.json`
> Output: DAST Scan Report + Deduplication Log

> [!WARNING]
> Active scanning must only run against the **staging** environment with synthetic data. Never run ZAP active scan against production. If you do not have a staging environment, use the simulated findings in Task 2 for triage.

## Learning Objectives

- Understand why DAST finds a different category of vulnerability than SAST.
- Configure ZAP correctly for an API-first application using the OpenAPI specification.
- Triage DAST findings and deduplicate against SAST results.
- Reason about authenticated vs unauthenticated scanning and its coverage implications.

## Code Files

| File | Role |
|------|------|
| `code/config/zap-config.yaml` | ZAP scan configuration |

---

## Task 1 — ZAP Configuration and Baseline Scan

```bash
docker pull zaproxy/zap-stable

docker run --rm \
  -v $(pwd):/zap/wrk \
  zaproxy/zap-stable \
  zap-api-scan.py \
  -t http://staging:8000/openapi.json \
  -f openapi \
  -c /zap/wrk/code/config/zap-config.yaml \
  -r /zap/wrk/zap-baseline-report.html
```

Review `code/config/zap-config.yaml` before running. Understand what is excluded and why before you can interpret the scan results correctly.

Before starting the scan, answer: why does specifying the OpenAPI spec (`-f openapi`) change the quality of ZAP's findings compared to plain crawling? What endpoints would ZAP miss without it?

---

## Task 2 — Active Scan and Findings Triage

```bash
docker run --rm \
  -v $(pwd):/zap/wrk \
  zaproxy/zap-stable \
  zap-api-scan.py \
  -t http://staging:8000/openapi.json \
  -f openapi \
  -c /zap/wrk/code/config/zap-config.yaml \
  -a \
  -r /zap/wrk/zap-active-report.html
```

For each finding you receive (or use the simulated findings below), produce a triage record. For each: state your conclusion, justify it technically, reference any related SAST finding, and define independently verifiable closure criteria.

**Simulated findings (use if no staging environment):**

| ID | Alert | Risk | Endpoint |
|----|-------|------|----------|
| DF-001 | Missing Anti-CSRF Tokens | Medium | `POST /api/v1/submissions` |
| DF-002 | SQL Injection | High | `GET /api/v1/submissions?sort=score` |
| DF-003 | Content Security Policy Header Not Set | Medium | All HTML responses |
| DF-004 | X-Frame-Options Header Not Set | Medium | All HTML responses |
| DF-005 | Cookie Without Secure Flag | Medium | `/api/v1/auth/login` |
| DF-006 | Server Leaks Version Information | Low | All responses |

DF-001 will test your understanding of CODING WAR's authentication architecture. Think carefully about whether CSRF is a real risk for this application before concluding it is a False Positive — state the specific technical reason.

---

## Task 3 — Deduplication Log

SAST and DAST sometimes find the same vulnerability from different angles. When they do, two independent tools confirming the same issue raises the confidence level and combined severity.

Review your SAST findings from Lab 8.3. Identify any findings where DAST and SAST point to the same underlying vulnerability. For each match: document both evidence sources, state the combined confidence level, and explain whether the deduplication changes the priority or remediation.

Also identify findings that DAST caught and SAST missed. What does this tell you about the structural difference in what each technique can detect?

---

## Task 4 — Authenticated Scanning Analysis

ZAP can be configured to send a JWT token with every request. Without authentication, ZAP can only reach public endpoints.

Analyse CODING WAR's attack surface: what percentage of the threat model's most critical threats are reachable without authentication? What would an authenticated ZAP scan add to the coverage? What are the risks of providing a real admin JWT in a scan configuration file, and how would you mitigate them?

---

## Discussion

1. The DAST scan finds a SQL injection in the sort field — the same issue identified by SAST in Lab 8.3. The developer argues that because SAST already caught it, the DAST finding can be closed as Duplicate without additional action. Evaluate this argument.

2. ZAP's active scan runs destructive tests (it submits injection payloads and may create records). In staging, a previous active scan left 200 test submissions in the database that contaminated the subsequent performance test. What process controls prevent this?

3. The coverage matrix from Lab 8.1 shows TH-08 (JWT algorithm confusion) as covered by a unit test. ZAP cannot test JWT algorithm confusion because it requires crafting a specific token. What does this reveal about the limits of DAST as a tool for this category of vulnerability?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| ZAP configuration analysis | **20** | OpenAPI importance explained; config choices understood before running |
| DAST findings triage | **35** | DF-001 CSRF conclusion technically justified; all 6 findings triaged with closure criteria |
| Deduplication log | **25** | SAST vs DAST matches identified; combined confidence reasoning; coverage gap analysis |
| Authenticated scanning analysis | **10** | Realistic estimate of unauthenticated coverage; JWT risk and mitigation described |
| Discussion | **10** | Answers show practical judgment |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-8.6.md](../solutions/sol-8.6.md) after completing the lab.*
