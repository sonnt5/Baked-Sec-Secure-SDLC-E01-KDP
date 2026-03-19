# Lab 5.5 — Crypto Toolbox: Crypto Design Decision Record (CDR)

> **Chapter 5 · Mitigations, Security Patterns, and Cryptography**
> Input: Threat List + Architecture | Output: Crypto Decision Record (CDR)

> [!NOTE]
> **Artifact for this lab:** Crypto Design Decision Record (CDR) — a table of crypto primitive decisions for each CODING WAR use case, with a Key Lifecycle Map and analysis of crypto mistakes in the current code. Format is similar to an ADR but focused on cryptographic decisions.

## Learning Objectives

- Understand and correctly apply each primitive: CSPRNG, Hash, HMAC, AEAD, Asymmetric, Digital Signature, PKI.
- Identify crypto mistakes in code — not just "wrong library" but also design-level mistakes.
- Write a Crypto Decision Record with justification and evidence.
- Design Key Lifecycle for critical keys in CODING WAR.

## Context

Most cryptographic security failures don't come from broken algorithms (AES and RSA are still strong). They come from: wrong mode (ECB instead of GCM), static IV (reused nonce destroys AEAD), fast hash for passwords (SHA-256 is too fast — GPU-crackable), hardcoded secrets, predictable tokens from non-CSPRNG sources. This lab builds a CDR — an artifact that helps the team make crypto decisions with documented justification.

---

## Task 1 — Crypto Primitive Quick Reference

Complete the table below. The *"When NOT to use"* column is as important as *"When to use"* — many crypto mistakes come from applying the wrong primitive in the wrong context.

| Primitive | Protection Goal | When to Use in CODING WAR | When NOT to Use | Common Mistake |
|-----------|----------------|--------------------------|----------------|----------------|
| **CSPRNG** (`secrets` module, `os.urandom`) | Unpredictability / entropy | Generate: reset token, session ID, nonce/IV, public_id, JWT signing key | When only a random number for game/simulation is needed (performance), when a predictable seed is acceptable | `random.randint()` for a reset token — predictable with a known seed state |
| **SHA-256 / SHA-512 (Hash)** | Integrity fingerprint (one-way) | Verify file integrity (test cases), build artifacts, deduplication | Password storage — a fast hash is an anti-pattern | `hashlib.sha256(password)` for storing a password — GPU-crackable trivially |
| **HMAC-SHA256** | Integrity + shared authenticity | Webhook signature verification, internal API message signing | When non-repudiation is needed (use Digital Signature), when there is no shared secret | Plain hash (no key) for webhook — anyone can forge |
| **AES-256-GCM (AEAD)** | Confidentiality + Integrity in one primitive | Encrypt submission source code at rest, sensitive data in DB | AES-ECB (pattern leak), AES-CBC without MAC (no integrity) | AES-CBC then adding SHA-256 separately — Encrypt-then-MAC is complex and error-prone; use AEAD instead |
| **bcrypt / Argon2id** | Password hashing (slow, memory-hard) | Store user passwords, admin passwords | Regular data encryption — too slow for high-volume data | `MD5(password)`, `SHA256(password)` — instant GPU-cracking |
| **ECDH / ECDHE** | Key establishment (no prior shared secret) | TLS handshake (handled by framework), service-to-service key exchange | Direct data encryption — ECDH gives a shared secret, then use AES-GCM | RSA direct encryption of large data — not designed for large payloads |
| **ECDSA / RSA-PSS (Digital Signature)** | Non-repudiation + Origin authentication | JWT signing (ES256), contest result signing, software release signing | Authentication between two parties sharing a secret (use HMAC) — overkill | HMAC for scenarios needing third-party verification — HMAC cannot prove identity to a third party |
| **TLS 1.3 (Protocol)** | Channel protection (confidentiality + integrity + auth) | All HTTP traffic, service-to-service (mTLS), DB connections | Should be used for all network communication — no exceptions | TLS 1.0/1.1 (deprecated), self-signed cert in production without proper CA validation |

---

## Task 2 — Crypto Mistakes Analysis

Analyze 6 Python code snippets with crypto mistakes. For each: (a) identify the mistake, (b) explain why it is dangerous, (c) write the fixed version.

### CM-01: Password Hashing

```python
import hashlib

def store_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
```

| | |
|---|---|
| **What is the mistake?** | |
| **Why is it dangerous?** | (Not just "because the book says so" — explain the specific attack scenario) |
| **Fixed version (Python)** | (Complete code, not pseudocode) |

### CM-02: AES Encryption Mode

```python
from Crypto.Cipher import AES

def encrypt(data: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_ECB)
    padded = data + b' ' * (16 - len(data) % 16)
    return cipher.encrypt(padded)
```

| | |
|---|---|
| **What is the mistake?** | |
| **Why is it dangerous?** | (Not just "because the book says so" — explain the specific attack scenario) |
| **Fixed version (Python)** | (Complete code, not pseudocode) |

### CM-03: Reset Token Generation

```python
import random, time, hashlib

def generate_reset_token(email: str) -> str:
    token = hashlib.md5(f'{email}{time.time()}'.encode()).hexdigest()[:16]
    return token
```

| | |
|---|---|
| **What is the mistake?** | |
| **Why is it dangerous?** | (Not just "because the book says so" — explain the specific attack scenario) |
| **Fixed version (Python)** | (Complete code, not pseudocode) |

### CM-04: JWT Secret

```python
# app/core/config.py
class Settings:
    JWT_SECRET = 'coding_war_secret_2024'  # hardcoded
    JWT_ALGORITHM = 'HS256'
```

| | |
|---|---|
| **What is the mistake?** | |
| **Why is it dangerous?** | (Not just "because the book says so" — explain the specific attack scenario) |
| **Fixed version (Python)** | (Complete code, not pseudocode) |

### CM-05: Webhook Signature Verification

```python
def verify_signature(body: bytes, sig: str) -> bool:
    expected = hashlib.sha256(body).hexdigest()
    return expected == sig  # No HMAC, no key, string comparison
```

| | |
|---|---|
| **What is the mistake?** | |
| **Why is it dangerous?** | (Not just "because the book says so" — explain the specific attack scenario) |
| **Fixed version (Python)** | (Complete code, not pseudocode) |

### CM-06: AES Nonce Reuse

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

STATIC_NONCE = b'\x00' * 12  # Fixed nonce for all encryptions

def encrypt_submission(code: str, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.encrypt(STATIC_NONCE, code.encode(), None)  # Reused nonce!
```

| | |
|---|---|
| **What is the mistake?** | |
| **Why is it dangerous?** | (Not just "because the book says so" — explain the specific attack scenario) |
| **Fixed version (Python)** | (Complete code, not pseudocode) |

---

## Task 3 — Crypto Decision Record (CDR)

Write a CDR for the most important crypto decisions in CODING WAR. CDR format is similar to an ADR — capture context, decision, and consequences.

### CDR-001: Password Hashing Algorithm

| Field | Content |
|-------|---------|
| **Context** | CODING WAR needs to store passwords for contestants and admins. The team has 2 options: (A) bcrypt with cost 12, (B) Argon2id with memory_cost=65536, time_cost=3. Currently using SHA-256 (see CM-01 — needs fixing). |
| **Decision (chosen option)** | |
| **Rationale** | (Why this option is better than the alternatives — must have specific reasons related to the threat model) |
| **Consequences (+/-)** | (Positive: security properties gained; Negative: trade-offs, limitations, operational complexity) |
| **Options NOT chosen** | (And the reason for rejecting — not just "it's bad" but specific reasons) |
| **Evidence** | (Test / config / benchmark proving the decision is correct) |
| **Review trigger** | (Conditions that would trigger a review of this decision) |

### CDR-002: Submission Data Encryption (at rest)

| Field | Content |
|-------|---------|
| **Context** | Contestants' source code is sensitive data (IP, effort). It needs to be encrypted at rest. Options: (A) Database-level TDE, (B) Application-level AES-256-GCM with Envelope Encryption (KMS), (C) No encryption (access control only). |
| **Decision (chosen option)** | |
| **Rationale** | (Why this option is better than alternatives — specific reasons related to the threat model) |
| **Consequences (+/-)** | (Positive: security properties gained; Negative: trade-offs, limitations, operational complexity) |
| **Options NOT chosen** | (And the specific reason for rejecting) |
| **Evidence** | (Test / config / benchmark proving the decision is correct) |
| **Review trigger** | (Conditions that would trigger a review) |

### CDR-003: JWT Signing Algorithm

| Field | Content |
|-------|---------|
| **Context** | CODING WAR needs to issue JWT tokens. Options: (A) HS256 (symmetric — single secret shared between all services), (B) RS256 (RSA-PKCS1v1.5), (C) ES256 (ECDSA P-256). Performance and security implications differ. |
| **Decision (chosen option)** | |
| **Rationale** | (Why this option is better than alternatives — specific reasons related to the threat model) |
| **Consequences (+/-)** | (Positive: security properties gained; Negative: trade-offs, limitations, operational complexity) |
| **Options NOT chosen** | (And the specific reason for rejecting) |
| **Evidence** | (Test / config / benchmark proving the decision is correct) |
| **Review trigger** | (Conditions that would trigger a review) |

---

## Task 4 — Key Lifecycle Map

Design the Key Lifecycle for the 2 most critical keys in CODING WAR: the JWT Signing Key and the DEK (Data Encryption Key) for submission source code. The lifecycle has 5 phases: Generate → Store → Use → Rotate → Retire.

| Phase | JWT Signing Key (ECDSA P-256) | DEK (AES-256 for submission encryption) | Responsible Party | Audit Trail |
|-------|------------------------------|----------------------------------------|------------------|-------------|
| **Generate** | CSPRNG within KMS at deploy time; key pair stored in KMS — private key never leaves KMS HSM | CSPRNG (`os.urandom(32)`) per-submission — not per-user, not static | DevOps / Security team | KMS: CreateKey event logged with key ID, purpose, creator |
| **Store** | KMS/HSM — private key in hardware-protected storage; public key in config/JWKS endpoint | KMS wraps DEK with CMK; wrapped DEK stored alongside ciphertext in DB — never plaintext in DB | KMS admin role only | KMS key policy: role-based, audited |
| **Use** | App calls KMS sign API per JWT issue; KMS returns signature — app never sees private key | App calls KMS unwrap API to get plaintext DEK; DEK used for AES-GCM decrypt; DEK zeroed from RAM immediately after use | Application service account (scoped permission) | KMS: every sign/decrypt call logged with caller identity |
| **Rotate** | Every 90 days + immediately if compromise suspected; new key → overlap period (both keys valid) → invalidate old key | CMK: rotate annually; re-wrap all DEKs with new CMK (no data re-encryption needed); DEK: immutable (each submission has own DEK, never rotated) | Security team approval (Separation of Privilege) | Rotation event + old key retirement + re-wrap confirmation |
| **Retire** | Old private key deleted from KMS; public key kept for historical JWT verification for 1 rotation period; crypto-shred confirmation | Old CMK deleted after all DEKs re-wrapped; crypto-shred = data encrypted with old CMK becomes inaccessible; verify 0 DEKs still using old CMK | Security team + mandatory audit | Deletion event + `count_of_active_deks_using_old_key = 0` verification |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Crypto Primitive Quick Reference | **20** | The "When NOT to use" column is specific and accurate (not just "when crypto is not needed") — this is the hardest criterion |
| Crypto Mistakes — 6 cases | **30** | Each case: mistake correctly identified (1 pt) + specific attack scenario (2 pts) + working fixed Python code (2 pts) |
| Crypto Decision Record — 3 CDRs | **30** | Each CDR: decision justified by the threat model (4 pts) + consequences are honest about trade-offs (3 pts) + evidence is testable (3 pts) |
| Key Lifecycle Map | **20** | All 5 phases for both keys; responsible party assigned; audit trail is specific (not just "logged") |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-5.5.md](../solutions/sol-5.5.md)*
