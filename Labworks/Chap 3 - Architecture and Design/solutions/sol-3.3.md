# Solution 3.3 — Five Views: Interface Design & Component Design

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — API Contract (5 endpoints)

### API-01: POST /api/v1/auth/login

| Field | Content |
|-------|---------|
| **Method + Path** | POST /api/v1/auth/login |
| **Authentication Required** | None |
| **Request Body Schema** | `{ "username": string (required, 3–30 chars), "password": string (required, min 8 chars) }` |
| **Response 200 Schema** | `{ "access_token": string (JWT), "refresh_token": string (JWT), "expires_in": 3600, "user": { "id": UUID, "username": string, "role": string } }` |
| **Response Error Codes** | 400 (missing/invalid fields), 401 (wrong credentials), 423 (account locked), 429 (rate limit exceeded) |
| **Preconditions** | The user account exists and has been email-verified |
| **Postconditions** | A session is created; refresh token is persisted in the DB; access_token is returned to the client |
| **Rate Limit** | 10 requests/minute per IP; account locked for 15 minutes after 5 failed attempts |

### API-02: POST /api/v1/submissions

| Field | Content |
|-------|---------|
| **Method + Path** | POST /api/v1/submissions |
| **Authentication Required** | Bearer JWT (Contestant role) |
| **Request Body Schema** | `{ "problem_id": UUID (required), "language": enum["cpp","java","python"] (required), "code": string (required, max 65535 chars), "contest_id": UUID (optional) }` |
| **Response 201 Schema** | `{ "submission_id": UUID, "status": "pending", "submitted_at": ISO8601, "problem_id": UUID, "language": string }` |
| **Response Error Codes** | 400 (invalid language/empty code), 401 (not authenticated), 403 (contest not started or already ended), 404 (problem not found), 429 (rate limit exceeded) |
| **Preconditions** | User is authenticated; problem exists with status=public; if contest_id is provided, the contest is active and the user is registered |
| **Postconditions** | Submission saved with status=pending; message published to judge_queue |
| **Rate Limit** | 30 submissions/hour per user |

### API-03: GET /api/v1/submissions/{id}

| Field | Content |
|-------|---------|
| **Method + Path** | GET /api/v1/submissions/{id} |
| **Authentication Required** | Bearer JWT |
| **Path Parameters** | `id`: UUID of the submission |
| **Response 200 Schema** | `{ "id": UUID, "status": enum, "verdict": enum, "score": int, "language": string, "submitted_at": ISO8601, "judged_at": ISO8601 \| null, "test_results": [{ "test_case_id": UUID, "verdict": string, "time_ms": int, "memory_mb": int }] }` |
| **Response Error Codes** | 401 (not authenticated), 403 (not the owner and not Admin), 404 (submission not found) |
| **Preconditions** | Submission exists; caller is the submission owner or is an Admin |
| **Postconditions** | Read-only; no state change |

### API-04: POST /api/v1/contests/{id}/register

| Field | Content |
|-------|---------|
| **Method + Path** | POST /api/v1/contests/{id}/register |
| **Authentication Required** | Bearer JWT (Contestant role) |
| **Path Parameters** | `id`: UUID of the contest |
| **Request Body Schema** | *(no body)* |
| **Response 200 Schema** | `{ "contest_id": UUID, "user_id": UUID, "registered_at": ISO8601 }` |
| **Response Error Codes** | 401 (not authenticated), 403 (private contest; user not invited), 404 (contest not found), 409 (already registered), 422 (contest already ended) |
| **Preconditions** | Contest exists; contest has not ended; if private, user is in the invitation list |
| **Postconditions** | ContestRegistration record created; user can now submit within the contest |

### API-05: GET /api/v1/contests/{id}/scoreboard

| Field | Content |
|-------|---------|
| **Method + Path** | GET /api/v1/contests/{id}/scoreboard |
| **Authentication Required** | Bearer JWT (optional — public contests may be viewable without auth) |
| **Path Parameters** | `id`: UUID of the contest |
| **Response 200 Schema** | `{ "contest_id": UUID, "is_frozen": boolean, "last_updated": ISO8601, "rankings": [{ "rank": int, "user_id": UUID, "username": string, "total_score": int, "problems": [{ "problem_id": UUID, "solved": boolean, "attempts": int, "solve_time_minutes": int \| null }] }] }` |
| **Response Error Codes** | 403 (private contest; user not registered), 404 (contest not found) |
| **Preconditions** | Contest exists; if private, user is registered |
| **Postconditions** | Read-only; if is_frozen=true, data reflects state at freeze_time |

---

## Task 2 — Component Design: JudgeService

### Step 1: Class Design

| Class | Attributes (private) | Methods (public) | Role |
|-------|---------------------|-----------------|------|
| **JudgeService** | submissionRepo: ISubmissionRepo, problemRepo: IProblemRepo, judgeRunner: IJudgeRunner, eventBus: IEventBus | `judge(submissionId: UUID): void`, `getResult(submissionId: UUID): JudgeResult` | Orchestrator — coordinates the entire judging flow without containing specific business logic |
| **JudgeRunner** | maxExecTimeMs: int, maxMemoryMb: int, sandboxFactory: ISandboxFactory | `compile(code: string, lang: Language): CompileResult`, `run(compiled: CompileResult, input: string, timeLimitMs: int): ExecutionResult` | Executes code safely inside a sandbox |
| **VerdictDeterminer** | *(stateless)* | `determine(expected: string, actual: ExecutionResult): TestCaseVerdict`, `aggregate(results: TestCaseVerdict[]): FinalVerdict` | Pure verdict logic — easy to unit test in isolation |
| **ISubmissionRepository** | *(interface)* | `findById(id: UUID): Submission`, `save(s: Submission): void`, `updateStatus(id: UUID, status: Status): void` | Abstraction for persistence |
| **JudgeEventPublisher** | eventBus: IEventBus | `publishCompleted(submissionId: UUID, verdict: FinalVerdict): void` | Publishes domain events |

### Step 3: Complete Algorithm Pseudocode

```
PROCEDURE judge(submissionId: UUID):

  submission ← submissionRepo.findById(submissionId)
  IF submission IS NULL → RAISE SubmissionNotFoundException(submissionId)

  submission.status ← JUDGING
  submissionRepo.updateStatus(submissionId, JUDGING)

  testCases ← problemRepo.getTestCases(submission.problemId)
  IF testCases.isEmpty() → RAISE NoTestCasesException(submission.problemId)

  compileResult ← judgeRunner.compile(submission.code, submission.language)

  IF compileResult.failed:
    submission.verdict ← CE
    submission.status ← COMPLETED
    submissionRepo.save(submission)
    eventPublisher.publishCompleted(submissionId, CE)
    RETURN

  results ← []
  FOR EACH testCase IN testCases:
    execResult ← judgeRunner.run(compileResult, testCase.input, submission.timeLimitMs)

    IF execResult.timedOut:
      testVerdict ← TLE
    ELSE IF execResult.memoryExceeded:
      testVerdict ← MLE
    ELSE IF execResult.runtimeError:
      testVerdict ← RE
    ELSE IF normalize(execResult.output) == normalize(testCase.expectedOutput):
      testVerdict ← AC
    ELSE:
      testVerdict ← WA

    results.append(TestCaseResult(testCase.id, testVerdict, execResult.timeMs, execResult.memoryMb))

  # Aggregate verdict: priority CE > RE > MLE > TLE > WA > AC
  finalVerdict ← AC
  FOR EACH result IN results:
    IF result.verdict != AC:
      finalVerdict ← result.verdict  # take the first non-AC verdict
      BREAK

  submission.verdict ← finalVerdict
  submission.status ← COMPLETED
  submission.testResults ← results
  submissionRepo.save(submission)

  eventPublisher.publishCompleted(submissionId, finalVerdict)
```

---

*Back to the lab: [labs/lab-3.3.md](../labs/lab-3.3.md)*
