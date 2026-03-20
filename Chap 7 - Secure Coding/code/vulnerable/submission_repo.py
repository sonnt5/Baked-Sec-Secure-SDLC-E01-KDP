# app/repositories/submission_repo.py — VULNERABLE version
# Lab 7.3: SQL Injection (IS-01 and IS-02)
# DO NOT USE IN PRODUCTION — educational purposes only
#
# Bugs demonstrated:
#   IS-01: ORDER BY injection — sort_field from user input concatenated directly
#          into SQL string. ORDER BY cannot be parameterized, so this is a
#          genuine injection sink even when using a parameterized DB driver.
#   IS-02: LIKE injection — search query concatenated into raw SQL with f-string.
#          db.execute() called with a user-controlled string.

from sqlalchemy.ext.asyncio import AsyncSession


# IS-01: ORDER BY injection
# VULNERABLE: sort_field comes from GET /submissions?sort=score_asc (user input)
# f-string puts it directly into the SQL string — ORDER BY cannot be parameterized
async def get_submissions_by_contest(
    db: AsyncSession,
    contest_id: str,
    sort_field: str = "score",   # user-supplied, unvalidated
    order: str = "desc",
) -> list:
    """Fetch contest submissions with user-controlled sort order.

    BUG (IS-01 — ASVS V1.2.4 violation):
      sort_field is interpolated directly into the SQL string.
      An attacker can supply: sort_field="score; DROP TABLE submissions; --"
      or use time-based blind SQLi: sort_field="CASE WHEN (SELECT ...)>0 THEN score ELSE 0 END"
    """
    # VULNERABLE: f-string interpolation of user input into SQL
    query = f"SELECT * FROM submissions WHERE contest_id='{contest_id}' ORDER BY {sort_field} {order}"
    result = await db.execute(query)
    return result.fetchall()


# IS-02: LIKE injection
# VULNERABLE: q comes from GET /problems?q=... (public endpoint, no auth required)
async def search_problems(
    db: AsyncSession,
    q: str,          # user-supplied search query, unvalidated
    max_len: int = 100,
) -> list:
    """Search problems by title.

    BUG (IS-02 — ASVS V1.2.4 violation):
      q is interpolated into a raw SQL string via f-string.
      An attacker can supply: q="' UNION SELECT username,password,null FROM users--"
      to extract the users table.
    """
    # VULNERABLE: raw SQL with f-string containing user input
    result = await db.execute(
        f"SELECT * FROM problems WHERE title LIKE '%{q}%'"
    )
    return result.fetchall()
