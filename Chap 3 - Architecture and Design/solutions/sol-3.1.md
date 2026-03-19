# Solution 3.1 — Core Concept Analysis & Design Trade-offs

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this. Many questions have multiple valid answers depending on your reasoning.

---

## Task 1 — Distinguishing Requirements from Design Decisions

| # | Statement | Type | Explanation |
|---|-----------|------|-------------|
| 1 | The system must allow contestants to submit solutions in C++, Java, or Python. | **R** | Defines *what* — a required capability, with no specification of how it is implemented. This is a functional requirement. |
| 2 | The judging service will use Docker containers to isolate the execution environment. | **D** | Defines *how* — selects a specific technology (Docker) to fulfill the isolation requirement. |
| 3 | Judging results must be returned within 30 seconds of a successful submission. | **R** | Non-functional requirement (performance). Specifies the constraint, not the mechanism to achieve it. |
| 4 | SubmissionService and JudgeService will communicate via a message queue (RabbitMQ). | **D** | A specific architectural decision — chooses a communication pattern (async queue) and a technology (RabbitMQ). |
| 5 | Admins must be able to create and manage problems in the system. | **R** | Functional requirement — defines an actor and a required capability. |
| 6 | User data will be stored in PostgreSQL; session tokens will be stored in Redis. | **D** | A design decision about the persistence layer — specifically selects two storage technologies. |
| 7 | The system must support at least 500 concurrent users. | **R** | Non-functional requirement (scalability/performance). This is a constraint, not a solution. |
| 8 | Authentication will be based on JWT with a 1-hour access token and a 7-day refresh token. | **D** | A design decision on the authentication mechanism — selects JWT and defines token lifetimes. |
| 9 | Contestants may only view the results of their own submissions. | **R** | Functional requirement defining an authorization/access control business rule. |
| 10 | Test cases will be stored on S3-compatible object storage rather than in the database. | **D** | An architectural data decision — selects a storage strategy for a specific type of data. |

**Analysis note:** The R/D boundary is not always absolute. Statement 8 could be argued as R if "use JWT" is a stakeholder security requirement. What matters is a consistent and well-reasoned argument.

---

## Task 2 — Identifying Violations of the 5 Core Concepts

### Scenario A — ContestController doing everything

| | |
|---|---|
| **Concept violated** | **Separation of Concerns** (and Single Responsibility Principle) |
| **Explanation** | A single class handles 5 completely different concerns: (1) HTTP request handling, (2) data access, (3) score calculation business logic, (4) email notification, and (5) response formatting. A change to the email template requires modifying the controller and risks breaking the entire submission flow. |
| **Correct design** | Separate into: `ContestController` (handles HTTP only, validates input), `ContestService` (business logic), `SubmissionRepository` (data access), `NotificationService` (email). The controller calls the service; the service calls the repository and notification service. |

### Scenario B — Exposing password hash via a public method

| | |
|---|---|
| **Concept violated** | **Information Hiding** |
| **Explanation** | `UserService` is leaking sensitive internal data (`password_hash`, `failedAttempts`) through its public interface. Other services have no need to — and should not — know the password hash. This is a violation of encapsulation: an implementation detail is exposed externally. |
| **Correct design** | `UserService` exposes a method `authenticate(username, password): AuthResult` that handles authentication internally. Other services call `authenticate()` or `isAuthenticated()` and never receive raw password hashes. |

### Scenario C — The Utils module as a grab bag

| | |
|---|---|
| **Concept violated** | **Modularity** (Low Cohesion) |
| **Explanation** | `Utils` has extremely low cohesion — its functions have no logical relationship with one another. `formatDate()` and `generatePDF()` have nothing in common. The module will be modified for many unrelated reasons, leading to high instability. |
| **Correct design** | Split into cohesive modules: `DateUtils`, `EmailService`, `ScoreCalculator`, `UserValidator`, `FileCompressor`, `ReportGenerator`. Each module contains only functions related to a single domain. |

### Scenario D — Depending on global config

| | |
|---|---|
| **Concept violated** | **Coupling** (High Coupling with global state) |
| **Explanation** | `JudgeService` is tightly coupled to `CONFIG.MAX_EXECUTION_TIME` — a global variable. It is impossible to test `JudgeService` with a different value without modifying the global config. This also prevents configuring different time limits per contest. |
| **Correct design** | Inject config via constructor: `JudgeService(config: JudgeConfig)`. Or inject directly: `JudgeService(maxExecTimeMs: int, maxMemoryMb: int)`. Tests can pass arbitrary values; production code injects from the config service. |

### Scenario E — Depending on a concrete implementation

| | |
|---|---|
| **Concept violated** | **Abstraction** (Dependency on Concrete, violates Dependency Inversion) |
| **Explanation** | `SubmissionService` depends on `PostgreSQLSubmissionRepository` directly. Testing requires a real PostgreSQL instance. Switching to MongoDB requires modifying `SubmissionService`. High coupling to an implementation detail. |
| **Correct design** | Define an `ISubmissionRepository` interface with `save()`, `findById()`, and `findByUser()`. `SubmissionService` depends only on the interface. Inject `PostgreSQLSubmissionRepository` in production and `InMemorySubmissionRepository` during testing. |

### Scenario F — ProblemService doing too much

| | |
|---|---|
| **Concept violated** | **Separation of Concerns** (God Service) |
| **Explanation** | `ProblemService` handles 4 different concerns: (1) problem management, (2) submission validation, (3) auto-grading, and (4) reporting. A change to the judging logic requires modifying the entire `ProblemService`. The module's reason for change is unclear. |
| **Correct design** | Split into: `ProblemService` (problem CRUD), `SubmissionService` (validate and handle submissions), `JudgeService` (auto-grading), `ReportingService` (statistics). Each service has a single, clear responsibility. |

---

## Task 3 — Architecture Decision Record (ADR-001)

| Field | Content |
|-------|---------|
| **ADR-001** | Selecting Asynchronous Architecture for the Judging System |
| **Date / Author** | \[Team fills in\] |
| **Context** | CODING WAR must satisfy two NFRs: (1) up to 500 concurrent users (NFR-01) and (2) results within 30s (NFR-02). Each submission requires compiling and running code against N test cases inside a sandbox — a process that may take 5–30 seconds. With a synchronous approach: 500 simultaneous submissions → 500 threads blocked waiting → server OOM. |
| **Decision** | Choose **Asynchronous architecture**: contestant submits → immediately receives a `submission_id` (HTTP 202) → polls `GET /submissions/{id}` or uses WebSocket to receive the result once ready. The JudgeWorker consumes from a message queue and grades independently. |
| **Positive Consequences** | (1) The API server is not blocked — it can handle significantly more requests with the same resources. (2) JudgeWorkers can scale independently — increase worker count during contest surges. (3) The queue acts as a buffer — submission spikes do not crash the system. (4) Retries are straightforward — if a JudgeWorker crashes, the message remains in the queue. |
| **Negative Consequences** | (1) More complex than synchronous — requires implementing polling or WebSocket on the client side. (2) Eventual consistency — results are not immediate; the UX must handle a "pending" state. (3) Requires managing a message queue (RabbitMQ/Kafka), adding operational overhead. |
| **Alternatives Considered** | **Synchronous**: contestant submits → waits for result. Rejected because: with 500 concurrent users, each request holds a thread for 5–30s → needs 500 threads → ~500MB memory for threads alone → not scalable. The server will time out or run out of memory during peak hours. |
| **Review Trigger** | Reconsider if: (1) the latency SLA drops below 5s (synchronous may become viable), (2) the concurrent user target drops below ~50 (synchronous is simpler), or (3) the team struggles with eventual consistency and has resources to vertically scale the server. |

---

*Back to the lab: [labs/lab-3.1.md](../labs/lab-3.1.md)*
