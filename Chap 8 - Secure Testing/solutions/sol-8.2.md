# Solution 8.2 — Security Unit Testing with pytest

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. The approach shown here is one valid path.

---

## Key Insights

### Fixed test user IDs

Fixed IDs make tests deterministic and debuggable. If `ALICE_ID` changed on every run, the `alice_submission` fixture would create a record under one ID while the IDOR test asserts access by a different ID — the test would pass vacuously. Fixed IDs also make log correlation trivial: `usr_alice_test_fixed` in a failure log unambiguously identifies the test actor.

### Client fixture scope

`scope='function'` means a fresh `AsyncClient` for every test. Security tests are especially sensitive to state leakage: a test that successfully authenticates must not carry its session into the next test. With `scope='session'`, a rate limit test that exhausts the limit would cause the next test's legitimate request to be rejected with 429 — a false failure. The scope choice is a security test design decision, not just a performance one.

### The admin token's `mfa_verified: True`

This enforces Code Contract CI-03: every `/admin/*` endpoint requires `Depends(require_admin_mfa)`. The fixture creates a token that has completed MFA, simulating a legitimate admin session. If CI-03 is changed to check a different claim name, the fixture must break — the coupling is intentional. It makes the contract requirement visible in the test infrastructure.

### The most important IDOR test

The test that matters most is the one whose failure would be immediately detectable if `verify_submission_owner` was removed from a single route. That test is the one where: Bob sends a legitimate JWT, to a real submission ID that exists, owned by Alice, and the assertion checks not just the status code but that `source_code` is absent from the response body. If the ownership check is removed, the status would still be 200 — only the source_code assertion would catch the regression.

### The rate limit oracle problem

A test that only checks the 6th request returns 429 is incomplete. It would pass even if the rate limiter triggered on request 1. The correct oracle is: requests 1-5 return something other than 429, AND request 6 returns 429. The first assertion prevents a false pass where the rate limiter is broken in the "too aggressive" direction.

### Cryptography tests — what you are actually verifying

TC-Crypto-001 (timing) does not test whether Argon2 is a good algorithm. It tests whether the implementation uses parameters with sufficient cost. If someone changes `memory_cost` from 65536 to 1024 to speed up tests, the timing test catches it — Argon2 with low cost runs in milliseconds. This is a regression test for a security parameter, not a theoretical algorithm choice.

TC-Crypto-004 (nonce uniqueness) tests AES-GCM's nonce reuse property. Two encryptions of the same plaintext with the same nonce would produce the same ciphertext — an attacker who observes two ciphertexts can XOR them and recover the XOR of the plaintexts. Different ciphertexts confirm the implementation is generating fresh nonces.

### Coverage assessment — the gaps

Unit tests cover: correct rejection of bad inputs, correct error codes, correct response structure. They do not cover: timing side-channels across the network, authentication state persistence across sessions, multi-step attack sequences that span multiple requests. Those gaps are filled by DAST (Lab 8.6) and pentest (Lab 8.8).

---

*Back to the lab: [labs/lab-8.2.md](../labs/lab-8.2.md)*
