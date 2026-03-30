"""
Seed script: Insert 10 classic algorithm problems into the database.
Run from /app inside the container:
    PYTHONPATH=/app python seed_problems.py
"""
import asyncio
import hashlib
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.problem import Problem
from app.models.test_case import TestCase
from app.models.user import User
from app.models.enums import Difficulty, Visibility, Role
from app.services.auth_service import hash_password


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


PROBLEMS = [
    {
        "title": "Two Sum",
        "difficulty": Difficulty.EASY,
        "tags": ["array", "hash-table"],
        "description": """\
## Problem

Given an array of integers `nums` and an integer `target`, return **indices** of the two numbers such that they add up to `target`.

You may assume that each input would have **exactly one solution**, and you may not use the same element twice.

## Input Format

- Line 1: `N` — number of integers
- Line 2: `N` space-separated integers
- Line 3: `target` integer

## Output Format

Two space-separated indices (0-based), smaller index first.

## Example

**Input:**
```
4
2 7 11 15
9
```
**Output:**
```
0 1
```

## Constraints

- `2 ≤ N ≤ 10^4`
- `-10^9 ≤ nums[i] ≤ 10^9`
- Exactly one valid answer exists.
""",
        "time_limit": 1000,
        "memory_limit": 256,
    },
    {
        "title": "Reverse a String",
        "difficulty": Difficulty.EASY,
        "tags": ["string", "two-pointers"],
        "description": """\
## Problem

Given a string `s`, reverse it and print the result.

## Input Format

A single line containing the string `s`.

## Output Format

The reversed string.

## Example

**Input:** `hello`
**Output:** `olleh`

## Constraints

- `1 ≤ |s| ≤ 10^5`
- `s` contains only printable ASCII characters.
""",
        "time_limit": 1000,
        "memory_limit": 128,
    },
    {
        "title": "Fibonacci Number",
        "difficulty": Difficulty.EASY,
        "tags": ["recursion", "dynamic-programming", "math"],
        "description": """\
## Problem

Given `n`, compute the `n`-th Fibonacci number.

`F(0) = 0`, `F(1) = 1`, `F(n) = F(n-1) + F(n-2)` for `n > 1`.

## Input Format

A single integer `n`.

## Output Format

A single integer — `F(n)`.

## Example

**Input:** `6`
**Output:** `8`

## Constraints

- `0 ≤ n ≤ 40`
""",
        "time_limit": 1000,
        "memory_limit": 128,
    },
    {
        "title": "Valid Parentheses",
        "difficulty": Difficulty.EASY,
        "tags": ["string", "stack"],
        "description": """\
## Problem

Given a string containing only `(`, `)`, `{`, `}`, `[`, `]`, determine if the input string is **valid**.

A string is valid if:
1. Open brackets must be closed by the same type of bracket.
2. Open brackets must be closed in the correct order.

## Input Format

A single line containing the brackets string.

## Output Format

`YES` if valid, `NO` otherwise.

## Example

**Input:** `()[]{}`
**Output:** `YES`

**Input:** `(]`
**Output:** `NO`

## Constraints

- `1 ≤ |s| ≤ 10^4`
""",
        "time_limit": 1000,
        "memory_limit": 128,
    },
    {
        "title": "Maximum Subarray",
        "difficulty": Difficulty.MEDIUM,
        "tags": ["array", "dynamic-programming", "divide-and-conquer"],
        "description": """\
## Problem

Given an integer array `nums`, find the **contiguous subarray** (containing at least one number) which has the largest sum and return its sum.

## Input Format

- Line 1: `N`
- Line 2: `N` space-separated integers

## Output Format

A single integer — the maximum subarray sum.

## Example

**Input:**
```
9
-2 1 -3 4 -1 2 1 -5 4
```
**Output:** `6`

*(The subarray [4,-1,2,1] has the largest sum = 6.)*

## Constraints

- `1 ≤ N ≤ 10^5`
- `-10^4 ≤ nums[i] ≤ 10^4`
""",
        "time_limit": 1000,
        "memory_limit": 256,
    },
    {
        "title": "Binary Search",
        "difficulty": Difficulty.EASY,
        "tags": ["array", "binary-search"],
        "description": """\
## Problem

Given a **sorted** array of integers `nums` and a `target`, return the index of `target` using binary search. If not found, return `-1`.

## Input Format

- Line 1: `N`
- Line 2: `N` space-separated integers (sorted ascending)
- Line 3: `target`

## Output Format

The 0-based index of the target, or `-1`.

## Example

**Input:**
```
6
-1 0 3 5 9 12
9
```
**Output:** `4`

## Constraints

- `1 ≤ N ≤ 10^4`
- All values are distinct.
""",
        "time_limit": 1000,
        "memory_limit": 128,
    },
    {
        "title": "Merge Two Sorted Lists",
        "difficulty": Difficulty.EASY,
        "tags": ["linked-list", "recursion"],
        "description": """\
## Problem

Given two sorted arrays, merge them into a single sorted array.

## Input Format

- Line 1: `N M`
- Line 2: `N` space-separated integers (sorted)
- Line 3: `M` space-separated integers (sorted)

## Output Format

A single line of `N+M` sorted integers.

## Example

**Input:**
```
3 4
1 2 4
1 3 4 5
```
**Output:** `1 1 2 3 4 4 5`

## Constraints

- `0 ≤ N, M ≤ 10^4`
- `-10^5 ≤ values ≤ 10^5`
""",
        "time_limit": 1000,
        "memory_limit": 256,
    },
    {
        "title": "Longest Common Subsequence",
        "difficulty": Difficulty.MEDIUM,
        "tags": ["string", "dynamic-programming"],
        "description": """\
## Problem

Given two strings `text1` and `text2`, return the **length** of their longest common subsequence. If there is no common subsequence, return `0`.

## Input Format

- Line 1: `text1`
- Line 2: `text2`

## Output Format

A single integer — the LCS length.

## Example

**Input:**
```
abcde
ace
```
**Output:** `3`

*(The LCS is "ace".)*

## Constraints

- `1 ≤ |text1|, |text2| ≤ 1000`
- Both strings consist of only lowercase English letters.
""",
        "time_limit": 2000,
        "memory_limit": 256,
    },
    {
        "title": "Number of Islands",
        "difficulty": Difficulty.MEDIUM,
        "tags": ["graph", "BFS", "DFS", "matrix"],
        "description": """\
## Problem

Given an `R x C` binary grid where `1` = land and `0` = water, count the number of **islands**.

An island is surrounded by water and formed by connecting adjacent land cells horizontally or vertically.

## Input Format

- Line 1: `R C`
- Next `R` lines: `C` space-separated values (`0` or `1`)

## Output Format

A single integer — number of islands.

## Example

**Input:**
```
4 5
1 1 1 1 0
1 1 0 1 0
1 1 0 0 0
0 0 0 0 0
```
**Output:** `1`

## Constraints

- `1 ≤ R, C ≤ 300`
""",
        "time_limit": 2000,
        "memory_limit": 256,
    },
    {
        "title": "Trapping Rain Water",
        "difficulty": Difficulty.HARD,
        "tags": ["array", "two-pointers", "stack", "dynamic-programming"],
        "description": """\
## Problem

Given `N` non-negative integers representing an elevation map where each bar has width `1`, compute how much water can be trapped after raining.

## Input Format

- Line 1: `N`
- Line 2: `N` space-separated non-negative integers

## Output Format

A single integer — total trapped water units.

## Example

**Input:**
```
12
0 1 0 2 1 0 1 3 2 1 2 1
```
**Output:** `6`

## Constraints

- `1 ≤ N ≤ 3 × 10^4`
- `0 ≤ height[i] ≤ 10^5`
""",
        "time_limit": 1000,
        "memory_limit": 256,
    },
]

# Test cases: keyed by problem slug → list of (input, expected_output)
# input_file / output_file store raw text content inline (no S3 needed in dev)
TEST_CASES: dict[str, list[tuple[str, str]]] = {
    "two-sum": [
        ("4\n2 7 11 15\n9\n", "0 1\n"),
        ("3\n1 2 3\n4\n", "0 2\n"),
        ("2\n3 5\n8\n", "0 1\n"),
    ],
    "reverse-a-string": [
        ("hello\n", "olleh\n"),
        ("abcde\n", "edcba\n"),
        ("a\n", "a\n"),
    ],
    "fibonacci-number": [
        ("0\n", "0\n"),
        ("1\n", "1\n"),
        ("6\n", "8\n"),
        ("10\n", "55\n"),
    ],
    "valid-parentheses": [
        ("()[]{}\n", "YES\n"),
        ("(]\n", "NO\n"),
        ("{[()]}\n", "YES\n"),
    ],
    "maximum-subarray": [
        ("9\n-2 1 -3 4 -1 2 1 -5 4\n", "6\n"),
        ("1\n1\n", "1\n"),
        ("5\n-1 -2 -3 -4 -5\n", "-1\n"),
    ],
    "binary-search": [
        ("6\n-1 0 3 5 9 12\n9\n", "4\n"),
        ("6\n-1 0 3 5 9 12\n2\n", "-1\n"),
        ("1\n5\n5\n", "0\n"),
    ],
    "merge-two-sorted-lists": [
        ("3 4\n1 2 4\n1 3 4 5\n", "1 1 2 3 4 4 5\n"),
        ("2 2\n1 3\n2 4\n", "1 2 3 4\n"),
    ],
    "longest-common-subsequence": [
        ("abcde\nace\n", "3\n"),
        ("abc\nabc\n", "3\n"),
        ("abc\ndef\n", "0\n"),
    ],
    "number-of-islands": [
        ("4 5\n1 1 1 1 0\n1 1 0 1 0\n1 1 0 0 0\n0 0 0 0 0\n", "1\n"),
        ("4 5\n1 1 0 0 0\n1 1 0 0 0\n0 0 1 0 0\n0 0 0 1 1\n", "3\n"),
    ],
    "trapping-rain-water": [
        ("12\n0 1 0 2 1 0 1 3 2 1 2 1\n", "6\n"),
        ("4\n4 2 0 3\n", "3\n"),
    ],
}


async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        problems_inserted = 0
        problems_skipped = 0
        tcs_inserted = 0

        for p in PROBLEMS:
            slug = slugify(p["title"])

            # Idempotent: skip problem if already exists
            existing = await session.execute(
                select(Problem).where(Problem.slug == slug)
            )
            problem = existing.scalar_one_or_none()

            if not problem:
                problem = Problem(
                    title=p["title"],
                    slug=slug,
                    description=p["description"],
                    difficulty=p["difficulty"],
                    time_limit=p["time_limit"],
                    memory_limit=p["memory_limit"],
                    tags=p["tags"],
                    visibility=Visibility.PUBLIC,
                )
                session.add(problem)
                await session.flush()  # get problem.id
                problems_inserted += 1
                print(f"  + {p['title']} [{p['difficulty'].value if hasattr(p['difficulty'], 'value') else p['difficulty']}]")
            else:
                problems_skipped += 1

            # Seed test cases for this problem (idempotent: only if none exist)
            tc_count_result = await session.execute(
                select(TestCase).where(TestCase.problem_id == problem.id)
            )
            existing_tcs = tc_count_result.scalars().all()
            if existing_tcs:
                continue  # already has test cases

            for i, (input_data, output_data) in enumerate(TEST_CASES.get(slug, [])):
                tc = TestCase(
                    problem_id=problem.id,
                    input_file=input_data,    # raw content (inline, no S3)
                    output_file=output_data,  # raw content (inline, no S3)
                    input_checksum=sha256(input_data),
                    output_checksum=sha256(output_data),
                    is_hidden=(i > 0),        # first TC visible, rest hidden
                    order_index=i,
                )
                session.add(tc)
                tcs_inserted += 1

        await session.commit()

        if problems_inserted:
            print(f"\n✅ Seeded {problems_inserted} problems and {tcs_inserted} test cases.")
        else:
            print(f"\n⏭️  Problems already exist ({problems_skipped} skipped). Seeded {tcs_inserted} new test cases.")

        # ── Seed default admin account ──────────────────────────────────────
        ADMIN_EMAIL    = "admin@codingwar.dev"
        ADMIN_USERNAME = "admin"
        ADMIN_PASSWORD = "Admin@123"

        existing_admin = (await session.execute(
            select(User).where(User.username == ADMIN_USERNAME)
        )).scalar_one_or_none()

        if existing_admin:
            if existing_admin.email != ADMIN_EMAIL:
                existing_admin.email = ADMIN_EMAIL
                await session.commit()
                print(f"\n🔄 Admin email updated → {ADMIN_EMAIL}")
            else:
                print(f"\n⏭️  Admin user already exists, skipping.")
        else:
            admin = User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password_hash=hash_password(ADMIN_PASSWORD),
                role=Role.ADMIN,
                is_email_verified=True,
            )
            session.add(admin)
            await session.commit()
            print(f"\n👤 Admin created → email: {ADMIN_EMAIL} | password: {ADMIN_PASSWORD}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())


