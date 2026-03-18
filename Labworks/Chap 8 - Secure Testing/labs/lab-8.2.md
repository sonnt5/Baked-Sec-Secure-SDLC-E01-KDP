# Lab 8.2 — Security Unit Testing with pytest

> **Chapter 8 · Security Testing Strategy and Toolchain Integration**
> Input: CODING WAR FastAPI application + Coverage Matrix from Lab 8.1
> Output: pytest security test suite

## Learning Objectives

- Build a security test suite from scratch by reasoning about threats — not by following a test list.
- Understand the security test oracle: verify *absence of adverse behaviour*, not just presence of expected output.
- Write tests that would catch a regression if a security control was silently removed.
- Organise a test suite so CI can run targeted subsets without running everything.

## Code Files

| File | Role |
|------|------|
| `code/reference/tests/conftest.py` | Reference infrastructure — consult after finishing your own |
| `code/reference/tests/security/` | Reference test implementations — consult after finishing |
| `code/reference/tests/fixtures/payloads.py` | Reference payload library — consult after finishing |

> There is no starter code. You create all test files from scratch.

---

## Background

A security test oracle is different from a correctness oracle.

A correctness oracle asks: *does the system do what it is supposed to?*
A security oracle asks: *does the system fail to do what an attacker needs?*

The difference matters for how you write assertions. A correctness test asserts that a valid request returns 200. A security test asserts that an adversarial request returns 4xx *and* does not leak the token value *and* does not include a stack trace in the response body. The second and third assertions are the ones that catch real bugs.

Before writing any test, ask: what specific adverse behaviour am I preventing? If you cannot answer that question, the test is not a security test.

---

## Task 1 — Test Infrastructure

Write your own `conftest.py`.

Before writing, decide what fixtures a security test suite for CODING WAR actually needs. Think about the threats in your Coverage Matrix from Lab 8.1 — each distinct attacker role or attack condition that appears across multiple tests is a candidate for a fixture.

Address in the file's comments or docstrings:
- Why test user IDs should be fixed strings rather than randomly generated on each run
- Why the HTTP client fixture scope matters for security tests, and what breaks if the scope is set incorrectly
- Which code contract from Lab 7.1 is reflected in the admin token payload, and why

---

## Task 2 — Authentication and Session Tests

Your Coverage Matrix from Lab 8.1 identified specific threats to authentication. Write tests that produce evidence the controls for those threats are working.

Do not start by writing tests. Start by asking: what are the different ways authentication can be bypassed or weakened in CODING WAR? What does each bypass need from the application to succeed? What observable HTTP behaviour would tell you the bypass is blocked?

Write as many tests as you need to be confident that each bypass path is closed. For each test, state the security property being verified in the docstring — not just what the test does, but what attack it prevents.

---

## Task 3 — Authorization Tests

Code Contract CI-01 from Lab 7.1 states that `verify_submission_owner` must be enforced on every route that accesses submission data. Write tests that prove this contract holds.

Think about the different dimensions of authorization in CODING WAR: between contestants accessing each other's data, between contestants and admin-level access, between different roles at different endpoint types. A test suite that only checks one scenario gives weak evidence.

One test in your suite matters more than all the others: it is the one that would fail immediately if `verify_submission_owner` was accidentally removed from a single route. Identify that test in its docstring and explain why it has this property.

---

## Task 4 — Input Validation, Rate Limiting, and Cryptography Tests

Write tests covering the remaining threat categories from your Coverage Matrix.

For **input validation**: write a parametrized test that covers multiple attack classes in a single pass. For each rejection response, assert that the error body does not contain the rejected value or any internal system detail. If an error response exposes the input back to the caller, that is a separate security bug.

For **rate limiting**: think about what the test must actually prove. Asserting that the 6th request is rejected is not sufficient — you also need to assert that the first 5 were not rejected. What does a false pass look like here?

For **cryptography**: you are not testing whether Argon2 is a good algorithm in theory — you are testing whether the CODING WAR implementation uses the parameters it is supposed to. What observable behaviour lets you verify this without reading the source code?

---

## Task 5 — Coverage Assessment

After finishing your test suite, map it back to the Coverage Matrix from Lab 8.1.

For each threat row: identify which tests cover it, what evidence they produce, and whether that evidence is sufficient to satisfy the acceptance threshold in your Security Test Plan. If any threat has no test coverage, explain why — either acknowledge the gap or explain which other technique (DAST, pentest) handles it instead.

Then review `code/.github/workflows/security-tests.yml` and answer:
1. What is the trade-off of using `-x` (stop on first failure) in a security test suite? When does it help and when does it hide information?
2. The workflow uses `${{ secrets.CI_JWT_SECRET }}` rather than a hardcoded test string. What attack does this prevent, even for a test secret?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Test infrastructure | **15** | Fixtures are justified; scope reasoning is correct; code contract connection documented in the file |
| Authentication + session tests | **25** | Security oracle stated for each test; tests would catch removal of the relevant control; bypass paths are identified, not just happy-path assertions |
| Authorization tests | **25** | Critical IDOR test identified with justification; multiple dimensions of authorization covered |
| Input + rate limiting + crypto | **25** | Parametrized input test checks error body for leakage; rate limit test has correct oracle; crypto tests verify implementation parameters, not just algorithm name |
| Coverage assessment | **10** | All Coverage Matrix threats mapped; gaps are acknowledged with justification |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-8.2.md](../solutions/sol-8.2.md) after completing the lab.*
