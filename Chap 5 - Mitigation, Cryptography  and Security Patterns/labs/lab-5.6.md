# Lab 5.6 — Applying Crypto to Architecture: Security Architecture Specification

> **Chapter 5 · Mitigations, Security Patterns, and Cryptography**
> Input: CDR from Lab 5.5 + Architecture | Output: Security Architecture Specification (SAS)

> [!NOTE]
> **Artifact for this lab:** Security Architecture Specification (SAS) — a document synthesizing the complete security architecture of CODING WAR: TLS/mTLS config, Envelope Encryption design, Opaque ID & Token design, Identity & Trust for distributed services. This is the most complete deliverable of Chapter 5.

## Learning Objectives

- Design a comprehensive TLS configuration — not just "enable HTTPS".
- Implement Envelope Encryption with a clean separation of concerns.
- Design a consistent Opaque ID and Token policy for the entire system.
- Design Identity & Trust for distributed CODING WAR services.
- Synthesize everything into a Security Architecture Specification — the final artifact of Chapter 5.

## Context

After 5 labs, the team has: a Mitigation Register, an Architecture Hardening Report, a Pattern Application Worksheet, an SDR Report, and a Crypto Decision Record. Lab 5.6 synthesizes all of these into a Security Architecture Specification — a single source-of-truth document for security decisions. In a real project, this document is referenced during code reviews, penetration test scoping, and compliance audits.

---

## Task 1 — TLS/mTLS Configuration Design

Design the TLS configuration for all CODING WAR communication channels:

| Channel | TLS Type | Min TLS Version | Cipher Suites / Profile | Certificate | Additional Controls |
|---------|----------|----------------|------------------------|-------------|---------------------|
| **Browser → nginx (public)** | TLS | 1.3 (1.2 min) | TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256 | Public CA (Let's Encrypt) | HSTS: max-age=31536000; includeSubDomains. OCSP stapling. ssl_session_tickets off (PFS) |
| **nginx → FastAPI (internal reverse proxy)** | mTLS | 1.2+ | ECDHE+AESGCM | Internal CA cert per service | Verify client cert CN = `fastapi-service.coding-war.internal` |
| **FastAPI → PostgreSQL** | TLS | 1.2+ | AES-256-GCM | Internal CA cert | `sslmode=verify-full`; verify server cert; reject self-signed |
| **FastAPI → Redis** | TLS | 1.2+ | AES-256-GCM | Internal CA cert | AUTH password + TLS; no plaintext fallback mode |
| **FastAPI → RabbitMQ** | mTLS | 1.2+ | AES-256-GCM | Internal CA per service | SASL + mTLS; separate vhost per service; topic-level ACLs |
| **Judge Node → API Service** | mTLS | 1.3 | AES-256-GCM | Internal CA, max 24h TTL | Certificate rotation via cert-manager; alert if cert approaching expiry |
| \[Add channel\] | | | | | |

**TLS Handshake Analysis** — Describe the TLS handshake for the most important channel (Browser → nginx). Explain each step in terms of the cryptographic primitives used:

| Step | Phase | Crypto Operation + Security Property |
|------|-------|--------------------------------------|
| **1** | **Client Hello** | Client sends: supported TLS versions, cipher suites, ClientRandom (32 bytes CSPRNG), SNI extension (`coding-war.io`). Security: ClientRandom ensures each session is unique — prevents replay. |
| **2** | **Server Hello + Certificate** | Server selects cipher suite (`TLS_AES_256_GCM_SHA384`), sends ServerRandom + Certificate (X.509 signed by Let's Encrypt CA chain). |
| **3** | **Certificate Verification** | Client verifies: (a) CA signature valid? (b) CN/SAN matches 'coding-war.io'? (c) Not expired? (d) Not revoked (OCSP)? — ensures server is who it claims to be. |
| **4** | **ECDHE Key Exchange** | Both sides generate ephemeral ECDH keypairs (P-256 curve). Share public keys → compute the same shared secret without transmitting it. Attacker only sees public values — discrete log problem. |
| **5** | **Session Keys Derived** | From ClientRandom + ServerRandom + ECDHE shared secret → HKDF → derive: client_write_key, server_write_key, client_write_IV, server_write_IV. Forward secrecy: even if long-term private key is compromised, past sessions are safe. |
| **6** | **Encrypted Application Data** | All HTTP/2 frames encrypted with AES-256-GCM: confidentiality (encrypt) + integrity (auth tag) in a single primitive. TLS record sequence numbers prevent reordering/replay. |

**nginx TLS configuration snippet:**

```nginx
# nginx/sites-available/coding-war.conf
server {
    listen 443 ssl http2;
    server_name coding-war.io;

    ssl_certificate /etc/letsencrypt/live/coding-war.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/coding-war.io/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:
                ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;   # TLS 1.3 handles this automatically
    ssl_session_tickets off;          # Disable — breaks forward secrecy

    ssl_session_cache shared:SSL:10m;

    add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains; preload' always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'" always;

    ssl_stapling on;
    ssl_stapling_verify on;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Force HTTPS redirect
server { listen 80; return 301 https://$host$request_uri; }
```

**Analysis questions:**

**Question 1:** `ssl_session_tickets off` — why is this setting important for forward secrecy? What do session tickets do to ECDHE?

**Question 2:** `ssl_prefer_server_ciphers off` — what changed from TLS 1.2 to 1.3? Why does TLS 1.3 not need this setting?

**Question 3:** The `Content-Security-Policy` header — what type of attack does it protect against? What are the consequences of not having this header, given the CDN third-party scripts from Lab 5.4?

---

## Task 2 — Envelope Encryption Design

Design and implement Envelope Encryption for submission source code in CODING WAR:

| Design Element | Specification |
|---------------|---------------|
| **Scope** | Encrypt: `submission.source_code` (per-submission); `user.email` + `user.full_name` (per-user PII) |
| **DEK (Data Encryption Key)** | AES-256 (32 bytes) from CSPRNG per-submission — not shared between submissions |
| **CMK (Customer Master Key)** | Managed in KMS (AWS KMS / HashiCorp Vault); labeled 'submissions-cmk'; 256-bit AES-256 |
| **Encryption Algorithm** | AES-256-GCM: single primitive for confidentiality + integrity; unique 96-bit nonce per encryption from `os.urandom(12)` |
| **Database Schema** | `submissions: { id (int, internal), public_id (str, CSPRNG), code_ciphertext (bytes), code_nonce (bytes), wrapped_dek (bytes), ... }` |
| **Encryption Flow** | (1) Generate DEK = `os.urandom(32)`; (2) Generate nonce = `os.urandom(12)`; (3) `ciphertext = AESGCM(DEK).encrypt(nonce, plaintext, None)`; (4) `wrapped_dek = KMS.wrap(DEK, CMK)`; (5) DEK → zero memory; (6) Store: ciphertext + nonce + wrapped_dek |
| **Decryption Flow** | (1) `KMS.unwrap(wrapped_dek, CMK) → DEK`; (2) `plaintext = AESGCM(DEK).decrypt(nonce, ciphertext, None)` — `InvalidTag` exception if tampered; (3) DEK → zero memory |
| **Key Rotation** | CMK: rotate annually → re-wrap all DEKs (no data re-encryption); DEK: immutable per submission — new submission = new DEK |
| **Access Control** | Only JudgeService and AdminService have KMS unwrap permission; rate-limited; full audit log in KMS |
| **Separation of Concerns** | Data leaked without KMS → attacker has ciphertext only (useless). KMS breached without data → nothing to decrypt. Defense in Depth. |

**Python implementation of Envelope Encryption Service:**

```python
# app/services/encryption_service.py
import os
from abc import ABC, abstractmethod
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dataclasses import dataclass

class IKeyManagementService(ABC):
    '''Interface for KMS — allows swapping between real KMS and test stub'''
    @abstractmethod
    async def wrap_key(self, dek: bytes) -> bytes: ...
    @abstractmethod
    async def unwrap_key(self, wrapped_dek: bytes) -> bytes: ...

@dataclass
class EncryptedData:
    ciphertext: bytes   # AES-GCM ciphertext + auth_tag
    nonce: bytes        # 96-bit nonce — unique per encryption
    wrapped_dek: bytes  # DEK wrapped by CMK — safe to store alongside data

class EnvelopeEncryptionService:
    def __init__(self, kms: IKeyManagementService):
        self._kms = kms

    async def encrypt(self, plaintext: str) -> EncryptedData:
        dek = os.urandom(32)  # Unique DEK per encryption — CSPRNG
        try:
            nonce = os.urandom(12)  # 96-bit nonce — MUST be unique per (key, nonce) pair
            aesgcm = AESGCM(dek)
            ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
            wrapped_dek = await self._kms.wrap_key(dek)
            return EncryptedData(ciphertext=ciphertext, nonce=nonce, wrapped_dek=wrapped_dek)
        finally:
            dek = b'\x00' * 32  # Zero DEK from memory — best effort in Python
            del dek

    async def decrypt(self, enc: EncryptedData) -> str:
        dek = await self._kms.unwrap_key(enc.wrapped_dek)
        try:
            aesgcm = AESGCM(dek)
            # InvalidTag raised if ciphertext was tampered — AEAD integrity check
            plaintext = aesgcm.decrypt(enc.nonce, enc.ciphertext, None)
            return plaintext.decode('utf-8')
        finally:
            dek = b'\x00' * 32
            del dek
            raise  # NOTE: This line has a bug — find and fix it in the exercises below
```

> [!WARNING]
> The code above has **1 intentional bug**: the `finally` block's `raise` re-raises an exception even when no exception occurred. Find the bug and fix it. This is the type of subtle bug common in crypto error handling.

**Code exercises:**
1. Fix the bug in `decrypt()`.
2. Implement `InMemoryKMSStub` for testing.
3. Write 3 pytest tests: roundtrip works, tampered ciphertext raises `InvalidTag`, unique nonce per encryption.

---

## Task 3 — Opaque IDs & Token Design

Design a consistent policy for all IDs and tokens in CODING WAR:

| ID/Token Type | Current (needs fixing) | New Design | Generation Method | Storage | Expiry / Rotation Policy |
|---------------|----------------------|-----------|------------------|---------|--------------------------|
| **Submission ID (public)** | Auto-increment integer (IDOR risk — TH-02) | `sub_<secrets.token_urlsafe(24)>` | `secrets.token_urlsafe(24)` — CSPRNG, URL-safe | DB: `public_id VARCHAR(50) UNIQUE`; internal PK remains integer for joins | Permanent — immutable per submission |
| **Password Reset Token** | `hash(email+timestamp)[:16]` — predictable (CM-03) | `secrets.token_urlsafe(32)` — 256-bit entropy | `secrets.token_urlsafe(32)` in Python | Store `hash(token)` in DB — never raw token | 15-minute TTL; single-use; invalidate on use |
| **JWT Access Token** | 30-day expiry, email+phone in payload | `sub` (user_id) + `role` + `type` + `exp`; ES256 | ECDSA P-256 private key from KMS | Stateless — verify signature; optional revocation list in Redis | 15 minutes; revoke on password change |
| **JWT Refresh Token** | Same as access — no revocation | `sub` + `jti` + `type=refresh`; stored hash in DB | ES256 + UUID v4 as jti | `hash(refresh_token)` in DB — enables revocation by jti | 7 days; rotate on use; invalidate all on password change |
| **Contest Invite Code** | \[Fill in current if applicable\] | Short code: `secrets.token_hex(6)[:8]` — 8 chars, human-typable but unpredictable | `secrets.token_hex(6)[:8]` | DB with `contest_id` + `expires_at` + `used_by` | TTL = contest start time; single-use; require login before use |
| **User ID (public-facing)** | Internal DB integer — never expose directly | `usr_<uuid4>` — generated at registration | `uuid.uuid4()` — UUID v4 CSPRNG-based | DB: `user_public_id VARCHAR(40) UNIQUE` | Permanent |

---

## Task 4 — Security Architecture Specification (SAS — Final Artifact)

Synthesize the complete CODING WAR security architecture into a Security Architecture Specification. This is the final and most important artifact of Chapter 5.

| § | Section | Source + Content to Synthesize |
|---|---------|-------------------------------|
| **1** | **Document Header** | System, Version, Author(s), Date, Status (Draft/Review/Approved), Related Documents |
| **2** | **Threat Model Reference** | Link/reference to the Threat Model Report (Ch.4 Lab 4.7). Summarize: top 5 threats, Risk Distribution (Critical/High/Medium/Low). |
| **3** | **Mitigation Summary** | From Lab 5.1. Summary table: Threat ID → Pattern applied → Implementation status (Planned/In Progress/Done). |
| **4** | **Attack Surface** | From Lab 5.2. EP count: Before/After hardening. Top remaining risks with compensating controls. |
| **5** | **Security Design Patterns Applied** | From Lab 5.3. Pattern Application Matrix — threat → pattern → control point → evidence (summary version, link to full worksheet). |
| **6** | **Anti-Patterns & Mitigations** | From Lab 5.4. List 4 anti-patterns found, severity, refactoring status (planned/done). |
| **7** | **Cryptographic Decisions** | From Lab 5.5. Summary of CDRs: password hashing (algorithm chosen), encryption at rest (Envelope Encryption), JWT signing (algorithm), key lifecycle summary. |
| **8** | **TLS/mTLS Configuration** | From Lab 5.6 Task 1. Channel table + TLS versions + cert types. Link to nginx config. |
| **9** | **Envelope Encryption Design** | From Lab 5.6 Task 2. DEK/CMK separation, encryption flow diagram, KMS integration. |
| **10** | **Opaque IDs & Token Design** | From Lab 5.6 Task 3. Summary table: all IDs/tokens, generation method, expiry policy. |
| **11** | **Defense in Depth Summary** | From Labs 5.2–5.3. Diagram or text: 5+ independent layers for critical flows (login, submission, admin). |
| **12** | **Open Issues & Accepted Risks** | List threats that were Accepted (with justification) + monitoring plan. Technical debt acknowledged. |
| **13** | **SDR Gate Readiness** | From Lab 5.4 SDR Report. Verdict + conditions. Ready for SDR? What's blocking? |
| **14** | **Next Steps** | Short roadmap: Sprint 1 (Critical fixes), Sprint 2 (High fixes), Q3 (Medium). Not a wish-list — prioritized with owners. |

> [!NOTE]
> The SAS is not a document written from scratch — it is a structured synthesis from the previous 5 labs. Its value is that a new developer, a security auditor, or a CTO can read a single document and understand the complete security posture of the system.

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| TLS Configuration table + nginx config analysis | **20** | Table covers 6+ channels; 3 analysis questions show depth — not just quoting back the config |
| Envelope Encryption — bug fix + implementation + tests | **25** | Bug fixed correctly (5 pts); InMemoryKMSStub workable (5 pts); 3 pytest tests complete and passing (15 pts) |
| Opaque IDs & Token Design table | **15** | All 6 types, specific generation method, clear storage policy, reasonable expiry |
| Security Architecture Specification — completeness | **25** | All 14 sections reference correct lab outputs; summary is detailed enough for a new reader to understand security posture |
| SAS — narrative quality | **15** | SAS reads as a real document — not copy-paste from labs; has an executive-readable summary |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-5.6.md](../solutions/sol-5.6.md)*
