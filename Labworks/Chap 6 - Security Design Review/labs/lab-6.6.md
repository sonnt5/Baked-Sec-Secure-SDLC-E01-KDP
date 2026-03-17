# Lab 6.6 — SDR Process & Preparation

> **Chapter 6 · Security Design and Review**
> Input: All artifacts Ch.3–6.5 | Output: SDR Preparation Package (agenda + checklist + 4 questions)

> [!NOTE]
> **Artifact for this lab:** SDR Preparation Package — includes: (1) SDR Agenda, (2) Review Checklist for CODING WAR, (3) 4 Questions Framework prep sheet, (4) Pre-SDR document completeness check. This package prepares for Lab 6.7 (Full SDR Practice).

## Learning Objectives

- Understand the 6-step SDR process (Study → Inquire → Identify → Collaborate → Write → Follow up) and the role of each step.
- Distinguish the roles of Reviewer and Designer in an SDR — who owns the architecture, who reviews the risk.
- Prepare an SDR session correctly: study materials, prepare questions, identify high-risk areas.
- Apply the 4-Questions Framework (Q1: What are we building? Q2: What can go wrong? Q3: What are we going to do? Q4: Did we do a good job?) to CODING WAR.

---

## Task 1 — 6-Step SDR Process Analysis

Analyze the 6 steps of the SDR process and identify the outputs of each step in the CODING WAR context:

| # | Step | Objective | Key Activities | Output / Deliverable | For CODING WAR — What to Do |
|---|------|-----------|---------------|---------------------|----------------------------|
| **1** | **Study** | Grasp design intent without judgment — understand the system as intended | Read architecture diagrams, DFD, SRS, API specs, data flow docs; build a mental model of the system | Mental model of system; questions list; high-risk area candidates | Read: Architecture Diagram (Ch.3), DFD + Trust Boundaries (Ch.4), Interface Catalogue (Lab 6.3), MRS (Lab 6.2). Note unclear assumptions. |
| **2** | **Inquire** | Adopt "security hat" — ask questions to clarify documentation and uncover hidden risks | Ask pointed questions about sensitive data handling, trust boundaries, assumptions, "what if X fails?" scenarios | Clarified documentation; answered assumptions; updated design docs if needed | Run through Assumption Register (Lab 6.1): ask "is this verified?" for each unverified assumption. Ask: "What happens if the sandbox escapes?" "Who can see raw test cases?" |
| **3** | **Identify** | Flag high-risk areas for deep analysis based on answers to Step 2 | Review: Internet-facing interfaces, sensitive data stores, payment/scoring flows, admin privileges, third-party hooks | List of high-risk areas with brief justification; focus areas for Step 4 | CODING WAR high-risk areas: Judge Sandbox (RCE risk), Submission API (IDOR + DoS), Admin Console (Separation of Privilege), Test Cases Storage (HVA), JWT handling (crypto). |
| **4** | **Collaborate** | Two-way exchange — reviewer highlights risk, designer explains constraints, together find mitigations | Present risks with business impact; offer options with pros/cons; respect designer's decision; agree on must-fix vs nice-to-have | Agreed action items; documented disagreements; must-fix list vs recommendations | Session: reviewer presents Issue Log. Designer responds. Together agree: CRITICAL (block SDR approval) vs HIGH (should fix) vs MEDIUM/LOW (recommendations). |
| **5** | **Write** | Document findings — creates reference for the implementation team and security record | Write SDR Report: context, issues (prioritized), severity, recommendations, verdict | SDR Report (Must/Should/Could structure); Issue Log; Verdict | Fill SDR Issue Log (Lab 6.7) with: Area, Issue, Pattern/Anti-pattern, Severity, Status, Notes & Actions. Write Executive Summary. |
| **6** | **Follow up** | Verify action items implemented; check for new risks post-implementation | Review design diffs, code changes, test results; confirm critical fixes; re-assess remaining issues | SDR closure record; updated risk register; lessons learned | After Lab 6.7: assign follow-up items to sprint. Set criteria: "SDR formally closed when CRITICAL items have design resolution + MEDIUM+ have owner assigned." |

---

## Task 2 — SDR Preparation Package (Main Artifact)

### 2a. SDR Agenda

| Time | Step | Activity | Owner |
|------|------|----------|-------|
| 0:00–0:15 | **Study (recap)** | Reviewer presents: scope, key design decisions reviewed, assumptions list. Designer confirms or corrects. | Reviewer (presents), Designer (confirms) |
| 0:15–0:35 | **Inquire** | Reviewer asks pre-prepared questions from Assumption Register + Interface Catalogue gaps. Designer answers. Document any new gaps. | Reviewer (questions), Designer (answers), Note-taker |
| 0:35–0:55 | **Identify + present** | Reviewer presents identified high-risk areas with brief justification. No discussion yet — just acknowledgment. | Reviewer |
| 0:55–1:30 | **Collaborate** | Deep dive on top 3 high-risk areas: Reviewer explains risk → Designer responds → Together agree on mitigation options → Record as action item or accepted risk. | Both (Reviewer leads risk framing, Designer leads solution) |
| 1:30–1:45 | **Write (live)** | Note-taker reads back Issue Log entries. Team agrees on severity and status. Quick vote if disagreement. | Note-taker, Reviewer, Designer |
| 1:45–1:55 | **Verdict discussion** | Reviewer proposes verdict (Approved / Approved with Conditions / Rejected). Designer can object with justification. Escalation if unresolved. | Reviewer (proposes), Designer (accepts or escalates) |
| 1:55–2:00 | **Follow-up planning** | Assign owners and due dates for CRITICAL and HIGH items. Schedule follow-up review date. | All — Project Manager captures actions |

### 2b. Pre-SDR Document Completeness Check

| Required Artifact | Available? | Location / Lab | Completeness (%) | Gap / Note |
|------------------|-----------|---------------|-----------------|-----------|
| **System Architecture Diagram (with trust boundaries)** | ✓ | Lab 3.2 + Lab 5.2 (annotated) | 85% | Missing: judge node isolation diagram not explicitly shown |
| **Data Flow Diagram (DFD Level-0 + Level-1)** | ✓ | Lab 4.2 (OWASP format) | 90% | Exit points added in Lab 4.2 v2; trust boundaries annotated |
| **Threat Model Report (STRIDE analysis + Risk Register)** | ✓ | Lab 4.7 (OWASP full document) | 95% | Complete; needs update if architecture changed since Ch.4 |
| **Measurable Security Requirements** | ✓ | Lab 6.2 (MRS) | 80% | Not all areas have complete test conditions; 3 requirements still marked TBD |
| **Interface Catalogue** | ✓ | Lab 6.3 | 85% | I7 (webhooks) not filled; misuse cases partially complete |
| **Assumption Register** | ✓ | Lab 6.1 | 70% | 4 of 6 assumptions still "Unverified" — high risk for SDR |
| **Crypto Decision Record (CDR)** | ✓ | Lab 5.5 | 90% | JWT algorithm decision complete; password hashing decision complete |
| **Mitigation Register** | ✓ | Lab 5.1 | 85% | Evidence column for TH-05 and TH-08 still "TBD" |
| **Design assumptions explicitly stated** | Partial | Lab 6.1 Assumption Register | 70% | Must be 100% before SDR — chase down remaining verifications |
| **SDR review questions prepared** | In progress | Lab 6.6 Task 2c | \[Fill in %\] | \[Fill in after completing 2c\] |

### 2c. Pre-SDR Review Questions (Reviewer prepares in advance)

A good reviewer arrives at the SDR with prepared questions — not improvising. Draft 12 specific questions across 4 groups:

**Group Q1 — What are we building? (Scope & Design Intent)**

| | Question | Expected Answer / Red Flags |
|--|---------|---------------------------|
| **Q1** | Trust boundary B3 (Services → Data) — who specifically can cross this boundary? Is there any service that should not cross it but does? | \[Expected answer / red flags if answer is weak\] |
| **Q2** | Scoring and verdicts are High Value Assets — how many code paths can currently write to the verdict table? Is there any path that does not go through the judge service? | \[Expected answer / red flags\] |
| **Q3** | \[Team writes one more question about scope/design intent\] | \[Expected answer / red flags\] |

**Group Q2 — What can go wrong? (Threats & Risks)**

| | Question | Expected Answer / Red Flags |
|--|---------|---------------------------|
| **Q1** | Scenario: a contestant compromises their own judge VM (via sandbox escape). Can they: (a) read test cases? (b) submit a fake verdict? (c) affect other contestants? Explain the path for each scenario. | \[Expected answer / red flags\] |
| **Q2** | Scenario: an admin account is phished. With current admin privileges, what can the attacker do? Is there a single point of failure? | \[Expected answer / red flags\] |
| **Q3** | The Assumption Register has 4 unverified assumptions. Which one — if wrong — has the highest impact? What is the verification plan before production? | \[Expected answer / red flags\] |
| **Q4** | \[Team writes one more threat/risk question\] | \[Expected answer / red flags\] |

**Group Q3 — What are we going to do? (Mitigations)**

| | Question | Expected Answer / Red Flags |
|--|---------|---------------------------|
| **Q1** | Mitigation for TH-01 (credential stuffing) includes rate limit + account lockout. Current evidence is "test planned." When will these tests be written? Which sprint? | \[Expected answer / red flags\] |
| **Q2** | Verdict integrity: the claim is an append-only table + hash-chain. Where is the hash-chain computed and stored? Who has access to the key used to sign? | \[Expected answer / red flags\] |
| **Q3** | \[Team writes one more question about mitigation effectiveness\] | \[Expected answer / red flags\] |

**Group Q4 — Did we do a good job? (Verdict)**

| | Question | Expected Answer / Red Flags |
|--|---------|---------------------------|
| **Q1** | MRS SR-AAA01 requires a uniform error response for login. Is there a test verifying the response is identical for valid vs invalid users? Is there a timing test? | \[Expected answer / red flags\] |
| **Q2** | After reviewing the entire Issue Log: are there any CRITICAL issues with residual risk that the team has not clearly documented? | \[Expected answer / red flags\] |
| **Q3** | \[Team writes one more question about overall security posture\] | \[Expected answer / red flags\] |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| 6-Step SDR Process Analysis — CODING WAR column | **20** | Each step: specific actions for the CODING WAR context (not generic descriptions) |
| SDR Agenda — realistic timing + owners | **10** | Timing is plausible; owner assignments are clear; Collaborate step gets the most time |
| Pre-SDR Document Check | **10** | Completeness % is honest; gaps are identified actionably |
| 12 Review Questions (4 groups) | **60** | Each question: specific (references actual design), challenging (has a right/wrong answer based on the design), tests a specific security property. Generic questions like "Is the system secure?" do not count |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-6.6.md](../solutions/sol-6.6.md)*
