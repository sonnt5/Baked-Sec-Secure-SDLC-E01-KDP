# app/repositories/submission_repo.py — FIXED version
# Lab 7.3: SQL Injection Prevention (ASVS V1.2.4)
#
# IS-01: ORDER BY injection — column names cannot be parameterized.
#         Fix: allowlist dict mapping user strings → SQLAlchemy column objects.
#         The user string is validated; only the mapped column object enters SQL.
#
# IS-02: LIKE search injection — f-string concatenation into raw SQL.
#         Fix: SQLAlchemy ilike() passes q as a bind variable automatically.

from typing import Literal

from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
# IS-01 Fix: ALLOWED_SORT_FIELDS allowlist
# ---------------------------------------------------------------------------
# ASVS V1.2.4 note: "Query parts such as table and column names cannot be
# escaped — using escaped user-supplied data results in failed queries or
# SQL injection."
#
# The correct solution is an allowlist: validate the user-supplied string,
# then use the corresponding SQLAlchemy column *object* — never the string
# itself — in the ORDER BY clause.
#
# Replace the placeholder strings below with actual model column references:
#   from app.models import Submission
#   ALLOWED_SORT_FIELDS = {
#       "score":        Submission.score,
#       "time":         Submission.execution_time_ms,
#       "penalty":      Submission.penalty_score,
#       "submitted_at": Submission.submitted_at,
#   }
ALLOWED_SORT_FIELDS: dict = {
    "score":        "Submission.score",           # replace with column object
    "time":         "Submission.execution_time_ms",
    "penalty":      "Submission.penalty_score",
    "submitted_at": "Submission.submitted_at",
}

SortOrder = Literal["asc", "desc"]


async def get_submissions_by_contest(
    db: AsyncSession,
    contest_id: str,
    sort_by: str = "score",
    order: SortOrder = "desc",
) -> list:
    """Fetch contest submissions with user-controlled sorting.

    sort_by is validated against ALLOWED_SORT_FIELDS before any SQL is
    generated. The mapped column object — not the user string — is passed
    to SQLAlchemy. The WHERE clause uses a parameterized bind variable.

    Raises ValueError for unknown sort_by values (API layer returns 422).
    ASVS V1.2.4 compliant.
    """
    # Step 1: validate against allowlist — reject unknown sort fields
    if sort_by not in ALLOWED_SORT_FIELDS:
        raise ValueError(
            f"Invalid sort field: {sort_by!r}. "
            f"Allowed: {list(ALLOWED_SORT_FIELDS)}"
        )
    sort_column = ALLOWED_SORT_FIELDS[sort_by]   # SQLAlchemy column object

    # Step 2: map order string to SQLAlchemy sort function
    sort_func = asc if order == "asc" else desc

    # Step 3: fully parameterized query
    #   contest_id  → bind variable (parameterized, never string-concatenated)
    #   sort_column → SQLAlchemy column object (never a raw string in SQL)
    from app.models import Submission  # noqa: PLC0415 — local import for clarity
    stmt = (
        select(Submission)
        .where(Submission.contest_id == contest_id)   # parameterized bind
        .order_by(sort_func(sort_column))              # column object, not string
    )
    result = await db.execute(stmt)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# IS-02 Fix: LIKE search with ORM parameterization
# ---------------------------------------------------------------------------
async def search_problems(
    db: AsyncSession,
    q: str,
    max_len: int = 100,
) -> list:
    """Search problems by title.

    SQLAlchemy ilike() passes q as a bind variable — the database driver
    receives: WHERE title ILIKE $1 with $1 = '%<user_input>%'
    The user's input is never concatenated into the SQL string.

    The % wildcards are part of the ORM pattern string; q is a bind value.
    This is safe. Contrast with f"... LIKE '%{q}%'" in raw SQL, which
    is NOT safe because the driver receives a complete SQL string with q
    already embedded.
    ASVS V1.2.4 compliant.
    """
    from app.models import Problem  # noqa: PLC0415
    q = q[:max_len]   # defensive length cap before DB call
    stmt = select(Problem).where(Problem.title.ilike(f"%{q}%"))
    result = await db.execute(stmt)
    return result.scalars().all()
