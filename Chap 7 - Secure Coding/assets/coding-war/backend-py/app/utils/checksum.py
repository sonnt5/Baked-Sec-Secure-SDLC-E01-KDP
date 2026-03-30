"""
SHA-256 Checksum Utilities
Equivalent to: backend/src/utils/checksumUtils.ts
SDRD: SDD 3.2.4 (Resource Downloader — Verify SHA-256)
"""

import hashlib
import hmac


def compute_sha256(content: bytes | str) -> str:
    """Compute SHA-256 hex digest of content."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def verify_sha256(content: bytes | str, expected_checksum: str) -> bool:
    """
    Verify SHA-256 checksum using timing-safe comparison.
    Prevents timing side-channel attacks.
    """
    actual_checksum = compute_sha256(content)
    # hmac.compare_digest is timing-safe (equivalent to crypto.timingSafeEqual)
    return hmac.compare_digest(actual_checksum, expected_checksum)
