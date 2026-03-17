# Solution 3.6 — Design Quality Review & Design Review Report

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this. Rubric scores may vary depending on your team's design.

---

## Task 1 — Design Quality Rubric (based on the Reference Solution from Labs 3.1–3.5)

### 1. Maintainability — Reference score: 12/16

| Criterion | Score | Evidence |
|-----------|-------|---------|
| Clear module boundaries; each component follows SRP | 4 | 5 clearly separated modules (Auth, Problem, Contest, Judge, Scoreboard). JudgeService delegates verdict logic to a dedicated `VerdictDeterminer`. |
| Design allows independent unit testing of components | 3 | Interfaces (ISubmissionRepo, IJudgeRunner) enable mocking. However, JudgeWorker's RabbitMQ integration lacks a clear abstraction for isolated testing. |
| Architecture supports horizontal scaling of critical components | 3 | JudgeWorker can scale horizontally. External session storage (Redis) is proposed but not fully reflected in the design artifacts. |
| Violations of Law of Demeter / inappropriate intimacy | 2 | API contracts are consistent with the ER model. Some API specs (Lab 3.3) lack a fully defined error response schema. |
| **Total** | **12/16** | Good design; a few areas are incomplete |

### 2. Testability — Reference score: 11/16

| Criterion | Score | Evidence |
|-----------|-------|---------|
| No God Class or Circular Dependency anti-patterns | 4 | Lab 3.5 detected and refactored all 4 anti-patterns. Current design is clean. |
| Interfaces are stable and easy to mock/stub | 3 | ISubmissionRepository, IJudgeRunner, IEventBus are all clean interfaces. An interface for EmailService is missing. |
| Data layer is separated enough for independent scaling | 2 | Repository pattern implemented. However, some complex queries (scoreboard) lack a clear read-model abstraction. |
| Coupling level between modules | 2 | Module-level coupling is low thanks to event-driven communication. However, a shared PostgreSQL database creates implicit coupling between modules. |
| **Total** | **11/16** | Solid; interface coverage needs improvement |

### 3. Scalability — Reference score: 10/16

| Criterion | Score | Evidence |
|-----------|-------|---------|
| ADRs document rationale and trade-offs | 4 | ADR-001 (async judging) has complete context and clear trade-offs. Missing ADRs for database choice and caching strategy. |
| Test data is easy to set up (isolated DB, fixtures) | 2 | No test fixture strategy has been designed. InMemoryRepository helps unit tests, but integration test setup is unclear. |
| SPOFs have been addressed | 2 | SPOF analysis (Lab 3.4) is thorough, but HA solutions are only proposals — not reflected in the beta Deployment Diagram. |
| Cohesion level within each module | 2 | JudgeService has high cohesion. ScoreboardModule still handles reporting — these should be separated. |
| **Total** | **10/16** | Needs additional ADRs and an HA-aware design |

### 4. Modularity & Separation of Concerns — Reference score: 9/12

| Criterion | Score | Evidence |
|-----------|-------|---------|
| Each module has a clear bounded context | 4 | 5 modules do not overlap. JudgeWorker is separated from the API server. |
| Cross-cutting concerns are centralized | 3 | Auth middleware is centralized at the API Gateway. Logging strategy is not clearly represented in the design. |
| No business logic in the presentation or data layer | 2 | API specs define pre/postconditions clearly. However, a few API endpoints still show business rule leakage into the controller layer (from Lab 3.3). |
| **Total** | **9/12** | Good; logging and error-handling strategy need attention |

---

## Task 2 — Design Review Checklist

| # | Check | ✓/✗ | Notes |
|---|-------|-----|-------|
| 1 | All FRs mapped to ≥1 component | ✓ | Traceability Matrix (Lab 3.2) covers FR-01 through FR-17 |
| 2 | All entities have a clear "owner" component | ✓ | User→Auth, Problem→ProblemSvc, Submission→JudgeSvc, Contest→ContestSvc |
| 3 | API contracts consistent with ER Model | ✓ | Field names consistent; UUID types match. A few nullable fields are not clearly defined. |
| 4 | Deployment Diagram covers all components | ✓ | App, JudgeWorker, PostgreSQL, Redis, RabbitMQ, MinIO, and Nginx are all present |
| 5 | No circular dependencies | ✓ | Lab 3.5 detected and resolved the UserService ↔ ContestService circular dependency |
| 6 | Each component has Single Responsibility | ✓ | After Lab 3.5 refactoring, no God Classes remain |
| 7 | Interfaces sufficient without knowing internals | ✓ | ISubmissionRepository, IJudgeRunner are well-defined |
| 8 | ADRs document key decisions with trade-offs | ✗ | Only ADR-001 exists. Missing ADRs for DB selection, caching strategy, and sandbox choice |
| 9 | No security anti-patterns | ✗ | Lab 3.5 Case 4 identified an SQL injection vulnerability in the draft — refactored. All API endpoints should be verified for auth checks. |
| 10 | Design can scale to meet concurrent user NFR | ✓ | JudgeWorker scales horizontally. DB replication is proposed in Lab 3.4. |
| 11 | Pattern Application Map consistent with design | ✓ | All 6 patterns from Lab 3.5 correspond to actual design artifacts |
| 12 | Pseudocode covers happy path + all error paths | ✓ | Lab 3.3 pseudocode covers CE, TLE, MLE, RE, WA, and AC |

---

## Task 3 — Design Review Report (SDR)

| Section | Content |
|---------|---------|
| **System Name / Version** | CODING WAR v0.1-beta — Design Review Report |
| **Review Date** | \[Fill in date\] |
| **Reviewer(s)** | \[Reviewing team\] |
| **Executive Summary** | The CODING WAR design demonstrates a solid understanding of separation of concerns and dependency management. The selected patterns (Repository, Event-Driven, Dependency Injection) are well-suited to the requirements. The main weaknesses are a lack of ADRs for key architectural decisions (database, cache, sandbox) and an incomplete HA design in the Deployment Diagram. Verdict: APPROVED WITH CONDITIONS. |
| **Quality Rubric Totals** | Maintainability: 12/16 · Testability: 11/16 · Scalability: 10/16 · Modularity: 9/12 · **Total: 42/60** |
| **Critical Issues** | **CI-01:** Missing ADR for the database choice (PostgreSQL) and caching strategy. No justification for why MongoDB or MySQL was not selected. Affected: Architecture artifacts. **CI-02:** The beta Deployment Diagram does not show HA for PostgreSQL or RabbitMQ — deploying as-is would leave known SPOFs unresolved in production. |
| **Major Issues** | **MA-01:** ScoreboardModule still handles reporting — extract a ReportingService before implementation begins. **MA-02:** EmailService has no interface abstraction — makes mocking in tests difficult. **MA-03:** Integration test strategy not designed (fixtures, test DB isolation). |
| **Minor Issues** | **MI-01:** Some API error response schemas do not define a consistent error message format. **MI-02:** Logging strategy is absent from the design (centralized logging, correlation IDs). |
| **Design Strengths** | (1) Event-driven architecture for judging — scalable and resilient. (2) Anti-pattern detection and refactoring in Lab 3.5 — team demonstrated self-review capability. (3) Complete Traceability Matrix — every FR is traced to a component. (4) `VerdictDeterminer` is a separate pure function class — easy to unit test in isolation. |
| **Verdict** | ☑ **APPROVED WITH CONDITIONS** |
| **Conditions for Approval** | (1) Add ADR-002 (Database Selection: PostgreSQL justification vs. alternatives) and ADR-003 (Caching Strategy: Redis patterns and rationale). (2) Update the Deployment Diagram to show: PostgreSQL Primary + Standby and RabbitMQ with ≥2 nodes. |

---

## Task 4 — Action Items

| ID | Required Change | Severity | Affected Artifact | Responsible | Deadline |
|----|----------------|----------|------------------|-------------|---------|
| AI-01 | Write ADR-002 (Database: PostgreSQL justification) and ADR-003 (Caching: Redis strategy) | Critical | ADRs folder | Tech Lead | Before Sprint 1 |
| AI-02 | Update Deployment Diagram to add PostgreSQL replica and RabbitMQ cluster | Critical | Deployment Diagram (Lab 3.4) | DevOps member | Before Sprint 1 |
| AI-03 | Extract ReportingService from ScoreboardModule; update Architecture Diagram | Major | Architecture Diagram (Lab 3.2) | Backend member | Sprint 1 |
| AI-04 | Define IEmailService interface; update Class Diagram | Major | Class Diagram (Lab 3.3) | Backend member | Sprint 1 |
| AI-05 | Standardize API error response schema across all 5 endpoints in the API Spec | Minor | API Specs (Lab 3.3) | API owner | Sprint 2 |

---

*Back to the lab: [labs/lab-3.6.md](../labs/lab-3.6.md)*
