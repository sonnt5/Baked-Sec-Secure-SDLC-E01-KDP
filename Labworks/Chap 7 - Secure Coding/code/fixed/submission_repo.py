# app/repositories/submission_repo.py — FIXED version
# Lab 7.3: SQL Injection Prevention (ASVS V1.2.4)
#
# IS-01: ORDER BY injection — column names cannot be parameterized directly.
#         Fix: allowlist of SQLAlchemy column objects (never raw strings).
# IS-02: LIKE search — can use ORM parameterization (ilike generates a
#         parameterized LIKE query internally).

from typing import Literal

from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

# Assume these are imported from app.models
# from app.models import Submission, Problem


# IS-01 Fix: allowlist approach for dynamic column names
# ASVS V1.2.4 note: "Query parts such as table and column names cannot be
# escaped — using escaped user-supplied data results in failed queries or
# SQL injection." → Use a mapping to safe SQLAlchemy column objects instead.
#
# ALLOWED_SORT_FIELDS maps user-supplied strings to SQLAlchemy column objects.
# The user string is NEVER placed in the SQL — only the mapped column object is.
ALLOWED_SORT_FIELDS: dict = {
    "score":        None,  # replace None with Submission.score
    "time":         None,  # replace None with Submission.execution_time_ms
    "penalty":      None,  # replace None with Submission.penalty_score
    "submitted_at": None,  # replace None with Submission.submitted_at
    # Only these four fields — not any user-supplied SQL fragment
}

SortOrder = Literal["asc", "desc"]


async def get_submissions_by_contest(
    db: AsyncSession,
    contest_id: str,
    sort_by: str = "score",
    order: SortOrder = "desc",
) -> list:
    """Fetch contest submissions with user-controlled sorting.

    The sort_by value is validated against ALLOWED_SORT_FIELDS before any
    SQL is generated. The column object — not the user string — is passed
    to SQLAlchemy's order_by(). The WHERE clause uses a parameterized bind.
    ASVS V1.2.4 compliant.
    """
    # Step 1: validate against allowlist — reject anything not in the map
    sort_column = ALLOWED_SORT_FIELDS.get(sort_by)
    if sort_column is None:
        # Raise ValueError — the API layer converts this to HTTP 422
        raise ValueError(f"Invalid sort field: {sort_by!r}")

    # Step 2: map order string to SQLAlchemy function
    sort_func = asc if order == "asc" else desc

    # Step 3: build fully parameterized query
    # contest_id → parameterized bind variable (never string-concatenated)
    # sort_column → SQLAlchemy column object (never a raw string in SQL)
    from app.models import Submission  # local import for example clarity
    stmt = (
        select(Submission)
        .where(Submission.contest_id == contest_id)   # parameterized
        .order_by(sort_func(sort_column))             # mapped column object
    )
    result = await db.execute(stmt)
    return result.scalars().all()


# IS-02 Fix: LIKE search using SQLAlchemy ilike()
# ilike() generates a parameterized LIKE query — q is a bind variable,
# never concatenated into the SQL string.
async def search_problems(
    db: AsyncSession,
    q: str,
    max_len: int = 100,
) -> list:
    """Full-text search problems by title.

    q is passed as a parameterized bind variable by SQLAlchemy.
    The % wildcards are part of the ORM pattern, not user input.
    ASVS V1.2.4 compliant.
    """
    from app.models import Problem
    q = q[:max_len]  # defensive length cap before DB call
    stmt = select(Problem).where(Problem.title.ilike(f"%{q}%"))
    # ilike() passes q as: WHERE title ILIKE $1 with $1 = '%user_input%'
    # The user's q value is never concatenated into the SQL string.
    result = await db.execute(stmt)
    return result.scalars().all()
