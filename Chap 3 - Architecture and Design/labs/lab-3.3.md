# Lab 3.3 — Five Views: Interface Design & Component Design

> **Chapter 3 · Software Architecture and Design**
> Input: Output from Lab 3.2 | Output: API specs, Class diagram

## Learning Objectives

- Design an Interface View: define API contracts between components, including endpoints, request/response schemas, and error handling.
- Design a Component View: analyze the internal structure of a complex component, identify classes, methods, and relationships.
- Apply the principles of Information Hiding and Low Coupling to interface design.
- Write an Algorithm Specification for complex logic at the pseudocode level.

## Scenario

Building on Lab 3.2, the team now has an Architecture Diagram and an ER Diagram. The next step is to define the *"contracts"* between components (Interface View) and the internal structure of each component (Component View). This lab focuses on the two most critical components: **Submission & Judging Service** and **Authentication Service**.

> [!NOTE]
> **API Design Standard:** Each endpoint must have: HTTP Method + Path, request body/params schema (with data types), response schema (success + error), HTTP status codes, and preconditions/postconditions. Field names must be consistent with the Data Model from Lab 3.2.

---

## Task 1 — Interface Design: API Contract

Design REST API contracts for 5 key CODING WAR endpoints. Template for each endpoint:

| Field | Content |
|-------|---------|
| **Method + Path** | — |
| **Authentication Required** | \[ \] None · \[ \] Bearer JWT · \[ \] Admin role required |
| **Request Headers** | Content-Type: application/json |
| **Path Parameters** | — |
| **Request Body Schema** | — |
| **Response 200/201 Schema** | — |
| **Response Error Codes** | 400 · 401 · 403 · 404 · 409 · 429 · 500 |
| **Preconditions** | — |
| **Postconditions** | — |
| **Rate Limit** | — |

### API-01: POST /api/v1/auth/login

*Contestant or Admin logs into the system*

| Field | Content |
|-------|---------|
| **Method + Path** | POST /api/v1/auth/login |
| **Authentication Required** | \[ \] None · \[ \] Bearer JWT · \[ \] Admin role required |
| **Request Headers** | Content-Type: application/json |
| **Path Parameters** | — |
| **Request Body Schema** | \[Fill in fields, data types, required/optional, constraints\] |
| **Response 200 Schema** | \[Fill in response body structure\] |
| **Response Error Codes** | 400 · 401 · 403 · 404 · 409 · 429 · 500 |
| **Preconditions** | \[Conditions that must be true before calling this API\] |
| **Postconditions** | \[System state after the API call succeeds\] |
| **Rate Limit** | \[If applicable: X requests/minute per user\] |

### API-02: POST /api/v1/submissions

*Contestant submits a solution for a problem*

| Field | Content |
|-------|---------|
| **Method + Path** | POST /api/v1/submissions |
| **Authentication Required** | \[ \] None · \[ \] Bearer JWT · \[ \] Admin role required |
| **Request Headers** | Content-Type: application/json, Authorization: Bearer \<token\> |
| **Path Parameters** | — |
| **Request Body Schema** | \[Fill in fields, data types, required/optional, constraints\] |
| **Response 201 Schema** | \[Fill in response body structure\] |
| **Response Error Codes** | 400 · 401 · 403 · 404 · 409 · 429 · 500 |
| **Preconditions** | \[Conditions that must be true before calling this API\] |
| **Postconditions** | \[System state after the API call succeeds\] |
| **Rate Limit** | \[If applicable: X requests/minute per user\] |

### API-03: GET /api/v1/submissions/{id}

*Retrieve the judging result of a specific submission*

| Field | Content |
|-------|---------|
| **Method + Path** | GET /api/v1/submissions/{id} |
| **Authentication Required** | \[ \] None · \[ \] Bearer JWT · \[ \] Admin role required |
| **Request Headers** | Authorization: Bearer \<token\> |
| **Path Parameters** | `id`: UUID, required |
| **Request Body Schema** | — |
| **Response 200 Schema** | \[Fill in response body structure\] |
| **Response Error Codes** | 400 · 401 · 403 · 404 · 429 · 500 |
| **Preconditions** | \[Conditions that must be true before calling this API\] |
| **Postconditions** | \[System state after the API call succeeds\] |
| **Rate Limit** | \[If applicable\] |

### API-04: POST /api/v1/contests/{id}/register

*Contestant registers to participate in a contest*

| Field | Content |
|-------|---------|
| **Method + Path** | POST /api/v1/contests/{id}/register |
| **Authentication Required** | \[ \] None · \[ \] Bearer JWT · \[ \] Admin role required |
| **Request Headers** | Authorization: Bearer \<token\> |
| **Path Parameters** | `id`: UUID of the contest, required |
| **Request Body Schema** | \[Fill in fields, data types, required/optional, constraints\] |
| **Response 200/201 Schema** | \[Fill in response body structure\] |
| **Response Error Codes** | 400 · 401 · 403 · 404 · 409 · 429 · 500 |
| **Preconditions** | \[Conditions that must be true before calling this API\] |
| **Postconditions** | \[System state after the API call succeeds\] |
| **Rate Limit** | \[If applicable\] |

### API-05: GET /api/v1/contests/{id}/scoreboard

*Retrieve the scoreboard for a contest*

| Field | Content |
|-------|---------|
| **Method + Path** | GET /api/v1/contests/{id}/scoreboard |
| **Authentication Required** | \[ \] None · \[ \] Bearer JWT · \[ \] Admin role required |
| **Request Headers** | Authorization: Bearer \<token\> |
| **Path Parameters** | `id`: UUID of the contest, required |
| **Request Body Schema** | — |
| **Response 200 Schema** | \[Fill in response body structure\] |
| **Response Error Codes** | 400 · 401 · 403 · 404 · 429 · 500 |
| **Preconditions** | \[Conditions that must be true before calling this API\] |
| **Postconditions** | \[System state after the API call succeeds\] |
| **Rate Limit** | \[If applicable\] |

---

## Task 2 — Component Design: Internal Structure

Design the Component View for **JudgeService** — the most complex component in the system, responsible for all judging logic.

### Step 1: Class Design

Identify the classes inside JudgeService:

| Class Name | Attributes (private) | Methods (public) | Role / SRP |
|-----------|---------------------|-----------------|-----------|
| **JudgeService** | submissionRepo: ISubmissionRepo, judgeRunner: IJudgeRunner, eventBus: IEventBus | judge(submissionId): void, getResult(submissionId): JudgeResult | Orchestrates the judging flow; publishes results |
| **JudgeRunner** | maxExecTimeMs: int, maxMemoryMb: int | run(code: string, lang: Language, testInput: string): ExecutionResult | Executes user code inside a sandbox |
| **ISubmissionRepository** | *(interface)* | findById(id): Submission, save(s: Submission): void | Abstraction layer for persistence |
| \[Add class\] | \[Fill in\] | \[Fill in\] | \[Fill in\] |

### Step 2: Class Diagram

Draw a Class Diagram for `JudgeService` showing classes, interfaces, methods, attributes, and relationships (dependency, implementation, association). Ensure Information Hiding (private/public) is clearly represented.

> 📎 Insert JudgeService Class Diagram here

### Step 3: Algorithm Specification (Pseudocode)

Write pseudocode for the `JudgeService.judge(submissionId)` method. The pseudocode must cover: fetching the submission from the repo, compiling the code, running each test case, comparing output, determining the verdict (AC / WA / TLE / MLE / RE / CE), saving the result, and publishing an event.

```
PROCEDURE judge(submissionId: UUID):

  submission ← submissionRepo.findById(submissionId)

  IF submission IS NULL → RAISE SubmissionNotFoundException

  submission.status ← JUDGING

  testCases ← problemRepo.getTestCases(submission.problemId)

  compileResult ← judgeRunner.compile(submission.code, submission.language)

  IF compileResult.failed → [Fill in: handle Compile Error]

  results ← []

  FOR EACH testCase IN testCases:

    execResult ← judgeRunner.run(compileResult, testCase.input, submission.timeLimitMs)

    [Fill in: compare output and determine verdict for this test case]

    results.append(testCaseResult)

  [Fill in: aggregate final verdict based on all test case results]

  submission.verdict ← finalVerdict

  submissionRepo.save(submission)

  [Fill in: publish JudgeCompleted event]
```

> [!TIP]
> The `[Fill in]` lines are the parts you must complete. Consider: TLE (time limit exceeded), MLE (memory limit), RE (runtime error), WA (wrong answer), AC (accepted). Aggregation rule: if any test case is not AC → the final verdict reflects the worst-case result (WA / TLE / ...).

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| API Contract — 5 complete endpoints | **35** | Each endpoint: correct method/path (2 pts), complete schema with types (2 pts), error codes (2 pts), pre/postconditions (1 pt) = 7 pts/endpoint |
| Component Design — Class Table | **15** | ≥4 classes, private attributes clearly marked, public methods with signatures |
| Class Diagram (JudgeService) | **20** | Interfaces used correctly, information hiding clearly shown, dependency direction correct |
| Algorithm Pseudocode | **30** | All branches covered, verdict mapping clear, error handling present |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-3.3.md](../solutions/sol-3.3.md)*
