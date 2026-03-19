# Lab 2.1 — Stakeholder Analysis & Requirements Elicitation

> **Chapter 2 · Requirement Modeling**
> Input: Customer Brief + User Stories | Output: Requirements Catalog (.xlsx)

## Learning Objectives

- Identify and classify stakeholders using the BABOK framework.
- Elicit requirements from two distinct sources: a Customer Brief (unstructured prose) and Agile User Stories (structured).
- Classify requirements by Nature Type (FR/NFR/DR/IR/TR) and Abstraction Level.
- Translate User Stories into Formal Requirements.
- Perform Gap Analysis between two sources and construct high-quality Clarification Questions.

---

## Context: The CODING WAR System

You have just been assigned to the CODING WAR project. The following Customer Brief was written by the client — the Head of the IT Department at a university. It is written in natural language, has no technical structure, and contains both explicit and implicit requirements. Your job is to extract, classify, and formalise everything you find.

---

### Customer Brief

*To: Development Team*

*From: Head of IT Department*


*Subject: CODING WAR — Online Programming Judge System*

---

We have been running programming contests at the Faculty for several years now, but honestly the process is a mess. Instructors type up problems in Word, students email their solutions in, and we grade everything by hand. Last semester's regional qualifier had 200 students and it took three lecturers a full weekend just to check submissions. We missed two wrong answers entirely. It is not sustainable.

What we want to build — and we are calling it CODING WAR — is something like Codeforces or the ACM judge systems you might have used in competitions, but adapted for our teaching needs. The most important thing for us is getting rid of manual grading completely. When a student submits code, the system should compile it, run it against our test cases, and tell the student whether they passed or failed within about 30 seconds. That alone would transform how we run assessments.

Beyond grading, we want students to be able to practice whenever they want. We have faculty who are quite good at writing algorithmic problems — they should be able to author problems with proper descriptions, example inputs and outputs, and time and memory limits. Problems need to stay hidden until they are ready to publish; we do not want half-finished problems showing up to students. Only department admins should be able to flip a problem from draft to live. Right now we are thinking about three programming languages to start: Python 3, C++, and Java. That covers most of what our students use.

The biggest worry we have with automated judging is security. When the system runs a student's code, that code is completely untrusted — a student could write anything. We need the execution to be completely isolated from the server and from other students' submissions. I do not know the technical details of how this is done, but I have seen what happens when sandboxing is done badly and it is not pretty.

For account management, we need the usual: students sign up with a username and email, verify the email, and log in. There should be a password reset flow. We also need different levels of access — most people are just students, but some faculty need the ability to create problems and organise contests, and then there are administrators who can do everything. The login system needs to be sensible about security too; if someone keeps entering the wrong password they should be locked out for a while.

The contest functionality is actually quite important to us. We run both open practice contests and closed examination-style competitions. A contest organiser should be able to set the start and end times, choose which problems are included, and decide whether the contest is open to everyone or invite-only. During a contest, students should not be able to see each other's solutions or read any editorial. We also want the scoreboard to freeze at some point near the end — like the last hour — so that the final standings are a surprise until the contest ends. Before any contest goes live, there should be some kind of dry run to make sure the problems and test cases are working properly with the model solutions.

We want to be able to see who our top performers are across the department. A ranking system showing cumulative performance would be really valuable for identifying students to recommend for external competitions.

On the technical side, I will be honest — we are not experts. But we know we need the system to hold up during a contest when everyone logs in at once; we had maybe 300 students in a recent contest and the third-party platform we used slowed down badly. We need student passwords stored properly — nobody, not even the admins, should be able to read them. The site should work on phones and laptops. Data needs to be backed up regularly. And everything transmitted between the browser and server should be encrypted.

We are realistic about what can be done first. The priority is getting the core working: registration and login, problems, automated judging, contests, and the scoreboard. Things like discussion forums, two-factor authentication, integration with our LMS, and plagiarism detection can wait. We have a small team and roughly four to six months. We are planning to use cloud hosting to keep infrastructure costs manageable.

---

### User Stories (second source)

You also receive `Coding_War_User_Stories.xlsx` from the Product Owner. This file contains **16 User Stories** across 4 Epics with Acceptance Criteria:

- **Epic 1: Authentication and Profile Management** — US01–US04
- **Epic 2: Problem Management** — US05
- **Epic 3: Problem Solving** — US06–US11
- **Epic 4: Contest** — US12–US16

Open this file alongside the Customer Brief. The two sources are **independent** and will not be perfectly aligned.

---

## Task 1 — Stakeholder Analysis

Identify **all stakeholders** of the CODING WAR system. For each stakeholder:

1. Define their **Role** in the system and in the project. Use BABOK classifications: Customer, End User, Domain SME, Implementation SME, Sponsor, Regulator, Operational Support, Tester, Project Manager.
2. Assess their **Influence** (power) and **Interest** level to position them on a **Power/Interest Grid**.
3. List their **Key Expectations** from the system.
4. Identify the most appropriate **Elicitation Method** for them: Interview, Workshop, Observation, Survey, Document Analysis.

**Deliverable:** Create a "Stakeholder Register" sheet in your Excel file. Also describe (or draw) the Power/Interest Grid and specify the engagement strategy for each quadrant.

> [!NOTE]
> Look beyond obvious users. Consider: Who authors problems? Who approves the system going live? Who maintains it after launch? Are there any non-human actors (Email Service, Judge Engine)?

---

## Task 2 — Requirements Elicitation from the Customer Brief

Read the Customer Brief above carefully. Extract **all** requirements you can identify — both **explicit** (clearly stated) and **implicit** (logically required but not stated directly).

For each requirement:

1. Assign a unique **ID** using the convention: `FR-xx`, `NFR-xx`, `DR-xx`, `IR-xx`, `TR-xx`
2. Write the requirement as: *"The system shall / should..."* (use **shall** for mandatory, **should** for desirable)
3. Classify the **Nature Type**:
   - **FR** — Functional Requirement (what the system does)
   - **NFR** — Non-functional / Quality Attribute (how well it does it)
   - **DR** — Data Requirement (what data the system stores)
   - **IR** — Interface Requirement (how it connects to other systems/users)
   - **TR** — Transition Requirement (what changes during migration/deployment)
4. Identify the **Abstraction Level**: Business, Stakeholder, System, or Software
5. Record the **Source**: which section of the Customer Brief this came from

Create a "Requirements from Brief" sheet in your Excel file.

> [!TIP]
> A thorough analysis of this Brief should yield **at least 20–25 requirements**, including implicit ones. If you find fewer than 15, re-read more carefully. For example: the sandbox security note implies requirements about resource limits, network isolation, and file system restrictions — none of which are stated explicitly.

---

## Task 3 — Translate User Stories into Formal Requirements

Open `Coding_War_User_Stories.xlsx`. For **all 16 User Stories**, perform:

1. **Extract FRs:** Each User Story typically implies 1–3 functional requirements. Write each as *"The system shall..."*
2. **Identify implicit NFRs:** Acceptance Criteria often contain quality constraints. Identify and formalise them as NFRs.
3. **Identify DRs:** If the User Story involves data storage, describe the entity and its required attributes.

Create a "Requirements from User Stories" sheet. Each row should contain: `US ID → Derived requirement(s) → Type (FR/NFR/DR) → Notes`.

---

## Task 4 — Gap Analysis & Clarification Questions

Compare the two sources:

**4a. Forward Gap** — In the Customer Brief but NOT in the User Stories (potentially lost when working Agile):

For each gap: describe the missing feature and propose a new User Story to add to the appropriate Epic.

**4b. Backward Gap** — In the User Stories but NOT clearly in the Customer Brief (additional detail from the Agile team):

For each item: explain what new information the User Stories add and how it affects the Brief's requirements.

**4c. Conflict Analysis** — Points where the two sources are contradictory or inconsistent. Explain the conflict and propose a resolution.

**4d. Clarification Questions** — Write at least **8 questions** to ask the client. Each question must:
- Arise from a specific gap or conflict (reference the FR/US ID)
- Be phrased so the answer will lead to a **measurable acceptance criterion**
- Not be answerable from information already provided

> [!WARNING]
> Weak question: *"How should the system handle login errors?"*
> Strong question: *"The Customer Brief mentions temporarily locking an account after multiple failed logins, but does not specify the threshold or lock duration. US02's Acceptance Criteria say 'lock for 15 minutes after 5 failed attempts' — is this the correct behaviour? Should the lock timer reset after each failed attempt, or only after a successful login?"*

Create "Gap Analysis" and "Clarification Questions" sheets.

---

## Task 5 — Master Requirements Catalog

Consolidate all requirements from Tasks 2 and 3 into a single "Master Requirements Catalog" sheet. Remove duplicates, resolve conflicts, and assign consistent IDs. Each requirement must have:

| Field | Description |
|-------|-------------|
| **Unique ID** | e.g., `REQ-FR-001`, `REQ-NFR-001` |
| **Statement** | Full *"The system shall..."* sentence |
| **Nature Type** | FR / NFR / DR / IR / TR |
| **Abstraction Level** | Business / Stakeholder / System / Software |
| **Priority** | MoSCoW (Must/Should/Could/Won't) or H/M/L |
| **Source(s)** | Customer Brief / US ID / Both |
| **Status** | Draft / Approved / Deferred |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Stakeholder Analysis | **15** | ≥6 stakeholders, correct BABOK classification, reasonable Power/Interest Grid, clear engagement strategy |
| Requirements from Brief (≥20) | **20** | Correct Nature Type and Abstraction Level; proper shall/should format; implicit requirements not missed |
| Translate 16 User Stories | **25** | Each US: FRs correctly extracted; implicit NFRs identified from Acceptance Criteria; DRs with full attributes |
| Gap Analysis (2 directions + conflicts) | **15** | ≥3 gaps each direction; analysis is specific not generic; proposed new User Stories are plausible |
| Clarification Questions (≥8) | **10** | Each question ties to a specific gap/conflict; references FR/US ID; leads to measurable acceptance criteria |
| Master Catalog (overall quality) | **15** | Consistent, no duplicates, no contradictions, professional format, all columns filled |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-2.1.md](../solutions/sol-2.1.md)*