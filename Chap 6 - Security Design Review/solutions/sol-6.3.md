# Solution 6.3 — Interface Catalogue & PEP/PDP Design

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.

---

## Task 1 — Interface I7 (Webhook/External Integration)

> [!NOTE]
> **Design Note:** Interface I7 represents optional external integration capability for contest platforms. This is not part of the core SRS requirements (SRS 1.4 focuses on internal online judge for students) but is included as an extensibility point for future integrations.

| ID | ① Caller | ② Operation & Resource | ③ Authority & Privilege | ④ Boundary & Channel | Key Controls |
|----|----------|----------------------|------------------------|---------------------|-------------|
| **I7** | External webhook receiver (contest platform integration, optional) — Trust: External (untrusted) | POST /webhooks/contest-events — receive contest result notifications (data: contest_id, event_type = Internal; no PII) | Min: HMAC-SHA256 signature header (`X-Webhook-Signature`) validated with shared secret. Max impact: trigger read-only notification only — NO state changes | HTTPS → API Gateway (B1) → Webhook handler | HMAC signature verification (CM-05 fix); schema validation; idempotency key to prevent replay; no PII in webhook payload; rate limit: 100/hour/source IP |

---

## Task 2 — Additional Misuse Cases

| Misuse Case | Linked Interface | Attacker | Vector | Control | Gap |
|------------|-----------------|---------|--------|---------|-----|
| Attacker submits valid HMAC signature with old webhook payload to re-trigger a contest result notification (replay attack) | I7 | External attacker | POST /webhooks with replayed valid signature | HMAC signature (prevents forgery) | Idempotency key not yet implemented — need nonce/timestamp in signature |
| Anonymous user scrapes all problem statements to build a competing platform | I4 | Automated bot | GET /api/v1/problems with high frequency | Rate limit: 30/min/IP (Note: not specified in SDD 3.3, added as security hardening) | No per-session tracking — distributed scraping across many IPs bypasses per-IP limit |

---

## Task 3 — PEP-03: Password Reset Flow

| Field | Content |
|-------|---------|
| **PEP Location** | API Gateway + FastAPI `password_reset_handler()` endpoint |
| **PDP Location** | `PasswordResetService.validate_token()` — checks token hash in DB, TTL, and single-use status |
| **Quotas / Limits (Business Terms)** | Max 3 reset requests/hour/email (business: prevents enumeration and abuse; legitimate users rarely need more than 1 reset/hour). Max 5 reset requests/hour/IP (business: prevents distributed enumeration). Reset token TTL = 15 minutes (business: minimize window if token intercepted in email transit). Note: Different from login rate limit (30 attempts/hour per user per SDD 3.3 baseline). |
| **Enforcement Mechanism** | Redis counter per email + per IP; token stored as `hash(token)` in DB; token record deleted after first successful use |
| **Audit Requirements** | Every reset request logged to admin_audit_logs: `actor_ip_hash` (SHA-256 prefix), `email_hash` (not raw per privacy), `timestamp`, `token_used: bool`; alert if >3 requests/hour from same email hash |

---

## Task 4 — Additional Shared Infrastructure

> [!NOTE]
> **Infrastructure Note:** PgBouncer is added as connection pooling middleware (not in original SDD deployment diagram) to improve database connection management and prevent connection exhaustion under high load (1,000 concurrent users per PER-01).

| Component | Type | Risk | Mitigation | Residual Risk |
|-----------|------|------|-----------|--------------|
| **PostgreSQL connection pooling (PgBouncer, shared between services)** | Shared Infrastructure | Transaction-level isolation: if connection pool misconfigured, one service's transaction may interleave with another's | Use session-mode pooling (not transaction-mode) for services with multi-statement transactions; separate pool per service with dedicated DB user | Pool exhaustion if one service holds connections — need connection timeout and per-service limits |

---

*Back to the lab: [labs/lab-6.3.md](../labs/lab-6.3.md)*
