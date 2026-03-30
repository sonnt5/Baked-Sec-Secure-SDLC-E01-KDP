"""
Rate Limiting Middleware
Equivalent to: backend/src/middleware/rateLimit.ts
3 tiers: general (100/min), submission (10/min), login (5/min)
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Create global limiter with IP-based key function
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=None,  # Will be set to Redis URL at startup
)

# Rate limit strings for use in router decorators:
# @limiter.limit("10/minute")
# async def submit(...):
GENERAL_LIMIT = "100/minute"
SUBMISSION_LIMIT = "10/minute"
LOGIN_LIMIT = "5/minute"
