# Solution 8.1 — Design-Driven Test Planning

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. The approach shown here is one valid path.

---

## Key Insights

### The Coverage Matrix row — what makes it strong

A weak row says "unit test for TH-02." A strong row says "TC-IDOR-001 and TC-IDOR-002 in `tests/security/test_authorization.py`; runs in PR gate via `pytest -m idor`; ZAP active scan also probes `GET /submissions/{id}` on weeknights with a forged JWT; Coverage Matrix updated 2025-03-15." The difference is traceability: can you point to the actual artifact that proves the risk is covered?

### Hygiene vs Deep — the real principle

The distinction is not about importance — it is about feedback speed versus depth. A CRITICAL SQL injection found by Semgrep in 30 seconds on a PR is worth more than the same finding from ZAP three days after merge. But ZAP finds runtime issues (authentication state across requests, session cookie behaviour) that Semgrep cannot see. Both are necessary; neither is sufficient alone.

### 4-Questions — what each question prevents

Q1 (what are we testing) prevents scope creep — if payment processing is N/A, ZAP should not probe payment endpoints and generate noise. Q3 (what do we do about it) ensures every Code Contract from Ch.7 has a corresponding test — if CI-03 (admin MFA) has no test, it is assumed but not verified. Q4 (did we do a good job) forces you to define what evidence looks like before you produce it.

### Discussion answers

**Q1 — Unit test for sandbox isolation:** A unit test can verify that `JudgeService.run_code()` calls `sandbox_runner.execute()` and never calls `subprocess.run()` directly. It can mock the sandbox and assert it receives the correct arguments. What it cannot verify is whether the sandbox itself actually contains the execution. Sandbox isolation is a runtime property — it requires integration testing against a real gVisor instance, or a pentest that attempts actual escape.

**Q2 — What triggers a Coverage Matrix update:** New threats added to the risk register; a finding in any lab that reveals an uncovered threat; a Code Contract modified in Ch.7 that changes what controls exist; a test deprecated or removed from CI; a component added to the architecture that was not in the original threat model.

**Q3 — DAST finding despite passing unit test:** The unit test verified that the code *contains* the correct control. The DAST finding reveals that the control is not effective at runtime — possibly because of a misconfiguration, a middleware that bypasses the check, or a route that was added without the control being applied. Unit tests and DAST test different layers. Both passing is the goal; one passing does not imply the other passes.

---

*Back to the lab: [labs/lab-8.1.md](../labs/lab-8.1.md)*
