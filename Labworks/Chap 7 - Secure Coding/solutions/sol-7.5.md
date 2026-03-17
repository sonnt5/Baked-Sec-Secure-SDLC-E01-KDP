# Solution 7.5 — Error Handling, Logging & Dependency Management

> [!WARNING]
> **Reference Solution** — Complete the lab on your own before consulting this.

---

## Key Answers

**Why user-not-found and wrong-password return the same `AUTH_INVALID`:**
Returning different messages allows an attacker to enumerate valid email addresses by testing which emails return "user not found" vs "wrong password." With a list of valid emails, credential stuffing becomes dramatically more efficient. The timing requirement: the response time must also be constant — if the "user not found" path returns in 1ms (no DB lookup) and "wrong password" returns in 300ms (Argon2id verification), an attacker can still enumerate users by measuring latency. Fix: always run the Argon2id verification even for non-existent users (against a dummy hash) to normalize timing.

**Passlib EOL significance:**
`passlib` 1.7.4 was last updated in 2022 and the project is effectively unmaintained. There are no security patches for any future CVEs discovered in `passlib` itself. The correct migration path is to `argon2-cffi` directly — it provides the same Argon2id algorithm with an actively maintained codebase. Migration: replace `passlib.hash.argon2.hash(password)` with `argon2.PasswordHasher().hash(password)` and `passlib.hash.argon2.verify(password, hash)` with `argon2.PasswordHasher().verify(hash, password)`. Backwards-compatible: existing hashes from `passlib` can be verified by `argon2-cffi` since they use the same PHC string format.

**python-jose CVE assessment logic:**
The CVE requires that `jwt.decode()` be called without explicitly specifying `algorithms=['ES256']`. The correct triage step is: audit every call to `jose.jwt.decode()` in `app/core/security.py`. If all calls have `algorithms=['ES256']` and explicitly reject 'none', the CVE is not exploitable in this codebase — document it as "mitigated by explicit algorithm specification" and close as acceptable risk. If any call is missing the `algorithms` parameter: fix immediately. The SAST rule `coding-war.ci01.raw-sql-execute` (adapted for JWT) should catch future missing-algorithm calls.

---

*Back to the lab: [labs/lab-7.5.md](../labs/lab-7.5.md)*
