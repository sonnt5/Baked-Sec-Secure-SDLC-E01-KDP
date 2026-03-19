# Solution 2.4 — Requirements Quality Gate

> [!WARNING]
> **Reference Solution** — Complete the lab independently before consulting this.

---

## Task 3 — Defect Analysis (complete table)

| REQ ID | Defect Type(s) | Why it is a defect | Corrected Version |
|--------|--------------|-------------------|-----------------|
| **REQ-01** | Non-testable, Ambiguous | "Fast" has no measurable criterion. No test can pass or fail against it. | `[REQ-01] [High]` The system shall process and confirm any financial transaction within 3 seconds for 95% of requests under normal load (≤200 concurrent users). |
| **REQ-02** | Missing actor/subject, Incomplete | "Users" is undefined — which users? All users or just account holders? No authentication precondition. | `[REQ-02] [High]` The system shall allow authenticated account holders to view the current balance of any account they own, updated in real time. |
| **REQ-03** | Non-testable, Gold-plating, Ambiguous | "Attractive", "modern", and "user-friendly" are subjective and cannot be tested. Multiple concerns in one sentence. | `[REQ-03] [Medium]` The system shall achieve a System Usability Scale (SUS) score of ≥75 in usability testing conducted with at least 10 representative users. |
| **REQ-04** | Incomplete, Contradictory (implied), Missing actor/subject | "Delete" a financial transaction is dangerous and likely illegal under audit trail regulations. "Any time" ignores business rules. | `[REQ-04] [High]` The system shall allow Admin to mark a transaction as void (status: Cancelled) with a mandatory reason field. Transactions shall never be physically deleted from the database. A voided transaction shall remain visible in the audit log. |
| **REQ-05** | Non-testable, Duplicate (of REQ-03) | Repeats REQ-03 in different words. "User-friendly" is not testable. | Remove as duplicate of REQ-03, or replace with a specific accessibility standard: `[REQ-05] [Medium]` The system shall conform to WCAG 2.1 Level AA accessibility guidelines. |
| **REQ-06** | Non-testable, Ambiguous | "Many" is undefined. No performance baseline. | `[REQ-06] [High]` The system shall process a minimum of 500 concurrent financial transactions per second without transaction failure or data corruption under peak load. |
| **REQ-07** | Mixed concerns | Email notification and event logging are two separate requirements that should be tracked, implemented, and tested independently. | Split into: `[REQ-07a]` The system shall send an email notification to the account holder within 30 seconds of any new transaction. `[REQ-07b]` The system shall write an event log entry for every transaction, including timestamp, actor, transaction ID, and result. |
| **REQ-08** | Non-feasible, Non-testable | "Permanently" is technically and legally problematic — storage has finite capacity; regulations may require deletion after N years. | `[REQ-08] [High]` The system shall retain all transaction logs for a minimum of 7 years, after which logs may be archived to cold storage. Logs shall not be modifiable after creation. |
| **REQ-09** | Ambiguous, Incomplete | "May" creates optionality — will it retry or not? The behaviour is undefined. If it retries, how many times? What triggers notification instead? | `[REQ-09] [High]` If a transfer transaction fails due to a transient error (network timeout, service unavailable), the system shall automatically retry the transaction up to 3 times with a 5-second interval. If all retries fail, the system shall notify the account holder with an error code and a transaction reference number within 60 seconds. |
| **REQ-10** | Ambiguous, Non-testable | "Current software quality standards" is undefined. Which standards? Version? Jurisdiction? | `[REQ-10] [Medium]` The system shall be developed in accordance with ISO/IEC 25010:2011 (SQuaRE) quality model, specifically achieving measurable targets for the Functional Suitability, Reliability, and Security characteristics as defined in the project quality plan. |

---

## Discussion Question Answers

**Q1 (highest cost if discovered late):** REQ-04's defect (allowing hard deletion of financial transactions) would be the most expensive. If implemented as written and discovered at testing, the entire data model would need to be redesigned (soft-delete architecture), the audit trail would be broken, compliance would fail, and all code that calls the delete API would need rewriting. This exemplifies Boehm's curve: fixing a requirements defect costs 1×; fixing it after implementation costs 10–100×.

**Q2 (delete vs cancel):** "Deleting" a transaction in a financial system violates the principle of **non-repudiation and audit trail integrity** — a core security control. Once a transaction is recorded, it is a fact that cannot be erased. "Voiding" or "cancelling" creates a new record (a reversal entry) that references the original, preserving the complete history. The corrected REQ-04 captures this by requiring records to remain visible in the audit log even after voiding.

**Q3 (hardest to test):** REQ-03 ("attractive, modern, user-friendly") is the hardest to test because it is entirely subjective. Rewritten as SUS ≥ 75 (REQ-03 corrected version): Test Case 1: "Conduct SUS survey with 10 users after 20 minutes of system use — average score must be ≥75." Test Case 2: "Repeat SUS survey after UI redesign — score must not drop below 75."

*Back to the lab: [labs/lab-2.4.md](../labs/lab-2.4.md)*
