# Chapter 5 — Mitigations, Security Patterns, and Cryptography

> **Bake Security into Modern Software Development**
> Case study system: **CODING WAR** — Online Judge System

## Chapter Objectives

Chapter 5 closes the loop from threat modeling to verifiable mitigations. Rather than simply listing controls, students build real artifacts: a Mitigation Register, an Architecture Hardening Report, a Pattern Application Worksheet, a Secure Design Review, a Crypto Decision Record, and a Security Architecture Specification — deliverables that appear in real software projects.

## Lab Roadmap

| Lab | Topic | Learning Objectives | Input | Main Artifact |
|-----|-------|---------------------|-------|--------------|
| [5.1](labs/lab-5.1.md) | Mitigation Planning: Reduce · Resist · Recover | Apply the Reduce/Resist/Recover framework; write a 6-field Mitigation Register; choose risk treatment strategies | Threat List Ch.4 | Mitigation Register (table, ≥5 threats) |
| [5.2](labs/lab-5.2.md) | Structural Mitigations: Architecture Hardening | Attack Surface Audit; Windows of Vulnerability; Data Minimization; PEP/PDP design; Architecture Hardening | Architecture Ch.3 + DFD Ch.4 | Architecture Hardening Report + Annotated Diagram |
| [5.3](labs/lab-5.3.md) | Security Design Patterns: Pattern Application Worksheet | Identify and apply 15 patterns (5 groups); analyze trade-offs; link patterns to specific threats | Design artifacts Ch.3–5.2 | Pattern Application Worksheet + Pattern Selection Matrix |
| [5.4](labs/lab-5.4.md) | Anti-Patterns & Secure Design Review | Detect 4 anti-patterns in CODING WAR design; write a Secure Design Review Report | Design + Pattern labs 5.2–5.3 | Anti-Pattern Report + SDR Report |
| [5.5](labs/lab-5.5.md) | Crypto Toolbox — Decision Record | Select correct crypto primitives for each goal; identify crypto mistakes; write a Crypto Decision Record | Threat List + Architecture | Crypto Decision Record (CDR) |
| [5.6](labs/lab-5.6.md) | Applying Crypto to Architecture | TLS/mTLS config; Envelope Encryption design; Opaque IDs; Distributed Identity — produce Security Architecture Specification | CDR Lab 5.5 + Architecture | Security Architecture Specification (SAS) |

> [!NOTE]
> **Continuous scenario:** All labs continue with CODING WAR. The outputs of Ch.4 (Threat List, Risk Register, DFD with trust boundaries, Asset Register) are the direct inputs for Ch.5. Each artifact in Ch.5 feeds into the next lab, and all artifacts accumulate into the Security Architecture Specification in Lab 5.6.

## Directory Structure

```
chapter-05/
├── README.md
├── labs/
│   ├── lab-5.1.md   ← Mitigation Planning
│   ├── lab-5.2.md   ← Architecture Hardening
│   ├── lab-5.3.md   ← Security Design Patterns
│   ├── lab-5.4.md   ← Anti-Patterns & SDR Report
│   ├── lab-5.5.md   ← Crypto Toolbox & CDR
│   └── lab-5.6.md   ← Applying Crypto: SAS
├── solutions/
│   ├── sol-5.1.md … sol-5.6.md
└── assets/
```

## Self-Assessment Checklist — Chapter 5

| # | Criterion — verify by evidence, not "I think it's correct" | Lab |
|---|-------------------------------------------------------------|-----|
| 1 | Mitigation Register: each entry has all 6 fields; Evidence field contains a real test ID, not "will test later" | 5.1 |
| 2 | Risk Treatment Strategy: every "Accept" decision has a monitoring plan — not just "accept and forget" | 5.1 |
| 3 | Attack Surface Score decreased after hardening — specific numbers, not just "improved" | 5.2 |
| 4 | Data Minimization: each surface has an implementation detail — Pydantic field exclusion / log redaction / opaque ID — not just a stated principle | 5.2 |
| 5 | PEP vs PDP correctly distinguished: no component both enforces AND decides in the same unit (mixed responsibility) | 5.2 |
| 6 | Pattern Selection Matrix: chosen pattern is linked to a specific threat — not applied just because it's a "best practice" | 5.3 |
| 7 | Defense in Depth: 5+ independent layers — if one layer fails, the attack does not automatically succeed | 5.3 |
| 8 | Anti-pattern analysis: explanation of why it is a structural vulnerability, not just a bug | 5.4 |
| 9 | SDR Report has a realistic verdict: CODING WAR currently has Confused Deputy + IDOR — it should not be APPROVED without conditions | 5.4 |
| 10 | Crypto Mistake Analysis: each mistake has a specific attack scenario — not just "because the crypto library docs say so" | 5.5 |
| 11 | CDR: Consequences include real negative trade-offs — not just a list of positives | 5.5 |
| 12 | Envelope Encryption: DEK is UNIQUE per submission and zeroed from memory after use — not shared between submissions | 5.6 |
| 13 | JWT design: access token has TTL ≤ 15 minutes; refresh token has a revocation mechanism (jti + DB lookup) | 5.6 |
| 14 | Security Architecture Specification: readable by someone who did not do the labs — a self-contained document | 5.6 |
| 15 | Any code written in the labs runs correctly — not pseudocode; pytest tests pass, not just compile | 5.3, 5.6 |
| 16 | Reference solutions have been read — at least 1 difference between the team's approach and the reference is noted | All |

## Lab Materials

| File | Description | Used In |
|------|-------------|---------|
