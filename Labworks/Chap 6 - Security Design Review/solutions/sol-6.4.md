# Solution 6.4 — Secure Data Handling: Classification, Token Vault & Privacy-Aware Logging

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.

---

## Task 1 — Additional Data Entity

| Data Entity | Examples | Class | Owner | Protection Goals | Design Controls |
|-------------|---------|-------|-------|-----------------|----------------|
| **Session Tokens (Redis)** | JWT refresh tokens, session state | **HVA** | Auth Service | C: must not be accessible outside Redis; I: token must not be forgeable; A: Redis high availability | Redis accessible only from app server (not internet); token stored as hash if persistence needed; TTL enforced; revocation via jti blocklist |

---

## Task 2 — Key Gaps from Sensitive Data Flow Maps

The most important gaps identified:

**Source Code Submission gaps:**
1. DEK zeroing in Python is "best effort" — CPython's garbage collector may delay actual memory clearing. Mitigation: use `ctypes.memset` or `mlock`/`mprotect` for production security-critical code.
2. Admin export function lacks 2-person approval — a single admin can export all submissions without oversight. Must be implemented before production.

**User Credentials gaps:**
1. Account lockout not yet implemented — TH-01 critical gap. The entire Collect → Use (Auth) stage is vulnerable to brute force.
2. Constant-time response for non-existent users not implemented — user enumeration via timing is possible on the login endpoint.
3. GDPR erasure process not designed — legal team input required before production deployment.

---

## Task 3 — Token Vault Resolution Flow Description

```
Request (with opaque token)
        ↓
Token Vault Service (privileged zone)
        ↓
1. Verify caller identity (mTLS cert for service-to-service; MFA for human)
2. Check caller's authorization level:
   - Standard: resolve sub_public_id → submission_id (no PII)
   - Elevated: resolve usr_public_id → email (requires justification)
   - Break-glass: resolve any token → PII (requires 2-person approval + reason)
        ↓
3. Log resolution event:
   {resolver_id, token_type, resolution_reason, timestamp, approver_if_needed}
        ↓
Return resolved value (with minimum necessary fields only)
```

Every resolution is append-only in the audit log. Break-glass access triggers an automated alert to the security team.

---

## Task 4 — Log Schema Analysis

The provided log schema correctly excludes: email, full_name, phone, password, access_token, JWT, raw IP address, source code, full request body. Key design decisions:
- `client_ip_hash` using SHA-256 prefix (16 chars) allows correlation across requests without storing PII, while still preventing exact IP reconstruction.
- `user_agent_class` (bucketed) provides browser/mobile/bot signal without storing the full user agent string that could enable fingerprinting.
- `object_id` is the opaque public_id — investigators can look up submissions by their public ID without needing DB internal integer keys.

---

*Back to the lab: [labs/lab-6.4.md](../labs/lab-6.4.md)*
