"""
Internal Authentication Utilities
Gap Fix: ADR-002 — HMAC-SHA256 signing for Web ↔ Judge communication
Pattern from: assets/code/fixed/internal_auth.py

IA-01: HMAC-signed payloads with timestamp (anti-replay)
IA-02: sign before enqueue, verify before processing
IA-03: Secret from environment variable
"""

import hashlib
import hmac
import json
import time
from typing import Any

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("internal_auth")

# Maximum age of a signed request (5 min) — prevents replay attacks
MAX_REQUEST_AGE_SECONDS = 300


def _get_secret() -> bytes:
    """Load HMAC secret from config. Raises at startup if missing."""
    secret = settings.judge_hmac_secret
    if not secret:
        raise RuntimeError("JUDGE_HMAC_SECRET is not set — internal auth is disabled")
    return secret.encode("utf-8")


def sign_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Sign a payload dict with HMAC-SHA256 + unix timestamp.
    Returns the payload with _ts and _sig fields added.
    """
    timestamp = str(int(time.time()))
    payload_with_ts = {**payload, "_ts": timestamp}
    canonical = json.dumps(payload_with_ts, sort_keys=True, separators=(",", ":"))
    signature = hmac.new(
        _get_secret(), canonical.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return {**payload_with_ts, "_sig": signature}


def verify_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Verify HMAC-SHA256 signature on a received payload.
    Returns the clean payload (without _sig/_ts) if valid.
    Raises ValueError on any failure — caller maps that to 403.
    """
    # Pop signature before reconstructing canonical form
    payload = dict(payload)
    signature = payload.pop("_sig", None)
    timestamp = payload.get("_ts")

    if not signature or not timestamp:
        raise ValueError("Missing _sig or _ts")

    try:
        request_time = int(timestamp)
    except (ValueError, TypeError):
        raise ValueError("Invalid _ts format")

    age = abs(time.time() - request_time)
    if age > MAX_REQUEST_AGE_SECONDS:
        raise ValueError(f"Request too old: {age:.0f}s > {MAX_REQUEST_AGE_SECONDS}s")

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    expected = hmac.new(
        _get_secret(), canonical.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # Constant-time comparison — prevents timing side-channel
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid HMAC signature")

    return {k: v for k, v in payload.items() if not k.startswith("_")}
