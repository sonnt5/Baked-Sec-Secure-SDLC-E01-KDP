# Solution 3.5 — Design Patterns: Identification, Selection, and Application

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — Pattern Identification

| Description | Pattern Name | Level | Explanation |
|------------|-------------|-------|-------------|
| **A** — `IJudgeRunner` injected via constructor | **Dependency Injection** (+ Strategy) | Design | Allows swapping implementations (Mock ↔ Docker) without modifying `SubmissionService`. High testability. |
| **B** — Each service has its own DB and deploys independently | **Microservices** (or Service-per-Database) | Deployment | Autonomous deployment, independent scaling, technology heterogeneity per service. |
| **C** — Submit → Queue → Worker → Event → Notification | **Event-Driven Architecture** (Message Queue + Event-based communication) | Tactical | Temporal decoupling: producer and consumer do not need to be online simultaneously. Enables async processing. |
| **D** — Writes → PostgreSQL, Reads → Redis cache (updated async) | **CQRS** (Command Query Responsibility Segregation) | Tactical | Separates the read model (Redis, optimized for queries) from the write model (PostgreSQL, authoritative). Reduces lock contention. |
| **E** — API Gateway: rate limit, auth validation, logging, routing | **API Gateway** (+ Cross-Cutting Concerns) | Structural | Single entry point, centralized policy enforcement. Eliminates duplicated auth/logging logic across services. |
| **F** — Interface + 2 implementations (Postgres & InMemory) | **Repository Pattern** (+ Strategy) | Design | Abstracts data access behind an interface. The service doesn't know the underlying storage technology → easy to swap, easy to test. |

---

## Task 2 — Anti-pattern Detection & Refactoring

### Case 1: ContestController

| | |
|---|---|
| **Anti-pattern name** | **God Class** / Spaghetti Code (violates SRP and SoC) |
| **Specific problem** | The controller is doing: (1) raw SQL queries, (2) business logic for compile/run, (3) score calculation, (4) email sending — all in one method. Changing the email template forces re-testing the entire submission flow. The raw SQL also introduces SQL injection risk. |
| **Consequences if unfixed** | Impossible to unit test (depends on real DB + real SMTP). Any change to email or scoring risks breaking submission. Class grows without bounds. |
| **Refactoring** | Split into: `SubmissionService.submit()` (orchestrate), `SubmissionRepository.save()` (data), `JudgeService.judge()` (compile+run), `ScoreService.updateScore()` (scoring), `NotificationService.send()` (email). The controller only validates input and delegates to services. |

### Case 2: SystemUtils God Class

| | |
|---|---|
| **Anti-pattern name** | **God Class** / Utility Bag (Low Cohesion) |
| **Specific problem** | 10 completely unrelated methods are grouped into one class just because they are "shared". `hash_password` and `generate_pdf_report` have no reason to coexist. This class changes for every possible reason, making it inherently unstable. |
| **Consequences if unfixed** | Frequent merge conflicts when multiple developers edit the file. Cannot inject only the needed dependency. Testing requires importing an enormous class. |
| **Refactoring** | Split by domain: `DateFormatter`, `EmailService`, `PasswordHasher`, `ScoreCalculator`, `UsernameValidator`, `ReportGenerator`, `FileCompressor`, `PlagiarismDetector`, `DatabaseConnectionPool`, `TestCaseParser`. Inject only what is needed. |

### Case 3: Circular Dependency

| | |
|---|---|
| **Anti-pattern name** | **Circular Dependency** (Tight Coupling) |
| **Specific problem** | `UserService` → `ContestService` → `UserService`. Neither can be instantiated first. Import order is undefined. A DI container will throw a circular dependency error at startup. |
| **Consequences if unfixed** | Application startup failure. Impossible to unit test either service in isolation. |
| **Refactoring** | Option 1: Extract a narrow `IUserReader` interface with only `findById()`. `ContestService` depends on `IUserReader`, not on the full `UserService`. Option 2: Extract a `ContestRegistrationService` as a mediator; both `UserService` and `ContestService` depend on it, eliminating the cycle. |

### Case 4: Leaky Abstraction

| | |
|---|---|
| **Anti-pattern name** | **Leaky Abstraction** + SQL Injection vulnerability |
| **Specific problem** | (1) The controller directly writes SQL — the storage layer leaks up to the presentation layer. (2) String interpolation `f"WHERE difficulty = '{filters['difficulty']}'"` is a clear SQL injection vulnerability. (3) Business logic (JOIN, GROUP BY, ORDER) lives in the controller. |
| **Consequences if unfixed** | SQL injection → data breach or data corruption. Changing the database requires modifying the controller. Business logic is untestable in isolation. |
| **Refactoring** | `ProblemController` calls `problemRepo.findWithFilters(filters: ProblemFilter)`. `ProblemFilter` is a value object. The repository uses parameterized queries: `WHERE difficulty = %s` with bound parameters. The controller knows nothing about SQL. |

---

## Task 3 — Pattern Application Map (≥5 patterns)

| Pattern | Level | Applied In CODING WAR | Problem Solved | Accepted Trade-off |
|---------|-------|----------------------|----------------|--------------------|
| **Repository** | Design | ISubmissionRepository, IProblemRepository | Decouples service from DB technology | Boilerplate interface + implementation |
| **Event-Driven / Message Queue** | Tactical | Submit → RabbitMQ → JudgeWorker | Async judging; decouples submission from judging latency | Eventual consistency, harder to debug |
| **Dependency Injection** | Design | JudgeService receives IJudgeRunner, IEventBus via constructor | High testability; swap implementations without modifying the service | Requires a DI container or manual wiring |
| **API Gateway** | Structural | Nginx + auth middleware: rate limiting, JWT validation, routing | Centralizes cross-cutting concerns; no duplication across services | Single point of failure if not made HA |
| **CQRS** | Tactical | ScoreboardService: writes → PostgreSQL, reads → Redis | Scoreboard is read-heavy and requires low latency; avoids lock contention | Eventual consistency between write and read model |
| **Strategy** | Design | IJudgeRunner: DockerJudgeRunner (prod) / MockJudgeRunner (test) / gVisorJudgeRunner (prod v2) | Swap sandbox implementations without modifying JudgeService | Multiple implementations must be maintained |

---

*Back to the lab: [labs/lab-3.5.md](../labs/lab-3.5.md)*
