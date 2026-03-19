# Chapter 6 — Security Design and Review

> **Bake Security into Modern Software Development**
> Case study system: **CODING WAR** — Online Judge System

## Chapter Objectives

Chapter 6 operationalizes secure design — moving from *"know the principles"* to *"apply them in design"*. Students build real design artifacts: a CAE chain, an Assumption Register, Measurable Security Requirements, an Interface Catalogue with PEP/PDP, Data Classification, Opaque ID design, Privacy-Aware Logging, and finally practice a complete SDR session following the 6-step process.

## Lab Roadmap

| Lab | Topic | Learning Objectives | Input | Main Artifact |
|-----|-------|---------------------|-------|--------------|
| [6.1](labs/lab-6.1.md) | Evidence-Based Design: CAE & Assumption Register | Build CAE chains; complete Assumption Register; map requirements → mechanisms → evidence | SRS Ch.2 + Threat Model Ch.4 | CAE Table + Assumption Register |
| [6.2](labs/lab-6.2.md) | Measurable Security Requirements | Translate protection goals into requirements with measurable criteria; write MRS | Business objectives + Threat List | Security Requirements Spec (MRS) |
| [6.3](labs/lab-6.3.md) | Interface Catalogue & PEP/PDP Design | Build complete 4-element Interface Catalogue; design PEP/PDP placement; define quotas & limits | Architecture Ch.3 + DFD Ch.4 | Interface Catalogue + PEP/PDP Design Doc |
| [6.4](labs/lab-6.4.md) | Secure Data Handling | Data Classification; Sensitive Data Flow Map; Opaque Identifier design; Privacy-Aware Logging schema | Asset Register Ch.4 | Data Classification Table + Token Vault Design + Log Schema |
| [6.5](labs/lab-6.5.md) | Privacy by Design & Trade-off Management | Privacy policy → design controls chain; balance security with usability; Design Simplicity strategy | MRS Lab 6.2 + Data Design 6.4 | Privacy Design Controls Checklist + Trade-off Decision Log |
| [6.6](labs/lab-6.6.md) | SDR Process & Preparation | 6-step SDR process; prepare SDR session for CODING WAR; draft review questions and checklist | All artifacts Ch.3–6.5 | SDR Preparation Package (agenda + checklist + 4 questions) |
| [6.7](labs/lab-6.7.md) | Full SDR Practice: From Design to Verdict | Practice a complete SDR: Study → Inquire → Identify → Collaborate → Write → Follow up | CODING WAR design artifacts | Complete SDR Report with Issue Log, Verdict, and Action Items |

> [!NOTE]
> **Continuous scenario:** All 7 labs continue with CODING WAR. Artifacts from Ch.2–5 are inputs: SRS (Ch.2), Architecture Diagram (Ch.3), DFD + Trust Boundaries + Asset Register (Ch.4), Mitigation Register + Pattern Application + CDR + SAS (Ch.5). Lab 6.7 is the convergence point: a real SDR session reviewing the complete design before construction begins.

## Directory Structure

```
chapter-06/
├── README.md
├── labs/
│   ├── lab-6.1.md   ← CAE Chain & Assumption Register
│   ├── lab-6.2.md   ← Measurable Security Requirements
│   ├── lab-6.3.md   ← Interface Catalogue & PEP/PDP Design
│   ├── lab-6.4.md   ← Secure Data Handling
│   ├── lab-6.5.md   ← Privacy by Design & Trade-off Management
│   ├── lab-6.6.md   ← SDR Process & Preparation
│   └── lab-6.7.md   ← Full SDR Practice
├── solutions/
│   ├── sol-6.1.md … sol-6.7.md
└── assets/
```

## Self-Assessment Checklist — Chapter 6

| # | Criterion — verify by artifact, not by feeling | Lab |
|---|-----------------------------------------------|-----|
| 1 | CAE Table: Evidence field for each entry has at least 1 runnable test ID — not "plan to test later" | 6.1 |
| 2 | Assumption Register: each unverified assumption has an owner and verification deadline | 6.1 |
| 3 | MRS: each requirement has a metric with a specific number (%) or threshold — not "should be secure" | 6.2 |
| 4 | MRS: test conditions have clear pass/fail criteria — a reviewer can run the test and determine outcome independently | 6.2 |
| 5 | Interface Catalogue: each interface has max impact documented (not just min requirements) | 6.3 |
| 6 | PEP/PDP: quotas expressed in business terms, not just req/sec — e.g., "max 1 bulk op/hour/admin" | 6.3 |
| 7 | Data Flow Map: gaps/missing controls are documented honestly — not just listing controls that exist | 6.4 |
| 8 | Log Schema: PII fields explicitly named and excluded — not just "no PII in logs" | 6.4 |
| 9 | Trade-off Decision Log: each decision acknowledges residual risk — not "no residual risk" | 6.5 |
| 10 | SDR Preparation: all 12 review questions are specific (reference actual design element) — not generic | 6.6 |
| 11 | SDR Issue Log: severity of each issue is justified in Notes — not arbitrary | 6.7 |
| 12 | SDR Verdict: if CRITICAL issues exist → verdict is APPROVED WITH CONDITIONS or REJECTED, not APPROVED | 6.7 |
| 13 | Action items: each CRITICAL/HIGH issue has an owner and specific resolution — not "team will fix this" | 6.7 |
| 14 | Traceability: any issue in the SDR Issue Log can be traced back to an MRS requirement and forward to CAE evidence | All |
| 15 | Reference solutions have been read; team notes at least 1 difference from their own approach | All |

## Lab Materials

| File | Description | Used In |
|------|-------------|---------|
