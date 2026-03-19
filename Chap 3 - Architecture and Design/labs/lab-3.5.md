# Lab 3.5 — Design Patterns: Identification, Selection, and Application

> **Chapter 3 · Software Architecture and Design**
> Input: Output from Lab 3.2–3.4 | Output: Pattern mapping table, refactored diagram

## Learning Objectives

- Identify patterns at 4 levels: Deployment, Structural, Tactical, and Design (OOP).
- Apply appropriate patterns to the CODING WAR architecture already designed.
- Analyze trade-offs of each pattern and recognize anti-patterns in design drafts.
- Write a Pattern Application Note: explain why a pattern was chosen for a specific context.

## Scenario

After completing the Five Views, the team conducts a *"Design Pattern Audit"* — reviewing the design to:
1. Confirm that patterns have been applied intentionally.
2. Identify areas where applying a pattern could improve quality.
3. Detect and fix anti-patterns.

---

## Task 1 — Pattern Identification Exercise

Read each technical description below and identify which Pattern is being applied (or should be applied). State: the pattern name, its level (Deployment / Structural / Tactical / Design), and your justification.

### Description A

`SubmissionService` does not directly instantiate a specific `JudgeRunner`. Instead, it receives an `IJudgeRunner` through its constructor. During testing, a `MockJudgeRunner` can be injected; in production, a `DockerJudgeRunner` is injected.

| Pattern Name | Level | Justification |
|-------------|-------|--------------|
| \[Fill in pattern name\] | \[Deployment / Structural / Tactical / Design\] | \[Fill in explanation\] |

### Description B

The CODING WAR system is divided into independent services: `AuthService`, `ProblemService`, `JudgeService`, `ContestService` — each running independently with its own database and deployment pipeline.

| Pattern Name | Level | Justification |
|-------------|-------|--------------|
| \[Fill in pattern name\] | \[Deployment / Structural / Tactical / Design\] | \[Fill in explanation\] |

### Description C

When a "Submit Solution" request arrives: the API Gateway receives it → publishes a `submission.created` message to the queue → JudgeWorker consumes the message and begins judging → publishes a `judging.completed` event → the Notification Service receives the event and notifies the user.

| Pattern Name | Level | Justification |
|-------------|-------|--------------|
| \[Fill in pattern name\] | \[Deployment / Structural / Tactical / Design\] | \[Fill in explanation\] |

### Description D

`ScoreboardService` has two operations: `UpdateScore` (write) and `GetRanking` (read). To avoid lock contention, write operations go to PostgreSQL, while read operations are served from a Redis cache that is updated asynchronously after each write.

| Pattern Name | Level | Justification |
|-------------|-------|--------------|
| \[Fill in pattern name\] | \[Deployment / Structural / Tactical / Design\] | \[Fill in explanation\] |

### Description E

All HTTP requests to CODING WAR pass through a single API Gateway. The gateway is responsible for: rate limiting, authentication token validation, request logging, and routing to the appropriate service.

| Pattern Name | Level | Justification |
|-------------|-------|--------------|
| \[Fill in pattern name\] | \[Deployment / Structural / Tactical / Design\] | \[Fill in explanation\] |

### Description F

`ProblemService` exposes an `IProblemRepository` interface. Two implementations exist: `PostgreSQLProblemRepository` (production) and `InMemoryProblemRepository` (testing). The service only knows about the interface, never about a concrete implementation.

| Pattern Name | Level | Justification |
|-------------|-------|--------------|
| \[Fill in pattern name\] | \[Deployment / Structural / Tactical / Design\] | \[Fill in explanation\] |

---

## Task 2 — Anti-pattern Detection & Refactoring

The following 4 code/design snippets from CODING WAR's draft have problems. Identify the anti-pattern and propose a refactoring:

### Anti-pattern Case 1: ContestController

```python
class ContestController:
    def handle_submit(self, request):
        user = db.query("SELECT * FROM users WHERE id=?", request.userId)
        submission = Submission(user, request.code, request.problemId)
        db.save(submission)
        result = self.compile_and_run(request.code, submission.id)
        db.update("UPDATE submissions SET verdict=? WHERE id=?", result, submission.id)
        if result == "AC":
            score = db.query("SELECT score FROM contest_scores WHERE userId=?", request.userId)
            db.update("UPDATE contest_scores SET score=? WHERE userId=?", score+100, request.userId)
        smtp.send_email(user.email, "Your result: " + result)
        return {"status": "ok", "verdict": result}
```

| | |
|---|---|
| **Anti-pattern name** | \[Fill in\] |
| **Specific problem (explanation)** | \[Fill in\] |
| **Consequences if left unfixed** | \[Fill in\] |
| **Proposed refactoring** | \[Fill in — description or short pseudocode\] |

### Anti-pattern Case 2: Utility God Class

```python
class SystemUtils:
    def format_date(date): ...
    def send_email(to, subject, body): ...
    def hash_password(password): ...
    def calculate_score(submission): ...
    def validate_username(username): ...
    def generate_pdf_report(contest_id): ...
    def compress_files(file_list): ...
    def check_plagiarism(code1, code2): ...
    def connect_to_database(): ...
    def parse_test_case_file(content): ...
```

| | |
|---|---|
| **Anti-pattern name** | \[Fill in\] |
| **Specific problem (explanation)** | \[Fill in\] |
| **Consequences if left unfixed** | \[Fill in\] |
| **Proposed refactoring** | \[Fill in\] |

### Anti-pattern Case 3: Circular Dependency

```python
# UserService needs ContestService to fetch a user's contests
class UserService:
    def __init__(self, contest_service: ContestService): ...
    def get_user_contests(self, userId):
        return self.contest_service.get_by_user(userId)

# ContestService needs UserService to validate a user
class ContestService:
    def __init__(self, user_service: UserService): ...
    def register_user(self, contestId, userId):
        user = self.user_service.findById(userId)  # circular!
```

| | |
|---|---|
| **Anti-pattern name** | \[Fill in\] |
| **Specific problem (explanation)** | \[Fill in\] |
| **Consequences if left unfixed** | \[Fill in\] |
| **Proposed refactoring** | \[Fill in\] |

### Anti-pattern Case 4: Leaky Abstraction

```python
# ProblemController directly knows about SQL internals
class ProblemController:
    def get_problems_with_filters(self, filters):
        sql = "SELECT p.*, COUNT(s.id) as solve_count FROM problems p"
        sql += " LEFT JOIN submissions s ON s.problem_id = p.id AND s.verdict='AC'"
        if filters.get('difficulty'):
            sql += f" WHERE p.difficulty = '{filters['difficulty']}'"  # SQL injection risk!
        sql += " GROUP BY p.id ORDER BY solve_count DESC"
        return db.execute(sql)
```

| | |
|---|---|
| **Anti-pattern name** | \[Fill in\] |
| **Specific problem (explanation)** | \[Fill in\] |
| **Consequences if left unfixed** | \[Fill in\] |
| **Proposed refactoring** | \[Fill in\] |

---

## Task 3 — Pattern Application Map

Based on the full CODING WAR design built across Labs 3.2–3.4, complete the Pattern Application Map (≥5 patterns):

| Pattern Name | Level | Where Applied in CODING WAR | Problem It Solves | Accepted Trade-off |
|-------------|-------|----------------------------|------------------|--------------------|
| **Repository** | Design | ISubmissionRepository + PostgreSQLImpl | Decouples service from DB technology | Extra interface layer, boilerplate |
| **Event-Driven / Message Queue** | Tactical | Submit → Queue → JudgeWorker | Decouples judging from API response path | Eventual consistency, harder to debug |
| \[Pattern 3\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| \[Pattern 4\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |
| \[Pattern 5\] | \[Fill in\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Pattern Identification (6 descriptions) | **30** | Each: correct name (3 pts) + correct level (1 pt) + justification (1 pt) |
| Anti-pattern Detection (4 cases) | **40** | Each: anti-pattern name (2 pts) + specific problem (4 pts) + reasonable refactoring (4 pts) |
| Pattern Application Map | **30** | ≥5 patterns, applied appropriately to CODING WAR context, trade-offs clearly stated |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-3.5.md](../solutions/sol-3.5.md)*
