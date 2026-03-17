# Solution 3.2 — Five Views: Architectural Design & Data Design

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — Architectural Design

### Step 1: Functional Areas

| Functional Area | Related FRs / UCs | Responsibility |
|----------------|------------------|----------------|
| **Authentication & User Management** | FR-01 (registration), FR-02 (login), FR-03 (password reset), FR-04 (profile update) | Manages the full user account lifecycle: registration, email verification, login, role-based authorization (Contestant / Problem Setter / Admin), session management |
| **Problem Management** | FR-05 (create problem), FR-06 (manage test cases), FR-07 (publish problem) | CRUD for problems, test case management, Draft/Public status control, problem search and filtering |
| **Contest Management** | FR-08 (create contest), FR-09 (register for contest), FR-10 (time management), FR-11 (dry run) | Create/manage competitions, control timing (start/end/freeze), contestant registration, Public/Private contests |
| **Submission & Judging** | FR-12 (submit solution), FR-13 (auto-judge), FR-14 (view history) | Accept submissions, enqueue, compile and run inside a sandbox, determine verdict (AC/WA/TLE/MLE/RE/CE), return results |
| **Scoreboard & Reporting** | FR-15 (view scoreboard), FR-16 (real-time updates), FR-17 (freeze/unfreeze), NFR-04 (backup) | Score calculation per contest rules, real-time scoreboard updates, freeze at the designated time, report export |

### Step 2: Architectural Style — Recommendation: Modular Monolith

| Criterion | Monolith | **Modular Monolith** | Microservices | N-tier |
|-----------|---------|---------------------|--------------|--------|
| Meets concurrent user NFR | ~ | **+** | + | ~ |
| Easy initial deployment | + | **+** | − | + |
| Independent service scaling | − | **~** | + | − |
| Suitable for current team size | + | **+** | − | + |
| Operational complexity | + | **+** | − | ~ |
| Attack surface | ~ | **+** | − | ~ |

**Rationale for Modular Monolith:** For a learning-phase team with a system in early development, a Modular Monolith provides clear separation of concerns across modules (Auth, Problem, Contest, Judge, Scoreboard) without the overhead of a distributed system. The JudgeService can run as a separate process (worker) to scale independently without requiring full microservices. Individual modules can be extracted into microservices later if needed.

> [!NOTE]
> Microservices is also a valid answer if the justification clearly addresses team capability and scalability NFRs. The important thing is a consistent, NFR-grounded argument.

### Step 3: Architecture Diagram — Reference Structure

```
[Client Browser / Mobile]
        ↓ HTTPS
[Nginx Reverse Proxy / Load Balancer]
        ↓ HTTP
[CODING WAR Application Server]
  ├── AuthModule          → [PostgreSQL: users, sessions]
  ├── ProblemModule       → [PostgreSQL: problems, test_cases] + [MinIO: test case files]
  ├── ContestModule       → [PostgreSQL: contests, registrations]
  ├── SubmissionModule    → [PostgreSQL: submissions] → [RabbitMQ: judge_queue]
  ├── ScoreboardModule    → [PostgreSQL: scores] + [Redis: scoreboard cache]
  └── API Gateway Layer   → rate limiting, auth middleware

[JudgeWorker Process]  ← consumes from [RabbitMQ: judge_queue]
  └── Docker Sandbox → compile & run user code
        ↓ results
  [SubmissionModule via internal API or shared DB]
```

> 📎 See `assets/CODING_WAR_Architecture_Reference.pdf` for the complete Reference Diagram.

### Step 4: Traceability Matrix — Completed Example

| REQ ID | Summary | Auth | Problem | Contest | Judge | Scoreboard |
|--------|---------|------|---------|---------|-------|-----------|
| FR-01 | User registration / login | ✓ | | | | |
| FR-05 | Create / manage problems | | ✓ | | | |
| FR-12 | Submit a solution | | | | ✓ | |
| FR-08 | Create / manage contests | | | ✓ | | |
| FR-15 | View scoreboard | | | | | ✓ |
| NFR-01 | 500 concurrent users | ✓ | ✓ | ✓ | ✓ | ✓ |
| NFR-02 | Judging response ≤ 30s | | | | ✓ | |

---

## Task 2 — Data Design

### Step 1: Entities and Attributes

| Entity | Key Attributes | PK / FK | Data Constraints |
|--------|---------------|---------|-----------------|
| **User** | id, username, email, password_hash, role, is_verified, failed_login_attempts, locked_until, created_at | PK: id (UUID) | username UNIQUE NOT NULL 3–30 chars, alphanumeric; email UNIQUE NOT NULL valid format; role IN ('contestant', 'problem_setter', 'admin') |
| **Problem** | id, title, description, difficulty, time_limit_ms, memory_limit_mb, status, created_by, created_at | PK: id, FK: created_by → User | time_limit 100–10000ms; memory_limit 16–512MB; status IN ('draft', 'public'); difficulty IN ('easy', 'medium', 'hard') |
| **Submission** | id, user_id, problem_id, contest_id, language, code, status, verdict, score, submitted_at | PK: id, FK: user_id → User, problem_id → Problem, contest_id → Contest (nullable) | language IN ('cpp', 'java', 'python'); verdict IN ('pending', 'AC', 'WA', 'TLE', 'MLE', 'CE', 'RE'); code NOT NULL max 65,535 chars |
| **Contest** | id, title, start_time, end_time, freeze_time, type, status, created_by | PK: id, FK: created_by → User | type IN ('public', 'private'); start_time < end_time; freeze_time BETWEEN start_time AND end_time |
| **ContestProblem** | contest_id, problem_id, order_index, point_value | PK: (contest_id, problem_id), FK: both → Contest and Problem | order_index ≥ 1; point_value > 0 |
| **TestCase** | id, problem_id, input_storage_key, expected_output_storage_key, is_sample, order_index | PK: id, FK: problem_id → Problem | input/output stored in MinIO (S3-compatible), not in the DB directly; is_sample BOOLEAN |

### Step 3: Data Architecture Decisions

**Q1 — Database type:** Relational (PostgreSQL). CODING WAR has well-structured data with many relationships (User → Submission → Problem → Contest). PostgreSQL provides ACID transactions critical for score integrity, native UUID support, full-text search for problem lookup, and is a mature production-ready choice.

**Q2 — Caching with Redis:** Cache: (1) Scoreboard per contest — read-heavy, acceptable stale (5–10s); strategy: write-through after each AC submission. (2) User session tokens — fast lookup, natural expiry via TTL. (3) Problem list — infrequently updated, cache for 60s with TTL-based expiry.

**Q3 — Test case storage:** Test cases should not be stored in the database. Test case files can be very large (several MB per problem × thousands of problems). Databases are not optimized for storing large binary/text files. Use MinIO (S3-compatible object storage) to store the files; only store the `storage_key` reference in the DB.

**Q4 — Cascade on Submission deletion:** `RESTRICT` — do not allow a Submission to be deleted if related TestResult records exist. Submission data has forensic and audit value. If deletion is needed, use soft delete (add a `deleted_at` column) rather than hard delete.

---

*Back to the lab: [labs/lab-3.2.md](../labs/lab-3.2.md)*
