# Solution 2.5 — Requirements Traceability Matrix

> [!WARNING]
> **Reference Solution** — Complete the lab independently before consulting this.

---

## Key Insights

**Forward gap (common):** BD-03 (Operational Sovereignty — full control of test cases and results) often has no explicit FR covering *access control to test cases* — test case files are typically assumed to be protected, but if no FR says "only Admin and Problem Setters may view test case content", there is a gap.

**Backward gap (common):** A requirement like "The system shall support dark mode" has no Business Driver. It is not in the Customer Brief, not in any User Story, and does not address any BD. This is gold-plating — it should either be removed or justified by a stakeholder.

**Test Coverage Gap insight:** Requirements like "The system shall store passwords using Argon2id" can seem hard to test, but they are testable: inspect the database schema and code, write an automated test that calls `hash_password("test")` and verifies the output starts with `$argon2`. If you cannot think of any test, the requirement needs rewriting.

**100% coverage is NOT always desirable:** Some requirements may be deferred (Status = Deferred) — they are valid but out of scope for MVP. 100% coverage with placeholder test IDs is better than 70% genuine coverage, but what you want is: every requirement that is In Scope has at least one testable TC ID. Deferred requirements can be marked with TC-TBD.

---

## Sample RTM rows

| BD-ID | BRQ | Priority | REQ-ID | Type | Statement | UC | Status | TC-ID |
|-------|-----|----------|--------|------|-----------|-----|--------|-------|
| BD-01 | BRQ-01 | Must | REQ-FR-021 | FR | The system shall automatically compile and execute submitted code against each test case and record the verdict within 30 seconds. | UC Submit Solution | Covered | TC-J-001 |
| BD-03 | BRQ-03 | Must | REQ-NFR-012 | NFR | The system shall ensure test case content (input/output files) is never transmitted to the contestant browser or API response. | UC Submit Solution, UC View Problem | Covered | TC-S-008 |
| BD-04 | BRQ-04 | Should | REQ-FR-035 | FR | The system shall maintain a global ranking of all users based on total points earned across all public contests. | UC View Rankings | Covered | TC-R-003 |

*Back to the lab: [labs/lab-2.5.md](../labs/lab-2.5.md)*
