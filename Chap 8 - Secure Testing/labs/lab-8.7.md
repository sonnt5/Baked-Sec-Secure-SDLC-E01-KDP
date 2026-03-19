# Lab 8.7 — Fuzzing: Hypothesis + Atheris

> **Chapter 8 · Security Testing Strategy and Toolchain Integration**
> Input: CODING WAR submission validator + score calculator
> Output: Property-Based Tests + Fuzz Harness + Crash Report

## Learning Objectives

- Write property-based tests that encode security invariants — not correctness examples.
- Build a coverage-guided fuzz harness from scratch and interpret its output.
- Understand why property-based testing finds a class of bug that example-based testing cannot.
- Manage a fuzz corpus and reason about what coverage means in a security context.

## Code Files

| File | Role |
|------|------|
| `code/reference/fuzz/test_hypothesis.py` | Reference property tests — consult after finishing your own |
| `code/reference/fuzz/fuzz_submission.py` | Reference fuzz harness — consult after finishing your own |

> There is no starter code. You create your own files from scratch.

---

## Background

An example-based test checks one specific input. A property-based test checks an invariant that must hold across *all* inputs in a domain — Hypothesis generates hundreds of inputs automatically and shrinks any failing case to the minimal reproducer.

The critical difference for security: adversarial inputs are often the ones a developer would never think to write as an example. A property test forces you to state what must *never* happen, which is exactly the right question for security.

Before writing any property test, ask: what catastrophic thing must this function never do, regardless of input? If the answer is "it should return the right value," that is a correctness property. If the answer is "it must never expose internal details" or "it must never increase a score under any arithmetic path," that is a security property.

---

## Task 1 — Property-Based Tests with Hypothesis

Read the scoring and login code in CODING WAR. Identify the security properties that must hold regardless of input — properties whose violation would constitute an exploitable bug, not just a correctness failure.

Write property-based tests that encode those properties. Each test must state the security invariant in the docstring: not what the test does, but what security guarantee it verifies and why violation of that guarantee would be exploitable.

```bash
pip install hypothesis --break-system-packages
pytest your-test-file.py -v --hypothesis-show-statistics
```

One of your properties must cover information leakage from error responses. Consider: what is the complete set of patterns that would indicate an internal detail has leaked? A list of three patterns is not sufficient for CODING WAR — think about every layer of the stack.

Write at least five distinct security properties. One of them must be entirely your own design — not derived from this document.

---

## Task 2 — Atheris Fuzz Harness

Build a fuzz harness for the CODING WAR submission pipeline using Atheris.

```bash
pip install atheris --break-system-packages
mkdir -p corpus/
python your-harness.py corpus/ -max_total_time=30
```

Your harness must cover at least two distinct targets within the submission pipeline. For each target, decide: what are the invariants that must hold if the target function behaves safely? An invariant that only checks for crashes is not a security invariant.

Address in the code:
- Why you catch all validation exceptions and only re-raise on a specific marker string — what would happen to the fuzzer run if you re-raised every exception?
- Why input values need to be bounded before fuzzing arithmetic functions — what happens to a coverage-guided fuzzer when it spends cycles on numerically extreme inputs that all follow the same code path?

Write an entry point that allows selecting between targets via command-line flags.

---

## Task 3 — Crash Analysis

If the fuzzer finds a crash, document it in full: the crash ID, the target, the reproducing input (as bytes or a reproduce command), the exception, the root cause, the security impact (is this exploitable, a data leak, or a DoS?), the fix, and how you would add this crash as a regression test in Lab 8.2.

If no crash is found in the time budget: this is useful information too. Document what code paths were exercised, estimate how much additional time would be needed for meaningful coverage of the unexplored branches, and identify 3 seed inputs that would push the fuzzer into branches it has not yet reached.

---

## Task 4 — Corpus and CI Strategy

Answer these questions — not generically, but with specific reference to CODING WAR:

1. What 5 seed inputs would you provide for the submission schema target, and why does each one help the fuzzer explore branches that random bytes would reach only slowly?

2. Coverage-guided fuzzing tracks which branches are newly reached by each input. Why does this matter specifically for testing input validation code with many conditional paths, compared to random mutation?

3. In CI: where should fuzz crash inputs be stored and retained? What criterion determines whether a crash blocks a release versus goes into a bug backlog? How does the severity of the crash (DoS vs data leak vs RCE) affect that decision?

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Property-based tests | **35** | Each test states a security invariant (not a correctness property); information leakage test covers the full CODING WAR stack; at least one property is original |
| Fuzz harness | **35** | Two targets with security invariants; exception handling and input bounding explained in code; entry point with flag selection works |
| Crash analysis | **15** | Full template completed if crash found; coverage analysis is substantive if not |
| Corpus and CI strategy | **15** | Seeds are justified against specific code paths; CI retention criteria distinguish severity levels |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-8.7.md](../solutions/sol-8.7.md) after completing the lab.*
