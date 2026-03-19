# Lab 4.6 — OWASP Step 4: Risk Register, Prioritization & Q4 Review

> **Chapter 4 · Threat Modeling and Risk-Driven Prioritization**
> Input: Labs 4.1–4.5 | Output: Risk Register, Risk Heatmap, Mitigation Plan

## Learning Objectives

- Build a Risk Register from the Threat Profile (Lab 4.5) using L×I scoring.
- Create a 5×5 Risk Heatmap to visualize risk distribution.
- Build a Mitigation Plan using 3 strategies: Reduce Likelihood, Reduce Impact, Increase Detectability.
- Conduct the Q4 Evidence checklist — *"Did we do a good job?"*

---

## Task 1 — Risk Register with L×I Scoring

> [!NOTE]
> **OWASP Note:** Qualitative Risk = Likelihood × Impact. Use the DREAD Qualitative results from Lab 4.4: Likelihood is HIGH if: remote exploit, no auth needed, automatable. Impact is HIGH if: system takeover, admin access, PII exposure.

| Threat ID | STRIDE | Threat Summary | L (1–5) | I (1–5) | Risk Score | Risk Level | Mitigation Status (from Lab 4.5) | Residual Risk |
|-----------|--------|---------------|---------|---------|-----------|-----------|--------------------------------|--------------|
| **TH-01** | S | Credential stuffing /login | 4 | 4 | 16 | Critical | Partially mitigated | Medium — if controls added |
| **TH-02** | E | IDOR /submissions/{id} | 4 | 3 | 12 | High | NON-mitigated | Critical — fix immediately |
| **TH-03** | D | DoS via infinite loop submit | 4 | 4 | 16 | Critical | Partially mitigated | Medium |
| **TH-04** | I | Verbose error messages | 3 | 2 | 6 | Medium | Partially mitigated | Low |
| **TH-05** | R | Missing admin audit log | 3 | 4 | 12 | High | NON-mitigated | High |
| **MC-02** | E | RCE via malicious code | 3 | 5 | 15 | Critical | NON-mitigated | Critical — fix immediately |
| **TH-06** \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-07** \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-08** \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-09** \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-10** \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Task 2 — Risk Heatmap 5×5

Place each Threat ID in the appropriate cell based on its L and I scores:

| L \\ I → | I=1 Negligible | I=2 Minor | I=3 Moderate | I=4 Major | I=5 Critical |
|---------|--------------|----------|-------------|----------|-------------|
| **L=5** | Score: 5 · \[IDs\] | Score: 10 · \[IDs\] | Score: 15 · \[IDs\] | Score: 20 · \[IDs\] | Score: 25 · \[IDs\] |
| **L=4** | Score: 4 · \[IDs\] | Score: 8 · \[IDs\] | Score: 12 · \[IDs\] | Score: 16 · \[IDs\] | Score: 20 · \[IDs\] |
| **L=3** | Score: 3 · \[IDs\] | Score: 6 · \[IDs\] | Score: 9 · \[IDs\] | Score: 12 · \[IDs\] | Score: 15 · \[IDs\] |
| **L=2** | Score: 2 · \[IDs\] | Score: 4 · \[IDs\] | Score: 6 · \[IDs\] | Score: 8 · \[IDs\] | Score: 10 · \[IDs\] |
| **L=1** | Score: 1 · \[IDs\] | Score: 2 · \[IDs\] | Score: 3 · \[IDs\] | Score: 4 · \[IDs\] | Score: 5 · \[IDs\] |

> **Legend:** 🔴 Critical (≥15): Fix immediately · 🟠 High (9–14): Fix in sprint · 🔵 Medium (4–8): Backlog · 🟢 Low (1–3): Accept or monitor

---

## Task 3 — Mitigation Plan (Reduce L + I + D)

For Critical and High threats, build a 3-strategy Mitigation Plan:

### TH-01 / MC-01 — Credential Stuffing

| Strategy | Mitigation Actions | Implementation Notes | Owner + Sprint |
|----------|------------------|---------------------|---------------|
| **🛡️ Reduce L** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |
| **💥 Reduce I** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |
| **👁️ Increase D** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |

### TH-03 / MC-02 — DoS + RCE via Submission

| Strategy | Mitigation Actions | Implementation Notes | Owner + Sprint |
|----------|------------------|---------------------|---------------|
| **🛡️ Reduce L** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |
| **💥 Reduce I** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |
| **👁️ Increase D** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |

### TH-02 / MC-03 — IDOR on Submissions

| Strategy | Mitigation Actions | Implementation Notes | Owner + Sprint |
|----------|------------------|---------------------|---------------|
| **🛡️ Reduce L** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |
| **💥 Reduce I** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |
| **👁️ Increase D** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |

### TH-05 — Missing Admin Audit Log

| Strategy | Mitigation Actions | Implementation Notes | Owner + Sprint |
|----------|------------------|---------------------|---------------|
| **🛡️ Reduce L** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |
| **💥 Reduce I** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |
| **👁️ Increase D** | \[Fill in actions\] | \[Fill in technical details\] | \[Team + Sprint\] |

---

## Task 4 — Q4 Evidence Checklist (OWASP Step 4)

| Q4 OWASP Check | Status (✓ / ✗ / Partial) | Evidence / Notes |
|----------------|--------------------------|-----------------|
| Is there a diagram (DFD) showing the system being modeled? | \[Fill in\] | \[Fill in\] |
| Is there a documented threat list? | \[Fill in\] | \[Fill in\] |
| Is there a control list (countermeasures) for each threat? | \[Fill in\] | \[Fill in\] |
| Do all Critical and High threats have a Mitigation Plan with an owner? | \[Fill in\] | \[Fill in\] |
| Does the Threat Profile correctly classify Non/Partial/Fully mitigated? | \[Fill in\] | \[Fill in\] |
| Does the Asset Register cover all assets shown in the DFD? | \[Fill in\] | \[Fill in\] |
| Does every trust boundary have ≥1 analyzed threat? | \[Fill in\] | \[Fill in\] |
| Do Misuse Cases have measurable detection criteria (not just "anomaly")? | \[Fill in\] | \[Fill in\] |
| Are scope assumptions (in-scope/out-of-scope) documented? | \[Fill in\] | \[Fill in\] |
| Do accepted/deferred threats have a justification and monitoring plan? | \[Fill in\] | \[Fill in\] |
| Is the Threat Model linked to SRS requirements from Lab 2.3? | \[Fill in\] | \[Fill in\] |
| Is the DFD consistent with the Architecture Design from Lab 3.2? | \[Fill in\] | \[Fill in\] |
| Were Exit Points analyzed (not just Entry Points)? | \[Fill in\] | \[Fill in\] |
| Are External Dependencies affecting trust assumptions documented? | \[Fill in\] | \[Fill in\] |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Risk Register (≥10 threats, L×I scoring) | **25** | Scoring is reasonable, Mitigation Status is accurate from Lab 4.5 |
| Risk Heatmap 5×5 | **15** | ≥8 threats placed correctly, distribution is reasonable (not all Critical) |
| Mitigation Plan (4 threats × 3 strategies) | **35** | Actions are specific, techniques are realistic, owners and sprints are assigned |
| Q4 Evidence Checklist | **25** | 14 items assessed honestly, evidence/notes are meaningful (not all ✓ without explanation) |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-4.6.md](../solutions/sol-4.6.md)*
