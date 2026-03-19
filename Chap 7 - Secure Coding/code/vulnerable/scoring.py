# app/services/scoring.py — VULNERABLE version
# Lab 7.2: Integer/Arithmetic vulnerabilities
# DO NOT USE IN PRODUCTION — educational purposes only
#
# Bugs demonstrated:
#   Scenario A: implicit int→float→int conversion loses precision
#   Scenario B: TOCTOU race condition on Redis counter (read-check-set is not atomic)
#   Scenario C: missing lower-bound validation on execution time


# Scenario A: Score calculation with float conversion
def calculate_penalty_score(
    base_score: int,
    wrong_attempts: int,
    time_penalty_per_attempt: float = 20.0,
) -> int:
    """ICPC-style penalty scoring.

    BUG: float multiplication loses precision for large values.
    BUG: int(final_score) truncates (floor), not rounds — systematically
         disadvantages contestants with fractional penalties.
    """
    # ISSUE: float multiplication can lose precision for large values
    total_penalty = wrong_attempts * time_penalty_per_attempt  # float!
    final_score = base_score - total_penalty                   # float subtraction
    return int(final_score)  # truncates, does not round — asymmetric rounding


# Scenario B: Quota counter with race condition
async def increment_submission_count(user_id: str, contest_id: str) -> bool:
    """Check-then-increment submission quota.

    BUG: read → check → increment is NOT atomic.
    Two concurrent requests can BOTH read current=9, BOTH pass the check,
    and BOTH increment to 10 → 11 submissions when limit is 10.
    ASVS V15.4.1 violation.
    """
    from redis.asyncio import Redis
    redis: Redis = ...  # injected

    current = await redis.get(f"sub_count:{user_id}:{contest_id}") or 0
    current = int(current)
    MAX_SUBMISSIONS = 10  # per contest per contestant

    if current >= MAX_SUBMISSIONS:
        return False  # Rate limit exceeded

    # TOCTOU gap: another request can slip in between GET and SET
    await redis.set(f"sub_count:{user_id}:{contest_id}", current + 1)
    return True  # race condition: two concurrent requests both succeed


# Scenario C: Execution time validation
def is_within_time_limit(execution_ms: int, time_limit_ms: int) -> bool:
    """Check if a submission's execution time is within the problem limit.

    BUG: if execution_ms comes from an untrusted source (judge result JSON),
    a negative value always passes the check — every submission looks fast.
    No lower-bound validation.
    """
    # ISSUE: negative execution_ms would always pass — no negative check!
    return execution_ms <= time_limit_ms
