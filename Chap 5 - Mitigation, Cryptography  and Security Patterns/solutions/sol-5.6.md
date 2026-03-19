# Solution 5.6 — Applying Crypto to Architecture: Security Architecture Specification

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — TLS Configuration Analysis Answers

**Question 1 — `ssl_session_tickets off` and forward secrecy:**

TLS session tickets allow resuming a previous session without a full handshake — the server encrypts session state with a ticket encryption key (TEK) and sends it to the client. On reconnect, the client presents the ticket, the server decrypts it, and skips the ECDHE key exchange.

This breaks forward secrecy: if the TEK is compromised (even years later), an attacker who recorded past TLS sessions can decrypt all sessions that used tickets. With `ssl_session_tickets off`, every session requires a fresh ECDHE key exchange, and the ephemeral keys are never stored — past sessions are safe even if the server's private key is later compromised.

**Question 2 — `ssl_prefer_server_ciphers off` in TLS 1.3:**

In TLS 1.2, the server advertises its preferred cipher suite order and the server's preference wins. `ssl_prefer_server_ciphers on` means the server picks the cipher. `off` means the client's preference wins.

TLS 1.3 eliminated this setting entirely because TLS 1.3 only supports a small set of strong cipher suites — all of them provide forward secrecy and authenticated encryption. There are no weak ciphers to defend against, so client/server preference ordering is irrelevant. The negotiation always results in a strong cipher regardless of preference order.

**Question 3 — CSP header and third-party scripts:**

`Content-Security-Policy: default-src 'self'; script-src 'self'` prevents the browser from loading scripts from any origin other than the server itself. This directly blocks the attack vector identified in Lab 5.4 (Third-Party Hooks): even if `cdn.syntax-highlighter.com` is compromised and injects malicious JavaScript, the browser refuses to execute it because it didn't come from `'self'`.

Without the CSP header, an XSS payload in a problem description or a compromised CDN script runs with full DOM access — can steal JWT tokens from `localStorage`, read the admin dashboard contents, and exfiltrate credentials. The CSP header is the last line of defense when other controls (SRI, self-hosting) are not applied.

---

## Task 2 — Envelope Encryption Bug Fix and Tests

**Bug in `decrypt()` fixed:**

```python
async def decrypt(self, enc: EncryptedData) -> str:
    dek = await self._kms.unwrap_key(enc.wrapped_dek)
    try:
        aesgcm = AESGCM(dek)
        plaintext = aesgcm.decrypt(enc.nonce, enc.ciphertext, None)
        return plaintext.decode('utf-8')
    except Exception:
        raise  # Re-raise only if there WAS an exception
    finally:
        # Zero memory regardless of success or failure
        dek = b'\x00' * 32
        del dek
```

**Fix explanation:** The original `finally` block had `raise` unconditionally, which re-raises even when no exception occurred — `decrypt()` would always fail with a `RuntimeError: No active exception to re-raise`. The fix uses `except Exception: raise` to re-raise only when an actual exception occurred, while `finally` always zeros the DEK.

**InMemoryKMSStub:**

```python
class InMemoryKMSStub(IKeyManagementService):
    """Test stub — wrapping is identity (no real KMS needed for unit tests)"""

    async def wrap_key(self, dek: bytes) -> bytes:
        # In tests: "wrap" = prepend a marker to detect correct usage
        return b'WRAPPED:' + dek

    async def unwrap_key(self, wrapped_dek: bytes) -> bytes:
        if not wrapped_dek.startswith(b'WRAPPED:'):
            raise ValueError("Invalid wrapped DEK")
        return wrapped_dek[8:]  # Strip marker
```

**pytest tests:**

```python
import pytest
from app.services.encryption_service import EnvelopeEncryptionService, InMemoryKMSStub

@pytest.fixture
def enc_service():
    return EnvelopeEncryptionService(kms=InMemoryKMSStub())

@pytest.mark.asyncio
async def test_roundtrip_encrypt_decrypt(enc_service):
    plaintext = "def solution(n): return n * 2"
    encrypted = await enc_service.encrypt(plaintext)
    decrypted = await enc_service.decrypt(encrypted)
    assert decrypted == plaintext

@pytest.mark.asyncio
async def test_tampered_ciphertext_raises_invalid_tag(enc_service):
    from cryptography.exceptions import InvalidTag
    encrypted = await enc_service.encrypt("hello world")
    # Flip a byte in ciphertext to simulate tampering
    tampered = encrypted.__class__(
        ciphertext=bytes([encrypted.ciphertext[0] ^ 0xFF]) + encrypted.ciphertext[1:],
        nonce=encrypted.nonce,
        wrapped_dek=encrypted.wrapped_dek
    )
    with pytest.raises(InvalidTag):
        await enc_service.decrypt(tampered)

@pytest.mark.asyncio
async def test_unique_nonce_per_encryption(enc_service):
    enc1 = await enc_service.encrypt("code 1")
    enc2 = await enc_service.encrypt("code 2")
    assert enc1.nonce != enc2.nonce  # Different nonces — critical for AES-GCM security
    assert enc1.wrapped_dek != enc2.wrapped_dek  # Different DEKs per submission
```

---

*Back to the lab: [labs/lab-5.6.md](../labs/lab-5.6.md)*
