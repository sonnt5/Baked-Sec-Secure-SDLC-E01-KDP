# Lab 4.1 — OWASP Step 1a: Threat Model Information & Privacy

> **Chapter 4 · Threat Modeling and Risk-Driven Prioritization**
> Input: SRS from Lab 2.3, Design from Lab 3 | Output: Threat Model Info block, Privacy Analysis table

> [!NOTE]
> **OWASP Note:** OWASP requires every Threat Model Document to begin with a "Threat Model Information" block: Application Name, Version, Description, Document Owner, Participants, Reviewer. This section is the most frequently skipped in practice, yet it is critical for traceability and governance.

## Learning Objectives

- Complete a full OWASP Threat Model Information block — the foundation of the entire threat model document.
- Distinguish Security (CIA/AAA) from Privacy — understand why security is necessary but not sufficient.
- Analyze CODING WAR data through the 5-step Privacy-by-Design Lifecycle.
- Build an adversarial mindset: shift from a *"builder mindset"* to an *"attacker mindset"*.

---

## Task 1 — OWASP Threat Model Information Block

Complete the Threat Model Information for CODING WAR. This is the mandatory header section of every OWASP-style Threat Model Document:

| Field | Value |
|-------|-------|
| **Application Name** | CODING WAR |
| **Application Version** | \[Fill in — e.g., v1.0-beta\] |
| **Application Description** | \[2–3 sentence description of CODING WAR: purpose, primary users, core features\] |
| **Document Owner** | \[Name of the person/team responsible for this Threat Model\] |
| **Participants (Threat Modelers)** | \[Team members involved — typically: Security Engineer, Backend Dev, Infra/DevOps\] |
| **Reviewer(s)** | \[Reviewer name — typically a Security Architect or CISO\] |
| **Date Created** | \[Date\] |
| **Last Updated** | \[Date\] |
| **Threat Modeling Methodology** | 4-Question Framework (Kohnfelder) + STRIDE + OWASP Threat Modeling Process |
| **Scope Summary** | \[One sentence: which components are IN scope, which are OUT of scope\] |
| **Related Documents** | SRS Lab 2.3 \| Architecture Design Lab 3.2 \| API Spec Lab 3.3 \| Deployment Design Lab 3.4 |

---

## Task 2 — Security vs. Privacy: Distinguishing the Concepts

Analyze 8 scenarios and classify each as: Security (S), Privacy (P), Both (B), or Neither (N).

| # | Scenario | S/P/B/N | Explanation |
|---|----------|---------|-------------|
| 1 | A hacker steals the database password hashes via SQL injection. | \[Fill in\] | \[Fill in\] |
| 2 | CODING WAR logs the contestant's IP address on every submission but has no deletion policy and does not disclose this in the ToS. | \[Fill in\] | \[Fill in\] |
| 3 | Admins can view all submitted source code after a contest ends, with no audit log. | \[Fill in\] | \[Fill in\] |
| 4 | The system requires a phone number at registration but never uses it. | \[Fill in\] | \[Fill in\] |
| 5 | Error messages from the judge engine expose internal stack traces and system paths. | \[Fill in\] | \[Fill in\] |
| 6 | CODING WAR shares the contestant email list with a sponsor without obtaining consent. | \[Fill in\] | \[Fill in\] |
| 7 | A session token does not expire after 30 days of inactivity. | \[Fill in\] | \[Fill in\] |
| 8 | System logs record all submitted source code in plaintext without access controls. | \[Fill in\] | \[Fill in\] |

---

## Task 3 — Privacy-by-Design Data Lifecycle

Analyze 4 types of data through the 5-stage lifecycle. For each stage, document the current mechanism, the privacy risk, and the proposed improvement.

### Data Type 1: Account information (username, email, password hash, IP)

| Lifecycle Stage | Current Mechanism | Privacy Risk | Proposed Improvement |
|----------------|------------------|--------------|---------------------|
| **📥 Collect** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🔍 Use** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🤝 Share** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🗄️ Retain** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🗑️ Delete** | \[Fill in\] | \[Fill in\] | \[Fill in\] |

### Data Type 2: Submitted source code (submissions)

| Lifecycle Stage | Current Mechanism | Privacy Risk | Proposed Improvement |
|----------------|------------------|--------------|---------------------|
| **📥 Collect** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🔍 Use** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🤝 Share** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🗄️ Retain** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🗑️ Delete** | \[Fill in\] | \[Fill in\] | \[Fill in\] |

### Data Type 3: Judging results & scores

| Lifecycle Stage | Current Mechanism | Privacy Risk | Proposed Improvement |
|----------------|------------------|--------------|---------------------|
| **📥 Collect** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🔍 Use** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🤝 Share** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🗄️ Retain** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🗑️ Delete** | \[Fill in\] | \[Fill in\] | \[Fill in\] |

### Data Type 4: Problem test cases

| Lifecycle Stage | Current Mechanism | Privacy Risk | Proposed Improvement |
|----------------|------------------|--------------|---------------------|
| **📥 Collect** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🔍 Use** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🤝 Share** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🗄️ Retain** | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **🗑️ Delete** | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Task 4 — Adversarial Mindset

For 3 CODING WAR features, document both the Builder and Attacker perspectives:

### Feature 1: New account registration

| 👷 Builder Mindset | 🔴 Attacker Mindset |
|-------------------|---------------------|
| \[Describe the normal flow — what a legitimate user does\] | *"As a malicious actor, I want to \[action\] so that \[harm\]."* — Specify: who the attacker is, how they abuse the feature, which asset is affected. |

### Feature 2: Submit a solution

| 👷 Builder Mindset | 🔴 Attacker Mindset |
|-------------------|---------------------|
| \[Describe the normal flow — what a legitimate user does\] | *"As a malicious actor, I want to \[action\] so that \[harm\]."* — Specify: who the attacker is, how they abuse the feature, which asset is affected. |

### Feature 3: Password reset

| 👷 Builder Mindset | 🔴 Attacker Mindset |
|-------------------|---------------------|
| \[Describe the normal flow — what a legitimate user does\] | *"As a malicious actor, I want to \[action\] so that \[harm\]."* — Specify: who the attacker is, how they abuse the feature, which asset is affected. |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Threat Model Information Block | **20** | All 11 fields completed; Description is clear; Scope Summary is accurate |
| Security vs. Privacy classification (8 scenarios) | **24** | Each scenario: correct classification (2 pts) + valid explanation (1 pt) |
| Privacy Lifecycle (4 data types × 5 stages) | **36** | Each stage: specific risk (2 pts), measurable improvement (2 pts) — partial credit for effort |
| Adversarial Mindset (3 features) | **20** | Each feature: complete misuse story (4 pts), asset identified (2 pts), specific harm (1 pt) |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-4.1.md](../solutions/sol-4.1.md)*
