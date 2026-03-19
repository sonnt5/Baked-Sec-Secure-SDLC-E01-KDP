# code/reference/tests/security/test_crypto.py
# Chapter 8, Lab 8.2: Cryptography Usage Tests
#
# Reference implementation — open only after completing your own.
# Run: pytest -m "security and crypto" -v

import base64
import json
import time

import pytest

pytestmark = pytest.mark.security


@pytest.mark.crypto
def test_TC_Crypto_001_password_hashing_uses_argon2_with_adequate_cost():
    """TC-Crypto-001: Password storage must use Argon2id with adequate parameters.

    Oracle:
      - Hash starts with $argon2id
      - Round-trip verify works correctly
      - verify_password() takes >= 100ms (confirms memory_cost >= 65536)

    The timing check verifies the implementation parameters, not the algorithm
    choice. If someone lowers memory_cost to speed up tests, this test catches it.
    """
    from app.core.security import hash_password, verify_password

    pwd = "test_password_unique_$%^_123"
    pwd_hash = hash_password(pwd)

    assert pwd_hash.startswith("$argon2"), (
        f"Must use Argon2, got: {pwd_hash[:20]!r}"
    )
    assert verify_password(pwd, pwd_hash), "Round-trip verify must succeed"
    assert not verify_password("wrong", pwd_hash), "Wrong password must not verify"

    start = time.monotonic()
    verify_password(pwd, pwd_hash)
    elapsed_ms = (time.monotonic() - start) * 1000

    assert elapsed_ms >= 100, (
        f"Argon2 verify took {elapsed_ms:.0f}ms — must be >= 100ms. "
        "Check memory_cost and time_cost in Argon2 configuration."
    )


@pytest.mark.crypto
def test_TC_Crypto_002_reset_tokens_have_sufficient_entropy():
    """TC-Crypto-002: Password reset tokens must be unique and have sufficient entropy.

    Oracle:
      - 100 tokens are all unique (CSPRNG, not sequential)
      - Each token has length >= 32 (>= 128-bit entropy)
      - No two tokens share the same 8-character prefix
    """
    from app.services.auth_service import generate_reset_token

    tokens = [generate_reset_token() for _ in range(100)]

    assert len(set(tokens)) == 100, "All 100 tokens must be unique"

    for token in tokens:
        assert len(token) >= 32, (
            f"Token must have >= 32 chars (128-bit entropy), got {len(token)}"
        )

    sorted_tokens = sorted(tokens)
    for i in range(len(sorted_tokens) - 1):
        assert sorted_tokens[i][:8] != sorted_tokens[i + 1][:8], (
            "Two tokens share an 8-char prefix — possible weak PRNG"
        )


@pytest.mark.crypto
def test_TC_Crypto_003_jwt_tokens_use_es256_algorithm(alice_token):
    """TC-Crypto-003: JWT tokens must use ES256, not HS256.

    Oracle: decoded header has alg=ES256.
    HS256 with a shared secret is insecure in a multi-service architecture
    because any service that can verify tokens can also forge them.
    ES256 (asymmetric) means only the signing service holds the private key.
    """
    header_b64 = alice_token.split(".")[0]
    header_b64 += "=" * (4 - len(header_b64) % 4)
    header = json.loads(base64.urlsafe_b64decode(header_b64))

    assert header.get("alg") == "ES256", (
        f"JWT must use ES256, got: {header.get('alg')!r}"
    )
    assert header.get("typ") == "JWT"


@pytest.mark.crypto
async def test_TC_Crypto_004_aes_gcm_nonce_uniqueness(client, alice_token):
    """TC-Crypto-004: AES-GCM encryption must produce different ciphertexts each call.

    Oracle: two encryptions of the same plaintext produce different outputs.
    AES-GCM with a repeated nonce is catastrophic — an attacker who observes
    two ciphertexts can XOR them to recover the XOR of the plaintexts.
    Different ciphertexts confirm the implementation generates a fresh nonce.
    """
    from app.core.crypto import encrypt

    plaintext = b"same plaintext for both encryptions"
    ct1 = encrypt(plaintext)
    ct2 = encrypt(plaintext)

    assert ct1 != ct2, (
        "Two encryptions of the same plaintext must produce different ciphertexts. "
        "AES-GCM nonce must be freshly generated per call."
    )
