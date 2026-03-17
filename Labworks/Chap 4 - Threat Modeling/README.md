# Chapter 4 — Threat Modeling and Risk-Driven Prioritization

> **Bake Security into Modern Software Development**
> Lab Works · OWASP-Enhanced Edition
> Case study system: **CODING WAR** — Online Judge System

> [!NOTE]
> **OWASP Note:** This chapter follows the OWASP Threat Modeling Process (owasp.org/www-community/Threat_Modeling_Process), incorporating: Exit Points, Trust Levels, External Dependencies, Threat Trees, the DREAD Qualitative Model, Threat Profile (non/partial/fully mitigated), STRIDE Mitigation Techniques, and Lab 4.7 — OWASP-Style Full Threat Model Document.

## Chapter Objectives

Chapter 4 marks the shift from a builder mindset to an adversarial one. Students practice the complete OWASP 4-step process:
1. **Scope** — DFD + Entry/Exit Points + Trust Levels + Assets
2. **Determine Threats** — STRIDE + Threat Trees + Use/Misuse Cases
3. **Countermeasures & Mitigation** — mapping, threat profile
4. **Assess** — Q4 evidence review + SDR readiness

## Lab Roadmap

| Lab | Topic | Learning Objectives | Input | Main Output |
|-----|-------|---------------------|-------|-------------|
| [4.1](labs/lab-4.1.md) | OWASP Step 1a: Threat Model Information & Privacy | Document the Threat Model Info block; Privacy-by-Design lifecycle; adversarial mindset | SRS Lab 2.3, Design Lab 3 | Threat Model Info block, Privacy Analysis table |
| [4.2](labs/lab-4.2.md) | OWASP Step 1b: DFD + Entry/Exit Points + Trust Levels | DFD-0/DFD-1; Entry + Exit Points (OWASP); Trust Levels table; External Dependencies | Architecture Lab 3.2 | DFD-0, DFD-1, Entry/Exit table, Trust Levels, Ext. Deps |
| [4.3](labs/lab-4.3.md) | OWASP Step 1c: Assets + Attack Surface Mapping | Asset Register with Trust Level cross-ref; Attack Surface Map; Entry Point Control Matrix | DFD Lab 4.2 | Asset Register, Attack Surface Map, EP Control Matrix |
| [4.4](labs/lab-4.4.md) | OWASP Step 2: STRIDE + Threat Trees + DREAD Qualitative | STRIDE per element; Threat Tree for critical threat; DREAD Qualitative scoring; Use-Misuse graph | Assets + DFD 4.2–4.3 | Threat List, Threat Tree diagram, DREAD table |
| [4.5](labs/lab-4.5.md) | OWASP Step 3: Countermeasures, Misuse Cases & Threat Profile | STRIDE Mitigation Techniques; Misuse/Abuse Cases (full template); Threat Profile (non/partial/fully mitigated) | Threat List Lab 4.4 | Countermeasure Map, ≥4 Misuse Cases, Threat Profile |
| [4.6](labs/lab-4.6.md) | OWASP Step 4: Risk Register, Prioritization & Q4 Review | Risk Heatmap (L×I); Mitigation Plan (L/I/D strategies); Q4 Evidence checklist | Labs 4.1–4.5 | Risk Register, Risk Heatmap, Mitigation Plan |
| [4.7](labs/lab-4.7.md) | OWASP Full Threat Model Document | Assemble all outputs → complete OWASP-style Threat Model Document for the SDR gate | All Labs 4.1–4.6 | Threat Model Document (OWASP format) |

> [!NOTE]
> **Continuous scenario:** All 7 labs use the CODING WAR system. Lab 4.7 is the synthesis artifact — it packages the complete output of Labs 4.1–4.6 into a finished Threat Model Document ready for the SDR gate.

## Directory Structure

```
chapter-04/
├── README.md
├── labs/
│   ├── lab-4.1.md   ← OWASP Step 1a: Threat Model Info & Privacy
│   ├── lab-4.2.md   ← OWASP Step 1b: DFD + Entry/Exit + Trust Levels
│   ├── lab-4.3.md   ← OWASP Step 1c: Assets + Attack Surface
│   ├── lab-4.4.md   ← OWASP Step 2: STRIDE + Threat Trees + DREAD
│   ├── lab-4.5.md   ← OWASP Step 3: Countermeasures + Misuse Cases
│   ├── lab-4.6.md   ← OWASP Step 4: Risk Register + Q4 Review
│   └── lab-4.7.md   ← OWASP Full Threat Model Document
├── solutions/
│   ├── sol-4.1.md … sol-4.7.md
└── assets/

```

## Self-Assessment Checklist — Chapter 4

| # | Criterion | Lab |
|---|-----------|-----|
| 1 | Threat Model Information block has all 11 fields — from Application Name through Related Documents | 4.1 |
| 2 | DFD uses correct OWASP notation: rectangle (external entity), circle (process), parallel lines (data store), dashed boundary | 4.2 |
| 3 | Trust Levels table has ≥6 levels cross-referenced to both Entry Points AND Assets | 4.2 |
| 4 | Exit Points are analyzed (not skipped) — ≥6 XPs with potential threats identified | 4.2 |
| 5 | External Dependencies table has ≥5 dependencies with trust assumptions documented | 4.2 |
| 6 | Asset Register has Trust Level cross-reference for each asset — who has access? | 4.3 |
| 7 | STRIDE analysis covers all 6 categories for ≥3 DFD elements | 4.4 |
| 8 | Threat Tree has ≥3 branches with AND/OR notation and a countermeasure for each leaf | 4.4 |
| 9 | DREAD Qualitative scoring uses structured questions (remote? auth needed? automatable? system takeover?) | 4.4 |
| 10 | OWASP STRIDE Mitigation Techniques are mapped specifically to the CODING WAR context | 4.5 |
| 11 | Misuse Cases include a "Complements Code Review" field pointing to code patterns to review | 4.5 |
| 12 | Threat Profile correctly classifies threats into 3 tiers: Non/Partially/Fully mitigated with evidence | 4.5 |
| 13 | Risk Heatmap has ≥8 threats placed with a reasonable distribution (not all Critical) | 4.6 |
| 14 | Q4 checklist (14 items) reflects an honest assessment (not all ✓) | 4.6 |
| 15 | Complementing Code Review table identifies specific components and code patterns to check | 4.7 |
| 16 | Executive Summary can be read and understood by a PM or CISO without a technical background | 4.7 |
| 17 | SDR Gate Verdict is justified — not just "READY" without explanation | 4.7 |

## Lab Materials

| File | Description | Used In |
|------|-------------|---------|
