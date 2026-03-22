# Solution 5.5 — Crypto Toolbox: Crypto Design Decision Record (CDR)

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 2 — Crypto Mistakes Analysis (Fixed Versions)

### CM-01: Password Hashing — Fixed

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Per SDD 3.1: Argon2id with 64MB, time_cost=4, parallelism=2
ph = PasswordHasher(
    memory_cost=65536,      # 64MB
    time_cost=4,            # iterations
    parallelism=2,          # threads
    hash_len=32,
    salt_len=16
)

def store_password(password: str) -> str:
    # Argon2id: memory-hard, includes built-in salt, OWASP recommended
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        ph.verify(hashed, password)
        return True
    except VerifyMismatchError:
        return False
```

**Why SHA-256 is dangerous:** A modern GPU can compute 10 billion SHA-256 hashes per second. A 10-character alphanumeric password (62^10 ≈ 8×10^17 combinations) would take ~10 years on SHA-256... but rainbow tables and dictionary attacks reduce this dramatically. Argon2id with 64MB memory requirement makes GPU attacks economically infeasible — GPU attacks are memory-bandwidth bound, not computation bound.

### CM-02: AES Encryption Mode — Fixed

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt(data: bytes, key: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(12)          # Unique 96-bit nonce per encryption
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)  # Includes auth tag
    return nonce, ciphertext        # Store nonce alongside ciphertext

def decrypt(nonce: bytes, ciphertext: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)  # InvalidTag if tampered
```

**Why AES-ECB is dangerous:** ECB mode encrypts each 16-byte block independently. Identical plaintext blocks produce identical ciphertext blocks. For structured data (like source code with repeated keywords), this creates visible patterns — a famous example is the "ECB penguin" where an image encrypted with ECB still shows the outline. Additionally, ECB has no integrity protection — an attacker can rearrange, remove, or replace blocks without detection.

### CM-03: Reset Token Generation — Fixed

```python
import secrets
import hashlib

def generate_reset_token() -> tuple[str, str]:
    """Returns (raw_token_for_email, hashed_token_for_db)"""
    raw_token = secrets.token_urlsafe(32)          # 256-bit CSPRNG entropy
    hashed = hashlib.sha256(raw_token.encode()).hexdigest()
    return raw_token, hashed                        # Store hash in DB, send raw in email
```

**Why the original is dangerous:** `hash(email + time.time())` has two problems: (1) `time.time()` has microsecond precision — an attacker who knows approximately when a reset was requested can enumerate ~1 million timestamps in seconds; (2) MD5 is broken for security purposes and `[:16]` reduces entropy to 64 bits — brute-forceable with GPU. The original token is functionally predictable.

### CM-04: JWT Secret — Fixed

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JWT_PRIVATE_KEY: str               # Required — RSA private key from environment
    JWT_PUBLIC_KEY: str                # RSA public key for verification
    JWT_ALGORITHM: str = 'RS256'       # Asymmetric per SDD 3.1

    class Config:
        env_file = '.env'

# In production: Keys stored in Vault/AWS Secrets Manager via CI/CD
# Generate once: 
# openssl genrsa -out private.pem 4096
# openssl rsa -in private.pem -pubout -out public.pem
```

**Why hardcoded secret is dangerous:** The secret is in version control. Anyone with repo access (current or historical) can forge JWT tokens with any payload — including admin role. Rotation requires code change and redeployment. Secret scanning tools will flag it. With RS256 (per SDD 3.1), the private key stays in KMS — only AuthService can sign, while all services verify using the public key.

### CM-05: Webhook Signature Verification — Fixed

```python
import hmac
import hashlib
import os

WEBHOOK_SECRET = os.environ['WEBHOOK_SECRET']  # Shared secret, not hardcoded

def verify_signature(body: bytes, received_sig: str) -> bool:
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    # Constant-time comparison prevents timing attacks
    return hmac.compare_digest(expected, received_sig)
```

**Why keyless hash is dangerous:** Without a secret key, anyone who knows the body content can compute the "signature" themselves. There's no authenticity — the signature only proves the body wasn't corrupted in transit, not that it came from a trusted sender. Additionally, `==` string comparison is vulnerable to timing attacks — an attacker can learn how many leading characters match by measuring response time.

### CM-06: AES Nonce Reuse — Fixed

```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_submission(code: str, key: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(12)    # MUST be unique per encryption — never static
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, code.encode('utf-8'), None)
    return nonce, ciphertext  # Store nonce with ciphertext
```

**Why static nonce destroys AEAD:** In AES-GCM, if the same (key, nonce) pair is used twice, an attacker who observes both ciphertexts can XOR them together to cancel out the keystream, recovering the XOR of the two plaintexts. This completely breaks confidentiality. Additionally, nonce reuse in GCM leaks the authentication key (GHASH key), breaking integrity — an attacker can forge any message they want. This is not a theoretical risk: the "Nonce Disrespect" attack is well-documented.

---

## Task 3 — Crypto Decision Records (Reference)

### CDR-001: Password Hashing

| Field | Content |
|-------|---------|
| **Decision** | **Argon2id** with `memory_cost=65536` (64MB), `time_cost=4`, `parallelism=2` (per SDD 3.1) |
| **Rationale** | Argon2id won the Password Hashing Competition (2015) and is the OWASP-recommended choice. The memory-hard property (64MB required per hash attempt) makes GPU/ASIC attacks impractical — GPU attacks are memory-bandwidth bound, not computation bound. bcrypt (option A) is also acceptable but does not have memory-hardness — only time-hardness. Parameters aligned with SDD 3.1 specification. |
| **Consequences (+)** | GPU-cracking is economically infeasible. Memory-hard means even a purpose-built ASIC has to dedicate significant memory per hash. OWASP-endorsed. |
| **Consequences (−)** | 64MB × parallelism per login attempt — with 1,000 concurrent logins (per PER-01), peak memory: 1,000 × 64MB × 2 = 128GB. Must tune parameters for available hardware. Requires `argon2-cffi` library. |
| **Options NOT chosen** | bcrypt: good but not memory-hard; SHA-256: fast — GPU-crackable in seconds. |
| **Evidence** | `tests/test_password.py::test_argon2_hash_takes_acceptable_time` (target: 300–800ms); `tests/test_password.py::test_argon2_verify_correct_password_returns_true` |
| **Review trigger** | When Argon2id is found vulnerable; when server hardware changes significantly (tune parameters); when OWASP changes recommendation |

### CDR-002: Submission Data Encryption

| Field | Content |
|-------|---------|
| **Decision** | **Application-level AES-256-GCM with Envelope Encryption (KMS) + TDE (Transparent Data Encryption) for PostgreSQL Volume (per SDD 7.2)** |
| **Rationale** | Defense in depth: Application-level encryption protects against SQL injection that reads plaintext data in memory — even a DB admin cannot read source code without KMS access. TDE (per SDD 7.2) provides additional protection against physical disk theft and unauthorized volume access. Together, they provide two-layer defense: attacker needs both application-level KMS access AND physical/volume access to decrypt. No encryption (option C) relies entirely on access control — insufficient for source code (intellectual property) per threat model. |
| **Consequences (+)** | Three-key defense: attacker needs ciphertext (DB) AND KMS access (application layer) AND volume encryption key (TDE layer). Compliance-friendly. Audit trail via KMS access logs. Physical disk theft protection via TDE. |
| **Consequences (−)** | Performance overhead: KMS unwrap call per submission read (~5ms latency) + TDE I/O overhead (~5-10%). Operational complexity: KMS dependency, key rotation procedures, TDE key management. Needs InMemoryKMSStub for testing. |
| **Options NOT chosen** | TDE only: insufficient against application-layer SQL injection. Application-level only: insufficient against physical disk theft. No encryption: violates data classification policy for IP. |
| **Evidence** | `tests/test_encryption.py::test_roundtrip_encrypt_decrypt`, `tests/test_encryption.py::test_tampered_ciphertext_raises_invalid_tag`, Infrastructure: TDE enabled on PostgreSQL volume per SDD 7.2 |

### CDR-003: JWT Signing Algorithm

| Field | Content |
|-------|---------|
| **Decision** | **RS256 (RSA-2048 or RSA-4096)** per SDD 3.1 |
| **Rationale** | HS256 (option A) requires sharing the signing secret with every service that verifies tokens — in a multi-service architecture, secret distribution and rotation is complex and risky. If any service is compromised, the shared secret allows forging tokens. RS256 uses asymmetric cryptography: the private key stays in KMS (only AuthService can sign), while all services verify using the public key (available from JWKS endpoint). ES256 (ECDSA P-256) produces shorter signatures but RS256 is more widely supported and specified in SDD 3.1. |
| **Consequences (+)** | Private key never leaves KMS. Any service can verify without needing signing capability. Key rotation only affects AuthService. JWKS endpoint enables automatic public key distribution. Industry-standard algorithm with broad library support. |
| **Consequences (−)** | External KMS dependency for every token issuance (~2ms). Larger signatures (~256 bytes for RSA-2048) compared to ES256 (~72 bytes). Services must fetch and cache JWKS. |
| **Options NOT chosen** | HS256: shared secret risk in multi-service setup. ES256: shorter signatures but not specified in SDD 3.1; RS256 chosen for consistency with design. |
| **Evidence** | `tests/test_jwt.py::test_rs256_token_verified_with_public_key_only`, `tests/test_jwt.py::test_algorithm_none_rejected`, `tests/test_jwt.py::test_hs256_rejected` |

---

*Back to the lab: [labs/lab-5.5.md](../labs/lab-5.5.md)*
