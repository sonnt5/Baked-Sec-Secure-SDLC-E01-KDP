# Solution 7.5 — Error Handling, Logging & Dependency Management

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. Your approach may differ and still be correct.

---

## Key Insights

### The two bugs in `error_handlers.py`

**Bug 1 — Stack trace in HTTP response:** The traceback, exception message, and request URL are all returned to the client. A traceback reveals: server file paths, library versions (helping identify exploitable CVEs), database schema (from SQLAlchemy error messages), and the exact code path that failed. An attacker who can trigger exceptions reliably has a low-cost reconnaissance tool.

**Bug 2 — User enumeration via login error differentiation:** Returning `USER_NOT_FOUND` for missing users and `WRONG_PASSWORD` for existing users with wrong passwords allows an attacker to build a list of valid email addresses by trying many emails and noting which error code is returned. This list is then used for targeted credential stuffing — far more efficient than untargeted attempts.

### The correlation ID pattern

The core design: generate a short random reference (8 hex characters is sufficient — that is 4 billion possibilities, enough to correlate without revealing anything). Include it in:
- The internal log at `ERROR` level — with the full exception type, request path, and request ID
- The client response — as the only connection between "something went wrong" and the log entry

Never include the exception message, exception type, or any path in the client response. The full traceback goes to `logger.debug(..., exc_info=True)` only — an internal-only level that is disabled in production log aggregators.

### Login enumeration — timing side channel

Even if the response bodies are identical, a difference in response time can reveal whether a user exists. Looking up a non-existent user returns quickly (no bcrypt/Argon2 needed); looking up an existing user with the wrong password requires running the hash comparison (100+ ms with proper Argon2 parameters).

The fix: always run the password hash comparison, even when the user does not exist. Use a dummy hash for the non-existent-user path:

```python
hash_to_check = user.hashed_password if user else DUMMY_HASH
verify_password(password, hash_to_check)  # always runs
```

### Log schema — what "never log" means

The phrase "never log" means regardless of log level, regardless of debug mode, regardless of circumstances. The fields that must never appear in logs:
- **Raw passwords** — even failed login attempts; the attacker-supplied value is useless for investigation but catastrophic if the log is breached
- **Raw IP addresses** — PII in many jurisdictions; use a salted hash (SHA-256[:12]) for correlation without retention of personal data
- **Full JWT tokens** — a stolen log file becomes a session hijack source
- **Contestant source code** — potentially copyrighted; definitely private

Fields that should be **hashed for correlation without identification**: IP address, user agent (use a class: `browser/mobile/cli/bot`).

### Dependency audit — key findings

`passlib[argon2]` 1.7.4 — last release 2022. The library has no active maintainer. There are no known CVEs, but an unmaintained library will not receive patches for future vulnerabilities. **Recommended action:** migrate to `argon2-cffi` directly, which is actively maintained. This sprint if possible; next sprint at latest.

`python-jose[cryptography]` 3.3.0 — CVE-2024-33663 is a conditional True Positive. If the application calls `jwt.decode()` without the `algorithms` parameter, the `alg=none` bypass applies. If `algorithms=['ES256']` is always specified explicitly, the vulnerability is not exploitable. **Required action:** audit all `jwt.decode()` call sites before closing.

---

*Back to the lab: [labs/lab-7.5.md](../labs/lab-7.5.md)*
