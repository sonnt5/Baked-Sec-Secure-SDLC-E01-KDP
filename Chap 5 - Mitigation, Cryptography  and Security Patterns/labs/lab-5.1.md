# Lab 5.1 — Mitigation Planning: Reduce · Resist · Recover

> **Chapter 5 · Mitigations, Security Patterns, and Cryptography**
> Input: Threat List from Ch.4 | Output: Mitigation Register (table, ≥5 threats)

> [!NOTE]
> **Artifact for this lab:** Mitigation Register — a table consolidating mitigations for ≥5 threats from Ch.4, each entry with all 6 required fields. This is the central artifact connecting Threat Modeling (Ch.4) with Design (Ch.5).

## Learning Objectives

- Understand and apply the **Reduce · Resist · Recover** framework: classify mitigations by their architectural impact.
- Write a complete 6-field Mitigation Entry to Secure SDLC standard — a prerequisite for SDR gate review.
- Select a risk treatment strategy (Accept / Eliminate / Mitigate / Transfer) with clear justification.
- Link mitigations to STRIDE categories and specific assets from the Asset Register (Ch.4).

## Context

After completing the Threat Model (Ch.4), the team has: a Threat List (≥10 threats), a Risk Register with L×I scoring, Misuse Cases, and a Threat Profile (non/partial/fully mitigated). The next step is to move from *"what can go wrong"* to *"what will we do"* — Q3 of the 4-Question Framework. This lab builds the Mitigation Register, the foundational artifact for designing specific security architecture.

> [!NOTE]
> **Reminder:** Each mitigation is not an isolated feature. It is a design decision with trade-offs, placed at a specific point in the architecture, with verifiable evidence. A mitigation of *"add rate limiting"* is insufficient — you must state: rate limiting where (API Gateway), what threshold, what key (IP or user), and which test case provides evidence.

---

## Task 1 — Reduce · Resist · Recover Classification

Classify the following 12 mitigations and identify: does each primarily belong to **Reduce** (decrease attack probability), **Resist** (decrease impact when attacked), or **Recover** (detect + recover)? Each mitigation primarily belongs to one lever, but may also contribute to another — state the primary lever and the secondary lever (if applicable).

| # | Mitigation / Control | Primary Lever | Secondary Lever | Brief Explanation |
|---|---------------------|-------------|----------------|-------------------|
| 1 | Rate limiting 10 req/min/IP at the API Gateway for /auth/login | | | |
| 2 | JWT access token TTL = 15 minutes (instead of 30 days) | | | |
| 3 | Object-level authorization: check `submission.user_id == jwt.sub` on every API call | | | |
| 4 | Append-only audit log with hash-chain for all admin actions | | | |
| 5 | gVisor sandbox with a separate network namespace for the judge container | | | |
| 6 | Monitoring + alerting: alert when >50 failed logins/5 minutes from the same IP | | | |
| 7 | Encrypt submission source code at rest with AES-256-GCM + KMS | | | |
| 8 | Mandatory MFA for admins before any sensitive operation | | | |
| 9 | Generic error messages: only return `error_code`, no stack traces | | | |
| 10 | Daily database backup + quarterly tested restore drill | | | |
| 11 | Input schema validation at the API layer using Pydantic | | | |
| 12 | Incident response runbook: 30-minute SLA to isolate a compromised account | | | |

---

## Task 2 — Mitigation Register (Main Artifact)

Build a Mitigation Register for at least **5 Critical/High threats** from the Risk Register (Ch.4). Each entry must have all 6 fields. This is the main artifact of Lab 5.1.

> [!WARNING]
> All 6 fields of a Mitigation Entry are mandatory. Missing **Evidence** = the mitigation has no value for SDR. Missing **Residual Risk** = the reviewer cannot know what risk remains after the control is applied.

**Field reference:**

| Field | Description + Example from CODING WAR |
|-------|----------------------------------------|
| **① Target Threat & Risk** | Threat ID from Threat List + STRIDE category + Risk Level (Critical/High/Medium). *Example: TH-01 — Spoofing — Credential Stuffing on /auth/login — Risk: Critical (L=4, I=4)* |
| **② Asset / Boundary / Flow** | Specific asset from the Asset Register + Trust Boundary where the control is placed. *Example: Asset: User Credentials (Tier 2) at Trust Boundary B1 (Internet → Web Tier), Entry Point EP-1.1* |
| **③ Mechanism (Lever: Reduce/Resist/Recover)** | Specific pattern/control name + key parameters. *Example: Rate Limiting (Reduce) — max 5 requests/minute/IP at API Gateway; Account Lockout after 5 failures/10min → 15min lock* |
| **④ Injection Point** | Exact location in the system: source code file, infra config, CI/CD gate, WAF rule. *Example: app/middleware/rate_limit.py (FastAPI) + nginx rate_limit_zone config* |
| **⑤ Evidence** | Proof the control works: test case ID, log schema, alert rule, config check. *Example: tests/test_rate_limiting.py::test_login_rate_limit_returns_429_after_5_attempts; alert rule: login_failures > 50 in 5min* |
| **⑥ Residual Risk & Assumptions** | Risk remaining after applying the control + environmental/user assumptions required. *Example: Medium — attacker may bypass IP-based rate limit via distributed botnet; Assumption: CAPTCHA added before beta launch* |

### Entry 1: TH-01 / MC-01 — Credential Stuffing on /auth/login

| Field | Content |
|-------|---------|
| **① Target Threat & Risk** | |
| **② Asset / Boundary / Flow** | |
| **③ Mechanism (Lever)** | |
| **④ Injection Point** | |
| **⑤ Evidence** | |
| **⑥ Residual Risk & Assumptions** | |

### Entry 2: TH-02 / MC-03 — IDOR on /submissions/{id}

| Field | Content |
|-------|---------|
| **① Target Threat & Risk** | |
| **② Asset / Boundary / Flow** | |
| **③ Mechanism (Lever)** | |
| **④ Injection Point** | |
| **⑤ Evidence** | |
| **⑥ Residual Risk & Assumptions** | |

### Entry 3: TH-03 — DoS / RCE via Submissions

| Field | Content |
|-------|---------|
| **① Target Threat & Risk** | |
| **② Asset / Boundary / Flow** | |
| **③ Mechanism (Lever)** | |
| **④ Injection Point** | |
| **⑤ Evidence** | |
| **⑥ Residual Risk & Assumptions** | |

### Entry 4: TH-05 — Missing Admin Audit Log

| Field | Content |
|-------|---------|
| **① Target Threat & Risk** | |
| **② Asset / Boundary / Flow** | |
| **③ Mechanism (Lever)** | |
| **④ Injection Point** | |
| **⑤ Evidence** | |
| **⑥ Residual Risk & Assumptions** | |

### Entry 5: \[Threat 5 from Risk Register — team's choice\]

| Field | Content |
|-------|---------|
| **① Target Threat & Risk** | |
| **② Asset / Boundary / Flow** | |
| **③ Mechanism (Lever)** | |
| **④ Injection Point** | |
| **⑤ Evidence** | |
| **⑥ Residual Risk & Assumptions** | |

---

## Task 3 — Risk Treatment Strategy

For all 10 threats from the Risk Register (Ch.4), determine a risk treatment strategy. Not every threat requires immediate mitigation — some may be Accepted with clear conditions.

| Threat ID | Risk Level | Strategy | Justification (why this strategy?) | Review Trigger |
|-----------|-----------|----------|-------------------------------------|---------------|
| **TH-01** | Critical | Mitigate | Login flow cannot be eliminated but risk can be significantly reduced with rate limiting + lockout | When a new breach incident occurs or attack patterns change |
| **TH-02** | High | Mitigate | IDOR fix is simple, 1-day effort, residual risk near zero | When the authorization model changes |
| **TH-03** | Critical | Mitigate | Code execution cannot be eliminated — sandbox isolation is the practical solution | When upgrading sandbox technology |
| **TH-04** | Medium | | | |
| **TH-05** | High | | | |
| **TH-06** | | | | |
| **TH-07** | | | | |
| **TH-08** | | | | |
| **TH-09** | | | | |
| **TH-10** | | | | |

---

## Discussion Questions

1. If the team only has 1 sprint (2 weeks) to implement mitigations, which 3 items do you prioritize first? Justify your answer using the L×I framework and effort-to-impact ratio.

2. Threat TH-04 (verbose error messages) — some argue it should be Accepted because the impact is low; others want to Mitigate it immediately. Make the argument for both perspectives and provide a justified decision.

3. The mitigation "mandatory MFA for admins" — who is responsible for implementing it? The Dev team, Infra team, or Security team? What are the risks of not clearly assigning an owner in the Mitigation Register?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Reduce/Resist/Recover classification (12 controls) | **24** | Correct primary lever (1.5 pts) + explanation demonstrating understanding (0.5 pts) — not just guessing |
| Mitigation Register — 5 entries × 6 fields | **50** | Each entry: Evidence is testable not "will test later" (3 pts/entry), Residual Risk is realistic (2 pts/entry), Injection Point is specific not generic (2 pts/entry) |
| Risk Treatment Strategy (10 threats) | **16** | Strategy has justification (1 pt), review trigger is practical (0.6 pts) |
| Discussion Questions (3 questions) | **10** | Each question: reasoned argument, not just a one-sided answer |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-5.1.md](../solutions/sol-5.1.md)*
