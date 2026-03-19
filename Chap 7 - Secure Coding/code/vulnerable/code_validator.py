# app/validators/code_validator.py — VULNERABLE version
# Lab 7.3: ReDoS — Regular Expression Denial of Service (IS-05)
# DO NOT USE IN PRODUCTION — educational purposes only
#
# Bugs demonstrated:
#   IS-05a: check_output_format() — no timeout on user-supplied regex patterns.
#           A crafted contestant_output can hang a judge worker indefinitely.
#
#   IS-05b: validate_verdict_format() — nested quantifiers in a pattern matched
#           against the verdict string returned by the sandbox process.
#           A crafted verdict string causes catastrophic backtracking.

import re


def check_output_format(pattern: str, contestant_output: str) -> bool:
    """Check whether contestant output matches the expected format.

    BUG (IS-05a — ASVS V1.2.9 violation):
      pattern comes from the problem database — admin-authored, but not
      guaranteed to be safe. contestant_output is entirely attacker-controlled.

      Attack: submit output = "a" * 30 + "X" against pattern r"(a+)+"
      The engine explores 2^30 (> 1 billion) paths before determining no match.
      A single request can hang a judge worker for minutes.

      No timeout is applied — the regex runs until completion or process kill.
    """
    # VULNERABLE: no timeout; pattern may contain nested quantifiers
    return bool(re.match(pattern, contestant_output))


def validate_verdict_format(verdict: str) -> bool:
    """Check that a verdict string from the sandbox is one of the valid values.

    BUG (IS-05b — ASVS V1.2.9 violation):
      The pattern uses nested quantifiers: ([A-Z_]+)* matched against verdict,
      which comes from sandbox process output — potentially attacker-influenced.

      Attack: verdict = "A" * 40 + "!"
      The engine explores 2^40 paths before the final mismatch on "!",
      hanging the calling thread for seconds to minutes.

    Valid verdicts: ACCEPTED, WRONG_ANSWER, TIME_LIMIT_EXCEEDED,
                   MEMORY_LIMIT_EXCEEDED, RUNTIME_ERROR, COMPILATION_ERROR
    """
    # VULNERABLE: nested quantifiers — exponential backtracking on crafted input
    pattern = r"^([A-Z_]+)*$"
    return bool(re.match(pattern, verdict))
