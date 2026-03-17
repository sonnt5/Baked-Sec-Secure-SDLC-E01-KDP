# Chapter 2 — Requirement Modeling

> **Bake Security into Modern Software Development**
> Lab Works — Requirements Engineering in Practice
> Case study system: **CODING WAR** — Online Judge System

## Overview

Chapter 2 labs are designed as a **cumulative chain**: the output of each lab is the input for the next. By the end, you will have built a complete set of requirements artifacts for the CODING WAR system — from raw stakeholder analysis all the way to a security-augmented requirements traceability matrix.

> [!NOTE]
> **Design philosophy:** Every deliverable in this chapter is built from scratch by you. There are no fill-in-the-blank templates. You design the structure, decide the depth, and own the quality. This is how real Requirements Engineering works.

## Lab Roadmap

| Lab | Topic | Objectives | Input | Deliverable |
|-----|-------|-----------|-------|-------------|
| [2.1](labs/lab-2.1.md) | Stakeholder Analysis & Requirements Elicitation | Identify stakeholders; elicit requirements from 2 sources; translate User Stories; Gap Analysis | Customer Brief + User Stories | Requirements Catalog (.xlsx) |
| [2.2](labs/lab-2.2.md) | Requirements Modeling (3 Views) | Use Case Diagram + 4 UC Descriptions; Domain Class Diagram; 3 State Machine Diagrams | Requirements Catalog Lab 2.1 | Requirements Models (.docx) |
| [2.3](labs/lab-2.3.md) | SRS Document | Synthesize Lab 2.1 + 2.2 into a complete IEEE 830 SRS | All Lab 2.1 + 2.2 outputs | SRS Document (.docx) |
| [2.4](labs/lab-2.4.md) | Quality Gate Review | Build Quality Gate Checklist; peer-review an SRS; detect and fix bad requirements | SRS (peer group or sample) | Quality Review Report (.docx) |
| [2.5](labs/lab-2.5.md) | Requirements Traceability Matrix (RTM) | Build end-to-end RTM: Business Drivers → Requirements → Use Cases → Test Cases | SRS Lab 2.3 + Business Drivers | RTM (.xlsx) + Gap Analysis |
| [2.6](labs/lab-2.6.md) | Security Requirements Elicitation | Analyze attack surface; elicit 15+ Security NFRs; embed into SRS; update RTM | SRS + RTM + Threat landscape | Security-Augmented SRS + Updated RTM |

## Continuous Scenario: CODING WAR

All six labs use the same system throughout — the **CODING WAR Online Judge**. The full Customer Brief is embedded in Lab 2.1. Key facts:

- **Customer:** A university IT department replacing a manual programming contest workflow
- **Business Drivers:** BD-01 Process Automation, BD-02 Skill Enhancement, BD-03 Operational Sovereignty, BD-04 Talent Identification
- **Users:** Anonymous visitors, Contestants, Problem Setters / Contest Organizers, Admins
- **Core features:** User management, Problem management, Auto-judging (sandbox), Contest management, Scoreboard

## Lab Materials (provided separately)

| File | Content | Used In |
|------|---------|---------|
| `Coding_War_User_Stories.xlsx` | 16 User Stories across 4 Epics with Acceptance Criteria | Lab 2.1 (second elicitation source) |
| `CODING_WAR_SRS.docx` (sample) | Complete SRS of a reference e-commerce system for format reference | Labs 2.3, 2.4 |
| `Coding_War_Traceability_Matrix.xlsx` | Sample RTM for CODING WAR | Lab 2.5 (for comparison) |

## Final Artifacts Checklist

When Chapter 2 is complete, you should have produced:

| # | Artifact | Lab | Used in |
|---|----------|-----|---------|
| 1 | Stakeholder Register + Power/Interest Grid | 2.1 | Chapter 3 (Design) |
| 2 | Master Requirements Catalog (.xlsx) | 2.1 | All subsequent chapters |
| 3 | UC Diagram + 4 UC Descriptions + Class Diagram + 3 State Machines | 2.2 | Chapters 3, 4, 5 |
| 4 | SRS Document (IEEE 830) with Security NFRs | 2.3, 2.6 | All subsequent chapters |
| 5 | Requirements Quality Gate Checklist | 2.4 | Chapters 3–8 |
| 6 | RTM with Security coverage | 2.5, 2.6 | Chapters 4 (Threat Modeling), 8 (Testing) |

## Self-Assessment Checklist

| # | Criterion | Lab |
|---|-----------|-----|
| 1 | All requirements follow format: `[ID] The system shall/should...` (clear subject) | 2.1, 2.3 |
| 2 | Each requirement addresses ONE thing only (single concern) | 2.1, 2.3 |
| 3 | Requirements with High/Critical priority have measurable Acceptance Criteria | 2.3, 2.6 |
| 4 | No vague language: "fast", "user-friendly", "many" — replaced with specific numbers | 2.1, 2.3 |
| 5 | Every requirement traces back to at least one Business Driver (no orphans) | 2.5 |
| 6 | UML diagrams (UC, Class, State Machine) use correct notation with legends | 2.2 |
| 7 | SRS has all 7 sections + appendices | 2.3 |
| 8 | RTM covers ≥18 requirements end-to-end | 2.5 |
| 9 | Gap Analysis identifies ≥1 gap per type | 2.5 |
| 10 | ≥15 Security NFRs embedded in SRS (not a separate "security document") | 2.6 |
| 11 | RTM updated with Security NFRs and TC IDs | 2.6 |
| 12 | All deliverables are files built by the team (no copied templates) | All |
