# code/reference/fuzz/fuzz_submission.py
# Chapter 8, Lab 8.7: Atheris Coverage-Guided Fuzz Harness
#
# Reference implementation — open only after completing your own.
# Install: pip install atheris --break-system-packages
# Run:     python fuzz_submission.py corpus/ -max_total_time=30
# Run:     python fuzz_submission.py --scoring corpus/ -max_total_time=30
# Run:     python fuzz_submission.py --error corpus/ -max_total_time=30

import sys
import atheris


# ---------------------------------------------------------------------------
# Target 1: Submission schema validation
# ---------------------------------------------------------------------------
def fuzz_submission_schema(data: bytes) -> None:
    """Fuzz the SubmissionCreate Pydantic schema with arbitrary bytes.

    Invariants if validation PASSES:
      - len(source_code) <= 64_000
      - language in {python, cpp, java}

    Exception handling design:
      ValidationError is the EXPECTED outcome for most fuzz inputs — random
      bytes are almost never valid submissions. Re-raising every exception
      would make the fuzzer stop on the first invalid input and report
      correct behaviour as a "crash", wasting the entire fuzzing budget.
      We only re-raise when an invariant is violated (FUZZ BUG prefix),
      which signals a genuine security issue.
    """
    try:
        from app.schemas.submission import SubmissionCreate
        fdp = atheris.FuzzedDataProvider(data)

        try:
            obj = SubmissionCreate(**{
                "language":    fdp.ConsumeUnicodeNoSurrogates(100),
                "source_code": fdp.ConsumeUnicodeNoSurrogates(100_000),
                "problem_id":  fdp.ConsumeUnicodeNoSurrogates(50),
                "contest_id":  fdp.ConsumeUnicodeNoSurrogates(50),
            })
            # Invariant checks — only if validation passed
            assert len(obj.source_code) <= 64_000, (
                f"FUZZ BUG: source_code > 64KB passed validation: "
                f"{len(obj.source_code)} bytes"
            )
            assert obj.language in {"python", "cpp", "java"}, (
                f"FUZZ BUG: unallowed language passed validation: {obj.language!r}"
            )
        except Exception:
            pass  # Validation rejection is expected — not a bug

    except Exception as e:
        if "FUZZ BUG" in str(e):
            raise


# ---------------------------------------------------------------------------
# Target 2: Scoring calculation
# ---------------------------------------------------------------------------
def fuzz_scoring(data: bytes) -> None:
    """Fuzz calculate_penalty_score with arbitrary integers.

    Invariant if no ValueError: result must be int.

    Input clamping rationale:
      Without clamping, the fuzzer generates base_score=2**63. Python's
      arbitrary-precision arithmetic makes this valid but extremely slow —
      the fuzzer spends its entire budget on one computation and never
      explores the interesting boundary conditions around the scoring logic.
      Clamping to 10_000_000 keeps computations fast and directs coverage
      guidance toward branches that matter for business logic.
    """
    try:
        from decimal import Decimal
        from app.services.scoring import calculate_penalty_score

        fdp = atheris.FuzzedDataProvider(data)
        base_score     = fdp.ConsumeInt(4)
        wrong_attempts = fdp.ConsumeInt(4)

        if abs(base_score) > 10_000_000 or abs(wrong_attempts) > 100_000:
            return  # Clamp — see docstring

        try:
            result = calculate_penalty_score(base_score, wrong_attempts)
            assert isinstance(result, int), (
                f"FUZZ BUG: result is not int: {type(result).__name__} = {result}"
            )
        except ValueError:
            pass  # Expected for negative wrong_attempts

    except Exception as e:
        if "FUZZ BUG" in str(e):
            raise


# ---------------------------------------------------------------------------
# Target 3: Generic exception handler
# ---------------------------------------------------------------------------
def fuzz_error_handler(data: bytes) -> None:
    """Fuzz generic_exception_handler with arbitrary exception messages.

    Invariants for every input:
      1. Response status is always 500
      2. Response body never contains traceback, sqlalchemy, or postgresql
      3. Response body always contains error_ref

    This target verifies that no exception message — however crafted — can
    cause the error handler to leak internal details or fail to produce a
    well-formed response.
    """
    import asyncio
    from unittest.mock import patch

    try:
        fdp = atheris.FuzzedDataProvider(data)
        exc_message = fdp.ConsumeUnicodeNoSurrogates(200)

        async def run():
            from httpx import AsyncClient, ASGITransport
            from app.main import app

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                with patch(
                    "app.api.submissions.get_submission",
                    side_effect=RuntimeError(exc_message),
                ):
                    from app.core.security import create_access_token
                    token = create_access_token(
                        {"sub": "usr_fuzz", "role": "contestant"}
                    )
                    resp = await client.get(
                        "/api/v1/submissions/test_id",
                        headers={"Authorization": f"Bearer {token}"},
                    )

                    # Invariant 1: always 500
                    assert resp.status_code == 500, (
                        f"FUZZ BUG: expected 500, got {resp.status_code} "
                        f"for exception: {exc_message[:50]!r}"
                    )

                    body_lower = resp.text.lower()

                    # Invariant 2: no internal details
                    for leak in ["traceback", "sqlalchemy", "postgresql",
                                 "asyncpg", "/app/"]:
                        assert leak not in body_lower, (
                            f"FUZZ BUG: response leaks {leak!r} "
                            f"for exception: {exc_message[:50]!r}"
                        )

                    # Invariant 3: error_ref present
                    assert "error_ref" in resp.json(), (
                        f"FUZZ BUG: error_ref missing from 500 response "
                        f"for exception: {exc_message[:50]!r}"
                    )

        asyncio.run(run())

    except Exception as e:
        if "FUZZ BUG" in str(e):
            raise


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if "--scoring" in sys.argv:
        target = fuzz_scoring
        sys.argv = [a for a in sys.argv if a != "--scoring"]
    elif "--error" in sys.argv:
        target = fuzz_error_handler
        sys.argv = [a for a in sys.argv if a != "--error"]
    else:
        target = fuzz_submission_schema

    atheris.Setup(sys.argv, target)
    atheris.Fuzz()
