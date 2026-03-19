# Solution 5.2 — Structural Mitigations: Architecture Hardening

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — Attack Surface Score Comparison

**Before Hardening:**
- EP-1.1 (Login): HIGH=3, EP-1.2 (Register): MEDIUM=2, EP-1.3 (Problems): LOW=1, EP-1.4 (Submissions): CRITICAL=4, EP-1.5 (Password Reset): MEDIUM=2, EP-1.6 (Admin): CRITICAL=4, EP-1.7 (Sub getById): MEDIUM=2, EP-1.8 (Scoreboard): LOW=1, EP-2 (Queue): HIGH=3, EP-3 (MinIO): HIGH=3
- **Total Score Before: 25** | CRITICAL EPs: 2 | HIGH EPs: 3 | Public EPs without rate limit: 4

**After Hardening (proposed):**
- EP-1.6 Admin: reduce from CRITICAL to HIGH via IP allowlist + VPN (−1)
- EP-1.2 Register: reduce from MEDIUM to LOW via email verification + rate limit (−1)
- EP-3 MinIO: reduce from HIGH to MEDIUM via network policy + access logging (−1)
- **Total Score After: 22** | CRITICAL EPs: 1 | HIGH EPs: 2 | Public EPs without rate limit: 0

---

## Task 3 — Data Minimization (Reference Answers)

### API Responses
**Proposed minimization:** Create a `UserPublicResponse` Pydantic model that includes only: `id` (opaque public_id, not DB integer), `username`, `role`. Exclude: email, phone, DOB, created_at, last_login_ip, password_hash_preview, internal_db_id.

**Implementation:** `class UserPublicResponse(BaseModel): id: str; username: str; role: str` — FastAPI route returns `response_model=UserPublicResponse`. Internal DB integer never leaves the service boundary.

### Error Messages
**Proposed minimization:** Global exception handler maps all DB exceptions to generic errors: `{'error': 'email_already_registered', 'code': 'CONFLICT'}`. No DB details, no table names, no constraint names.

**Implementation:**
```python
@app.exception_handler(IntegrityError)
async def db_integrity_error_handler(request, exc):
    logger.error(f"DB integrity error: {exc}")  # Log internally
    return JSONResponse(status_code=409, content={"error": "resource_conflict"})
```

### Application Logs
**Proposed minimization:** Log structured fields without PII or code content: `{user_id: uuid, submission_id: uuid, action: 'submit', language: 'python', timestamp: ISO8601}`. Never log source code, email addresses, or IP in application logs (IP only in access logs with 30-day retention).

**Implementation:** Pydantic `AuditEvent` model with explicit fields — no `**kwargs`. Custom log formatter strips any field matching email/code pattern as a safety net.

### URLs & IDs
**Proposed minimization:** Replace auto-increment submission IDs with `public_id = secrets.token_urlsafe(24)`. Password reset URL: `/reset-password` with POST body `{token: <value>}` — token never in URL.

**Implementation:** `submission.public_id` generated at creation with `secrets.token_urlsafe(24)`. All public-facing APIs use `public_id`; internal DB joins use integer PK.

### JWT Token Payload
**Proposed minimization:** JWT payload contains only: `{sub: user_public_id, role: 'contestant', type: 'access', exp: ...}`. No email, no full_name, no phone. Role is a single string (not list) for simplicity.

**Implementation:** `create_access_token(user: User)` extracts only `user.public_id` and `user.role` — no other fields included regardless of what's on the User model.

---

## Task 4 — PEP/PDP (Additional Locations)

| Location | PEP or PDP? | Policy | Boundary | Implementation |
|----------|-------------|--------|---------|----------------|
| **SubmissionController.getById()** | PEP | Enforce: `submission.user_id == current_user.id` OR `current_user.role == 'admin'` | B2 → resource | `Depends(verify_submission_ownership_or_admin)` |
| **Rate Limiter (Redis sliding window)** | PEP + PDP | Decide AND enforce: counter < limit → allow; counter ≥ limit → 429 | B1 | Redis counter + FastAPI middleware |
| **Email verification gate** | PDP → PEP | Decide: `user.is_verified == True`; enforce at login and submission | B1 → B2 | `Depends(require_verified_user)` dependency |

---

*Back to the lab: [labs/lab-5.2.md](../labs/lab-5.2.md)*
