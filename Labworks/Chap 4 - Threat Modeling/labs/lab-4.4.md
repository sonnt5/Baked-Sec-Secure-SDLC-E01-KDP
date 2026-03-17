# Lab 4.4 — OWASP Step 2: STRIDE + Threat Trees + DREAD Qualitative Scoring

> **Chapter 4 · Threat Modeling and Risk-Driven Prioritization**
> Input: Assets + DFD from Labs 4.2–4.3 | Output: Threat List, Threat Tree diagram, DREAD table

> [!NOTE]
> **OWASP Note:** OWASP adds two key techniques to Step 2: (1) Threat Trees — *"one tree per threat goal; useful to perform threat analysis"*; (2) DREAD-inspired Qualitative Risk Model — instead of numeric DREAD scores (which were deprecated for being too subjective), structured qualitative questions are used to determine Likelihood and Impact in a more principled way.

## Learning Objectives

- Apply STRIDE per element to the CODING WAR DFD.
- Build a Threat Tree for a critical threat — analyze attack paths and root causes.
- Use the OWASP Qualitative Risk Model to score threats by Likelihood and Impact.
- Create a Threat List fully linked to assets, entry points, and trust boundaries.

---

## Task 1 — STRIDE / CIA-AAA Mapping

| STRIDE | Full Name | CIA/AAA Violated | Primary DFD Element | Specific Example in CODING WAR |
|--------|-----------|-----------------|--------------------|---------------------------------|
| **S** | **Spoofing** | Authentication (AAA) | External Entity | Credential stuffing on POST /auth/login using stolen passwords from breach databases |
| **T** | **Tampering** | Integrity (CIA) | Data Flow, Data Store | Modifying a submission's JSON payload before it reaches JudgeService — changing the code being judged |
| **R** | **Repudiation** | Auditing (AAA) | Process, Data Store | Admin deletes a problem with no audit trail — accountability cannot be traced |
| **I** | **Information Disclosure** | Confidentiality (CIA) | Data Flow, Data Store | \[Fill in a specific CODING WAR example\] |
| **D** | **Denial of Service** | Availability (CIA) | Process, Data Flow | \[Fill in a specific CODING WAR example\] |
| **E** | **Elevation of Privilege** | Authorization (AAA) | Process, Trust Boundary | \[Fill in a specific CODING WAR example\] |

---

## Task 2 — STRIDE per Element Analysis

Apply STRIDE to each of the 5 DFD element types. For each CODING WAR element, describe a specific threat scenario.

### 👤 External Entities (Primary risk: S)

> Attackers typically start here — identity verification is the priority.

| Element | STRIDE | Threat Scenario | Asset at Risk | Current Control |
|---------|--------|----------------|---------------|----------------|
| **Contestant** | **S** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Admin** | **S** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Anonymous Guest** | **S** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |

### ⚙️ Processes / Services (Primary risks: T, R, I, D, E)

> Application logic — where code vulnerabilities typically appear.

| Element | STRIDE | Threat Scenario | Asset at Risk | Current Control |
|---------|--------|----------------|---------------|----------------|
| **Authentication Service** | **T** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Authentication Service** | **R** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Authentication Service** | **I** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Submission & Judge Service** | **T** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Submission & Judge Service** | **R** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Submission & Judge Service** | **I** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Contest Service** | **T** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Contest Service** | **R** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Contest Service** | **I** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |

### ➡️ Data Flows (Primary risks: T, I, D)

> Data in transit — interception and modification threats.

| Element | STRIDE | Threat Scenario | Asset at Risk | Current Control |
|---------|--------|----------------|---------------|----------------|
| **HTTP request: client → API** | **T** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **HTTP request: client → API** | **I** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **HTTP request: client → API** | **D** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Message: submission → Judge Queue** | **T** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Message: submission → Judge Queue** | **I** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Message: submission → Judge Queue** | **D** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **JWT token in header** | **T** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **JWT token in header** | **I** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **JWT token in header** | **D** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |

### 🗄️ Data Stores (Primary risks: T, R, I, D)

> Data at rest — high-value assets.

| Element | STRIDE | Threat Scenario | Asset at Risk | Current Control |
|---------|--------|----------------|---------------|----------------|
| **User DB** | **T** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **User DB** | **R** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **User DB** | **I** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Submission DB** | **T** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Submission DB** | **R** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Submission DB** | **I** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Test Cases Storage** | **T** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Test Cases Storage** | **R** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **Test Cases Storage** | **I** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |

### 🔲 Trust Boundaries (All STRIDE categories apply)

> Control concentration points — all STRIDE threats are possible.

| Element | STRIDE | Threat Scenario | Asset at Risk | Current Control |
|---------|--------|----------------|---------------|----------------|
| **B1: Internet → Web** | **STRIDE** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **B2: Web → Services** | **STRIDE** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |
| **B3: Services → Data** | **STRIDE** | \[Describe specific attack scenario\] | \[Asset from Register\] | \[Current control / MISSING\] |

---

## Task 3 — Threat Tree (OWASP)

> [!NOTE]
> **OWASP Note:** *"There is one tree for each threat goal... Threat trees are useful to perform threat analysis by exploring attack paths, root causes, and necessary mitigation controls."* A Threat Tree shows: Goal (root) → Sub-goals (branches) → Leaf conditions (attackable leaves). Each node is an AND or OR condition.

Build a Threat Tree for the attack goal: **"ACCOUNT TAKEOVER"**.

> **Threat Tree Structure:** Root Goal → Branches (OR: any one path is sufficient) → Leaves (specific conditions the attacker must achieve). AND-node: ALL child conditions required. OR-node: only ONE child condition required.

> 📎 Draw the Threat Tree here (Root: Account Takeover)
>
> Suggested structure: Root: Account Takeover → Branch 1 (OR): Steal credentials; Branch 2 (OR): Bypass authentication; Branch 3 (OR): Session hijacking. Each branch has 2–3 leaf attacks. Use draw.io or hand-draw + photograph.

**Text representation of the Threat Tree** (for inclusion in the document):

| Node ID | Node Description | AND/OR | Parent Node | Mitigation / Countermeasure |
|---------|-----------------|--------|-------------|----------------------------|
| **AT-0** | Account Takeover (ROOT GOAL) | **OR** | — | Defense-in-depth: MFA + rate limiting + monitoring |
| **AT-1** | Steal Credentials | **OR** | AT-0 | MFA, HTTPS, anti-phishing training |
| **AT-1.1** | Credential stuffing via /login | **Leaf** | AT-1 | Rate limit, account lockout, CAPTCHA |
| **AT-1.2** | Phishing for password | **Leaf** | AT-1 | MFA, anti-phishing awareness |
| **AT-1.3** | Password breach database attack | **Leaf** | AT-1 | Breach monitoring, password rotation notification |
| **AT-2** | Bypass Authentication | **OR** | AT-0 | \[Fill in mitigations\] |
| **AT-2.1** | \[Fill in attack leaf\] | **Leaf** | AT-2 | \[Fill in\] |
| **AT-2.2** | \[Fill in attack leaf\] | **Leaf** | AT-2 | \[Fill in\] |
| **AT-3** | Session Hijacking | **OR** | AT-0 | \[Fill in mitigations\] |
| **AT-3.1** | \[Fill in attack leaf\] | **Leaf** | AT-3 | \[Fill in\] |
| **AT-3.2** | \[Fill in attack leaf\] | **Leaf** | AT-3 | \[Fill in\] |

---

## Task 4 — DREAD Qualitative Risk Scoring (OWASP)

> [!NOTE]
> **OWASP Note:** OWASP recommends a Qualitative Risk Model instead of numeric DREAD scores (which were deprecated for being too subjective). The model uses structured questions: *Ease of exploitation* (exploitable remotely? auth required? automatable?) and *Damage potential* (system takeover? admin access? crash? PII exposure?). Result: HIGH / MEDIUM / LOW instead of numbers.

| Threat ID | Threat Summary | Remote exploit? | Auth needed? | Automatable? | Likelihood | System takeover? | Admin access? | Crash system? | PII exposed? | Impact | Risk = L×I (H/M/L) |
|-----------|---------------|----------------|-------------|--------------|-----------|-----------------|--------------|--------------|-------------|--------|---------------------|
| **TH-01** | Credential stuffing /login | Y | N | Y | HIGH | N | N | N | Y | HIGH | CRITICAL |
| **TH-02** | IDOR /submissions/{id} | Y | Y (basic) | Y | HIGH | N | N | N | Y (code) | MEDIUM | HIGH |
| **TH-03** | DoS via infinite loop submit | Y | Y (basic) | Y | HIGH | N | N | Y | N | HIGH | CRITICAL |
| **TH-04** | Verbose error messages | Y | N | Y | HIGH | N | N | N | Partial | LOW | MEDIUM |
| **TH-05** | Missing admin audit log | Y (internal) | Y (admin) | N | LOW | N | Y | N | Y | HIGH | MEDIUM |
| **TH-06** | \[New threat\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-07** | \[New threat\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-08** | \[New threat\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-09** | \[New threat\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| **TH-10** | \[New threat\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| STRIDE per Element (5 element types) | **30** | Specific threats, realistic attack scenarios, assets linked |
| Threat Tree (Account Takeover) | **30** | ≥3 branches, ≥6 leaves, correct AND/OR notation, countermeasure for each leaf |
| DREAD Qualitative Scoring (≥10 threats) | **40** | Questions answered consistently, Risk Level is logical, ≥3 CRITICAL identified with justification |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-4.4.md](../solutions/sol-4.4.md)*
