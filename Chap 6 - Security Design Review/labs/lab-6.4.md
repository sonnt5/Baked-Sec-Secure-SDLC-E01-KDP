# Lab 6.4 — Secure Data Handling: Classification, Token Vault & Privacy-Aware Logging

> **Chapter 6 · Security Design and Review**
> Input: Asset Register Ch.4 | Output: Data Classification Table + Token Vault Design + Log Schema

> [!NOTE]
> **Artifacts for this lab:** (1) Data Classification Table — classifying all data classes in CODING WAR. (2) Sensitive Data Flow Map — lifecycle of sensitive data from collect to delete. (3) Token Vault Design — opaque identifier mapping. (4) Privacy-Aware Log Schema — a log schema that contains no raw PII.

## Learning Objectives

- Classify data by sensitivity and apply the corresponding protection requirements.
- Map the data flow lifecycle — trace data from creation to deletion.
- Design a Token Vault and Opaque Identifier pattern following the Chapter 6 standard.
- Write a Privacy-Aware Log Schema — sufficient for investigation without exposing PII.

---

## Task 1 — Data Classification Table

Classify all important data entities in CODING WAR into 4 classes: **Public**, **Internal/Operational**, **Personal (PII)**, **High Value Asset (HVA)**:

| Data Entity | Examples | Class | Owner | Protection Goals (C/I/A/Privacy) | Design Controls (by class) |
|-------------|---------|-------|-------|----------------------------------|--------------------------|
| **User Credentials** | email, password_hash, salt | **PII + HVA** | Auth Service | C: never log raw; I: Argon2id hash; A: account lockout; Privacy: email is PII | Argon2id hashing; opaque user_id in all inter-service calls; email stored only in User DB (Data Vault pattern) |
| **Source Code Submissions** | source_code, language, submission timestamp | **PII (contestant IP)** | Submission Service | C: encrypt at rest (AES-GCM); I: AEAD integrity; Privacy: source code is contestant IP | Envelope Encryption per submission; only owner + admin can decrypt; judge sees plaintext only during execution |
| **Test Cases** | input files, expected output | **HVA** | Problem Admin | C: highest protection; I: immutable after upload; Privacy: N/A | Content-addressed storage (sha256); admin-write only; judge reads via pre-signed URLs; never exposed to contestants |
| **JWT Signing Key** | ECDSA private key | **HVA** | KMS/DevOps | C: must never leave KMS HSM; I: rotation tracked; A: signing available | KMS-managed; app never holds private key; only sign() API calls; audit every use |
| **Contest Metadata** | contest name, time, problem list | **Internal** | Contest Admin | C: partial (problem details before contest); I: tamper-evident after publication; A: available | Published via CDN after contest start; admin-write only before start; no PII |
| **Verdict & Scores** | verdict, execution time, memory usage | **Internal** | Judging Service | I: immutable after creation; A: available during contest | Append-only verdict table; hash-chain; no UPDATE after creation |
| **Access Logs** | request timestamp, IP, endpoint, status_code | **Operational** | DevOps/SRE | I: tamper-evident; A: retained 90 days; Privacy: IP must not be raw PII | IP hashed (SHA-256); no email/name in logs; correlation via opaque request_id; retain 90 days then purge |
| \[Add entity\] | | | | | |

**Legend:** 🔴 HVA = High Value Asset (highest protection) · 🟠 PII = Personal Information (privacy obligations) · ⚪ Internal = operational data · 🟢 Public = no protection required

---

## Task 2 — Sensitive Data Flow Map

Select 2 most important data entities (**Source Code Submission** and **User Credentials**) and map their complete lifecycle from Collect → Use → Share → Store → Delete:

### Data Flow: Source Code Submission

| Stage | Mechanism | Security Control | Owner | Risk | Gap |
|-------|-----------|-----------------|-------|------|-----|
| **📥 Collect** | POST /submissions — JSON payload with source_code field; TLS in transit; schema validation (size ≤64KB, language allowlist) | TLS encryption; Pydantic schema validation; rate limit enforced before data reaches business logic | API Service | Malformed large payloads; code injection attempts | None identified |
| **⚙️ Process (Judge)** | Submission passed to JudgeService via message queue; JudgeService decrypts source_code using DEK from KMS; runs in gVisor sandbox | mTLS on message queue; KMS access control for DEK; sandbox isolation; DEK zeroed after use | Judge Service | Sandbox escape; side-channel via timing; test case leakage | Verify: DEK actually zeroed in Python (GC may delay) |
| **🗄️ Store** | Encrypted ciphertext + nonce + wrapped_dek stored in submissions table; plaintext never in DB | Envelope Encryption (AES-256-GCM + CMK in KMS); DB encrypted at rest (disk encryption) | Backend + DevOps | Backup contains ciphertext — acceptable; CMK compromise = all submissions exposed | Backup encryption must be verified; CMK rotation policy enforced |
| **🤝 Share** | Owner can view own submission via API (decrypted on-the-fly); Admin can view any (with audit log); Scoreboard shows verdict only (no source code) | Object-level ownership check; admin access audit logged; scoreboard projection (no source_code field) | API Service | IDOR (TH-02); admin abuse | Admin export function needs 2-person approval (not yet implemented) |
| **🗑️ Delete (Retention End)** | After retention period (e.g., 2 years post-contest), submissions purged; crypto-shred by destroying DEK first | Retention policy enforced by scheduled job; crypto-shred: destroy DEK → ciphertext unreadable → purge record | DevOps / Data Owner | Backup copies may survive beyond primary retention | Backup purge must be explicitly verified; tombstone record for compliance |

### Data Flow: User Credentials (email + password)

| Stage | Mechanism | Security Control | Owner | Risk | Gap |
|-------|-----------|-----------------|-------|------|-----|
| **📥 Collect** | POST /auth/register — email + password over TLS; Pydantic validates email format, password strength | TLS in transit; server-side validation only (client validation is UX, not security) | Auth Service | Credential stuffing at register; user enumeration via error messages | Email verification before account activation not yet enforced |
| **⚙️ Process (Hash)** | `password → Argon2id(password, salt)` immediately on receipt; plaintext never persisted; email stored as-is in User DB | Argon2id min settings: memory_cost=65536, time_cost=3; password cleared from memory after hashing | Auth Service | Timing difference between existing/non-existing user (user enumeration) | Constant-time response needed: `dummy_verify()` when user not found |
| **🗄️ Store** | Users table: {user_id (internal int), public_id (CSPRNG), email (plaintext in User DB), password_hash, created_at} | User DB isolated from other services; email not propagated to other services — only public_id used inter-service; DB encrypted at rest | User DB / Auth Service | User DB compromise → email list exposed | Consider hashing email for storage (lookups by hash) — trade-off with account recovery |
| **⚙️ Use (Auth)** | POST /auth/login: lookup user by email; verify password with Argon2id.verify(); issue JWT (public_id, role, exp=15min) | Rate limiting + account lockout; constant-time comparison; JWT minimal claims (no email/name/phone) | Auth Service | Brute force; credential stuffing; user enumeration via timing | Account lockout not yet implemented (TH-01 critical gap) |
| **🗑️ Delete (User Request)** | GDPR right to erasure: anonymize email (replace with `'deleted_{public_id}@deleted'`), keep public_id for audit trail referential integrity | Anonymization job; verify all cross-service references use public_id (can keep for audit); email pointer deleted from User DB | Compliance / Backend | References in audit logs to deleted email may need review | GDPR erasure process not yet designed — needs legal input |

---

## Task 3 — Token Vault Design: Opaque Identifier Mapping

Design the Token Vault for CODING WAR — mapping internal primary keys to opaque tokens used in all external-facing APIs:

| Entity | Real Fields (sealed in DB) | Token (carried in system) | Scope Context | Resolution Authority | Generation Method |
|--------|--------------------------|--------------------------|--------------|---------------------|------------------|
| **User** | email, full_name, password_hash, internal user_id | `user_public_id`: `usr_<CSPRNG>` e.g. `usr_7f3a8b2c...` | All services use user_public_id; email only in User DB / Auth Service | Auth Service only (Token Vault) | `secrets.token_urlsafe(24)` at registration, never rotated (stable reference) |
| **Submission** | source_code, user_id (internal), contest_id (internal) | `sub_public_id`: `sub_<CSPRNG>` | All external APIs, scoreboard, logs use sub_public_id | Submission Service (owns mapping) | `secrets.token_urlsafe(24)` at submission time |
| **Contest** | internal contest config, test case locations | `contest_public_id`: `cst_<CSPRNG>` | Public-facing contest page URL, API responses | Contest Service | `uuid4()` at contest creation |
| **Password Reset Token** | user_id reference | `reset_token`: `rt_<CSPRNG 256-bit>` | Email link only; single-use; 15min TTL | Auth Service (validates and invalidates) | `secrets.token_urlsafe(32)`; store `hash(token)` in DB |
| **Audit Log Entry** | actor_id (internal), action details | `req_id`: `req_<CSPRNG>`; `actor_public_id` reference | Log analytics, incident investigation | Security/Ops team (privileged resolution) | `secrets.token_urlsafe(16)` per request |
| \[Team adds entity\] | | | | | |

**Token Vault resolution flow** — when a customer service needs to resolve an opaque ID to PII (break-glass scenario):

> 📎 Draw a Token Vault Resolution Flow diagram here
>
> Flow: Request with opaque token → Token Vault (privileged zone) → verify caller authorization + 2-person approval for sensitive data → return PII
> Audit: Every resolution logged with: who requested, which token, reason, timestamp, approver

---

## Task 4 — Privacy-Aware Log Schema

The following is a reference log schema for CODING WAR access logs. Review it and complete the retention + access control table.

```json
// CODING WAR — Access Log Schema (Privacy-Aware)
// Principle: Log 5W1H (who/what/when/where/why/how) without raw PII
{
  "request_id": "req_7f3a8b2c...",          // Opaque ID for correlation
  "timestamp": "2025-03-14T09:00:00.123Z",  // ISO-8601 with ms precision
  "method": "POST",
  "path": "/api/v1/submissions",             // NOT query params (may contain sensitive data)
  "status_code": 201,
  "duration_ms": 247,
  "actor_id": "usr_7f3a8b2c...",            // Opaque user ID (NOT email or name)
  "actor_role": "contestant",               // Role for access analysis
  "client_ip_hash": "a3f2b1c4...",          // SHA-256(IP) — analysis without PII
  "user_agent_class": "browser/mobile",     // Bucketed — NOT full user agent string
  "object_id": "sub_9d2c4e1a...",           // Opaque object ID affected
  "object_type": "submission",
  "correlation_id": "req_7f3a8b2c...",      // For distributed tracing
  "service": "submission-service",
  "environment": "production"
}

// FIELDS EXPLICITLY EXCLUDED (never log):
// - email, full_name, phone (PII)
// - source_code content (sensitive + large)
// - password, access_token, JWT (secrets)
// - raw IP address (PII in some jurisdictions)
// - full request body (may contain all of the above)
```

```python
# FastAPI implementation:
def build_access_log(request, response, duration_ms):
    import hashlib
    return {
        'request_id': request.state.correlation_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'method': request.method,
        'path': request.url.path,  # NOT .query (may contain tokens)
        'status_code': response.status_code,
        'duration_ms': duration_ms,
        'actor_id': getattr(request.state, 'user_public_id', 'anonymous'),
        'actor_role': getattr(request.state, 'user_role', None),
        'client_ip_hash': hashlib.sha256(
            request.client.host.encode()
        ).hexdigest()[:16],
    }
```

**Retention and access control table:**

| Log Category | Retention Period | Deletion Trigger | Access: Who Can Read | PII Included? | Tamper-Evident? |
|-------------|-----------------|-----------------|---------------------|--------------|----------------|
| **Access Logs (general)** | 90 days | Age-out automated | DevOps, SRE — not Admin App team | No (IP hashed) | Hash-chain via log aggregation system |
| **Admin Action Audit Log** | 2 years (compliance) | Retention policy end + legal hold check | Security team, Compliance — NOT App team | No (actor_public_id) | Append-only table; app user cannot delete |
| **Auth Event Log (login, logout, failed attempts)** | 90 days | Age-out | Security team for incident investigation | No (actor_public_id, ip_hash) | Hash-chain; alert on tampering |
| **Judge Execution Log** | 30 days (contest performance analysis) | Contest + 30 days | DevOps, Contest Admin — NOT contestants | No (sub_public_id) | Not required for this log type |
| \[Add log type\] | | | | | |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Data Classification Table (7+ entities) | **24** | Each entity: correct class (1 pt), protection goals reflect class (2 pts), controls match class (1 pt) |
| Sensitive Data Flow Map (2 entities × 5 stages) | **30** | Each stage: control is specific (2 pts), gap is honestly documented (1 pt). Documenting gaps is more valuable than only listing existing controls |
| Token Vault Design (5+ entities) | **20** | Scope context is specific (not "all services"); generation method is correct; resolution authority defined |
| Privacy-Aware Log Schema + Retention Table | **26** | Schema explicitly excludes named PII fields; retention periods are realistic; access control is tiered |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-6.4.md](../solutions/sol-6.4.md)*
