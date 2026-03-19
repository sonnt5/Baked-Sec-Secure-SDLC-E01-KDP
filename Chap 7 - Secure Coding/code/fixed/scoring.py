# app/services/scoring.py — FIXED version
# Lab 7.2: Integer/Arithmetic fixes (ASVS V15.4.1 compliant)
#
# Fixes applied:
#   Scenario A: Use Decimal for exact arithmetic; explicit ROUND_HALF_UP
#   Scenario B: Atomic Redis Lua script eliminates TOCTOU race condition
#   Scenario C: Validate execution_ms has a non-negative lower bound

from decimal import Decimal, ROUND_HALF_UP


# Scenario A — Fixed: Decimal precision + symmetric rounding
def calculate_penalty_score(
    base_score: int,
    wrong_attempts: int,
    time_penalty_per_attempt: Decimal = Decimal("20"),
) -> int:
    """ICPC-style penalty scoring with exact decimal arithmetic.

    No float imprecision. ROUND_HALF_UP gives the same rounding for all
    contestants regardless of the direction of fractional penalties.
    ASVS V15.3.5: variables are the correct expected type before use.
    """
    if wrong_attempts < 0:
        raise ValueError(
            f"wrong_attempts must be non-negative, got {wrong_attempts}"
        )
    total_penalty = wrong_attempts * time_penalty_per_attempt   # exact Decimal
    final_score   = Decimal(base_score) - total_penalty
    # Symmetric rounding: .5 rounds up (consistent for every contestant)
    return int(final_score.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


# Scenario B — Fixed: Atomic Redis Lua script (ASVS V15.4.1)
#
# Lua scripts run atomically inside Redis — no other command can interleave.
# The read, check, and increment happen as a single indivisible operation.
INCR_IF_BELOW_LIMIT_SCRIPT = """
local key     = KEYS[1]
local max_val = tonumber(ARGV[1])
local current = tonumber(redis.call('GET', key) or '0')
if current >= max_val then
    return -1   -- rate limit exceeded
end
return redis.call('INCR', key)  -- atomic increment
"""

MAX_SUBMISSIONS_PER_CONTEST = 10


async def increment_submission_count_atomic(
    user_id: str,
    contest_id: str,
    *,
    redis,  # redis.asyncio.Redis instance
) -> bool:
    """Atomically check-and-increment the per-user, per-contest submission quota.

    Returns True if the submission is allowed, False if the limit is reached.
    No TOCTOU race: the Lua script is atomic inside Redis.
    ASVS V15.4.1: shared objects in concurrent code protected by locking.
    """
    key = f"sub_count:{user_id}:{contest_id}"
    result = await redis.eval(
        INCR_IF_BELOW_LIMIT_SCRIPT,
        1,           # number of keys
        key,         # KEYS[1]
        MAX_SUBMISSIONS_PER_CONTEST,  # ARGV[1]
    )
    return result != -1  # -1 means rate limit exceeded


# Scenario C — Fixed: lower-bound validation on execution time
_MAX_REASONABLE_EXECUTION_MS = 60_000  # 60 seconds — no problem should exceed this


def is_within_time_limit(execution_ms: int, time_limit_ms: int) -> bool:
    """Check whether a submission's execution time is within the problem limit.

    Treats the judge result as semi-trusted: validates range before comparing.
    Negative or implausibly large values are rejected.
    ASVS V15.3.5: verify variables are the correct expected type before use.
    """
    if not (0 <= execution_ms <= _MAX_REASONABLE_EXECUTION_MS):
        raise ValueError(
            f"execution_ms {execution_ms!r} out of valid range "
            f"[0, {_MAX_REASONABLE_EXECUTION_MS}]"
        )
    return execution_ms <= time_limit_ms
