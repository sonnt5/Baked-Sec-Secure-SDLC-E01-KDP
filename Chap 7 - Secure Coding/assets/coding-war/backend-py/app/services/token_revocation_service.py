"""
Token Revocation Service
Gap Fix #4: Refresh tokens are not revocable — stored & verified only via JWT signature.
This service maintains a Redis-backed blocklist of revoked refresh token JTIs.

Usage:
  await revoke_refresh_token(jti, ttl_seconds)  — on logout
  await is_token_revoked(jti)                   — in /refresh endpoint
"""

import hashlib

import redis.asyncio as aioredis

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("token_revocation")

_redis: aioredis.Redis | None = None


async def _get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def _jti_key(jti: str) -> str:
    """
    Store a salted SHA-256 hash of the JTI — avoids leaking raw token IDs in Redis.
    Even if Redis is compromised, the blocklist cannot be reversed to recover tokens.
    """
    digest = hashlib.sha256(f"revoked:{jti}:blocklist".encode()).hexdigest()
    return f"token:revoked:{digest}"


async def revoke_refresh_token(jti: str, ttl_seconds: int) -> None:
    """
    Add a refresh token JTI to the revocation blocklist.
    TTL = remaining token lifetime so the key auto-expires when the token would anyway.
    """
    try:
        r = await _get_redis()
        await r.setex(_jti_key(jti), ttl_seconds, "1")
        logger.info("Refresh token revoked", jti_prefix=jti[:8])
    except Exception as e:
        # Non-fatal — token will expire naturally via JWT exp claim.
        logger.warning("Failed to revoke token in Redis", error=str(e))


async def is_token_revoked(jti: str) -> bool:
    """Check if a refresh token JTI has been revoked."""
    try:
        r = await _get_redis()
        return await r.exists(_jti_key(jti)) == 1
    except Exception as e:
        logger.warning("Redis revocation check failed — allowing token", error=str(e))
        return False  # Fail-open: Redis unavailable → don't block all users
