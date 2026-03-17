# Lab 5.4 — Anti-Patterns & Secure Design Review Report

> **Chapter 5 · Mitigations, Security Patterns, and Cryptography**
> Input: Design + Pattern labs 5.2–5.3 | Output: Anti-Pattern Report + SDR Report

> [!NOTE]
> **Artifact for this lab:** Secure Design Review Report — includes: (1) Anti-Pattern Analysis (4 anti-patterns), (2) Design Quality Assessment, (3) Issues List by severity, (4) Verdict and Action Items. Format matches a real-world SDR gate artifact.

## Learning Objectives

- Identify 4 anti-patterns (Confused Deputy, Backflow of Trust, Third-Party Hooks, Unpatchable Components) in real-world designs.
- Understand why each anti-pattern is more dangerous than a regular bug — they create structural vulnerabilities.
- Write a Secure Design Review Report in the standard SDR gate format.

## Context

Anti-patterns are design decisions that seem reasonable in the short term but create structural vulnerabilities over time. Unlike bugs (fixable with a single commit), anti-patterns typically require architectural refactoring. Detecting them early — during the design phase — is the cheapest way to deal with them. This lab combines anti-pattern analysis with writing a Secure Design Review Report — the artifact for the SDR gate.

---

## Task 1 — Anti-Pattern Analysis: 4 Cases

### Case 1: Confused Deputy in JudgeService

**Current design:**

```python
# CODING WAR — JudgeService: current implementation
class JudgeService:
    async def judge(self, submission_id: int) -> JudgeResult:
        submission = await self.db.get(Submission, submission_id)
        # JudgeService has DB read-all privilege → fetches all test cases
        test_cases = await self.db.execute(
            select(TestCase).where(TestCase.problem_id == submission.problem_id)
        )
        results = []
        for tc in test_cases.scalars():
            # Contestant's code is executed with JudgeService's privileges
            result = await self.runner.run(submission.source_code, tc.input)
            # result.stdout = output of contestant code — untrusted
            results.append({'verdict': self._compare(result.stdout, tc.expected), ...})
        return self._aggregate_verdict(results)
```

| Analysis | Content |
|----------|---------|
| **Where is the Confused Deputy?** | \[JudgeService is a Deputy with high privilege: reads all test cases. The caller (contestant code) has low privilege but the contestant's code is executed with JudgeService's permissions\] |
| **Attack scenario** | \[Contestant writes code that does: `print(open('/judge/test_cases/1.txt').read())` → if the judge sandbox does not isolate the filesystem, the code can read test cases with the judge process's permissions\] |
| **Why is this more dangerous than a typical IDOR?** | \[Fill in: why this is a structural vulnerability, not just a missing check\] |
| **Proposed refactoring** | \[Fill in: how to ensure JudgeService is no longer a Confused Deputy — hint: network namespace isolation + filesystem sandbox + output comparison in an isolated evaluator\] |
| **Implementation in FastAPI/Python** | \[Fill in: code snippet or design description of the fixed architecture\] |

### Case 2: Backflow of Trust in Verdict Evaluation

**Problematic design:**

```python
# CODING WAR — evaluate_result() with Backflow of Trust
async def evaluate_result(code_output: str, expected_output: str) -> str:
    # PROBLEM: parsing contestant code's output to determine the verdict
    if 'VERDICT=AC' in code_output.upper():
        return 'AC'  # Contestant code claims to be AC!
    if 'JUDGE_OVERRIDE' in code_output:
        return code_output.split('JUDGE_OVERRIDE:')[1].strip()
    # Normal comparison (only reached if no magic strings)
    return 'AC' if code_output.strip() == expected_output.strip() else 'WA'
```

| Analysis | Content |
|----------|---------|
| **Where is the Backflow of Trust?** | \[Low-trust execution output (contestant code) influences a high-trust verdict decision. Contestant code is untrusted input but is parsed to determine a business outcome\] |
| **Why is it dangerous?** | \[Fill in: unlike Confused Deputy, Backflow is about data flow — untrusted data flows UP to influence a trusted decision\] |
| **Fixed design** | \[Fill in: verdict must be determined ONLY from: return code, execution time, memory usage, and exact output comparison — never parse output for "signals"\] |
| **Code fix (Python)** | \[Fill in: rewrite `evaluate_result()` without magic string parsing\] |

### Case 3: Third-Party Hooks in the Frontend Bundle

**Situation:** CODING WAR's frontend loads 3 third-party scripts directly from CDNs into the admin/contestant pages:

```html
<script src="https://cdn.syntax-highlighter.com/latest.min.js">  <!-- code editor -->
<script src="https://analytics.example.com/track.js">             <!-- usage tracking -->
<script src="https://cdn.chat-widget.com/widget.js">              <!-- support chat -->
```

| Analysis | Content |
|----------|---------|
| **What are the Third-Party Hook risks?** | \[Fill in: supply chain attack, malicious update, CDN hijack → code runs in admin/contestant's browser with full DOM access\] |
| **Worst-case scenario with the admin page** | \[Fill in: attacker compromises CDN → injects keylogger into syntax-highlighter.js → harvests admin credentials\] |
| **Mitigations for Third-Party JS** | \[Fill in: Subresource Integrity (SRI) hash, Content Security Policy (CSP), self-host critical scripts, pin versions\] |
| **Unpatchable Component risk (bonus)** | \[Fill in: if chat-widget is no longer maintained and has a CVE, it cannot be patched → Unpatchable Component anti-pattern\] |

### Case 4: Unpatchable Components in Judge Infrastructure

**Situation:** CODING WAR's judge infrastructure uses the Docker image `judge-python:2.7` — Python 2.7 reached EOL in 2020. The justification for keeping it: *"many contest problems were written for Python 2.7, we don't want to break backward compatibility."*

| Analysis | Content |
|----------|---------|
| **Unpatchable Component risk** | \[Fill in: Python 2.7 no longer receives security patches; CVEs will not be fixed → permanent vulnerability in judge infrastructure\] |
| **Why is "don't break backward compat" insufficient justification?** | \[Fill in: business requirement vs. security requirement — this needs to be escalated as a product decision, not a technical one\] |
| **Mitigation options** | \[Fill in: (1) migrate problems to Python 3, (2) run Python 2.7 in a super-isolated sandbox with extra controls, (3) sunset support with a deprecation timeline\] |
| **Link to Reluctance to Trust** | \[Fill in: third-party components (including language runtimes) should be treated as untrusted — extra isolation required regardless\] |

---

## Task 2 — Secure Design Review Report (SDR Report)

Synthesize the anti-pattern analysis and review of all design artifacts from Ch.3–5.3 into a Secure Design Review Report. This is the formal artifact for the SDR gate in the Secure SDLC.

| Section | Content |
|---------|---------|
| **System / Version** | CODING WAR v\[X.Y\] — SDR Report |
| **Review Date** | \[Fill in\] |
| **Reviewer(s)** | \[Names — ideally includes: developer, architect, security-minded person\] |
| **Design Artifacts Reviewed** | Architecture Diagram (Lab 3.2), DFD + Trust Boundaries (Lab 4.2), Mitigation Register (Lab 5.1), Architecture Hardening Report (Lab 5.2), Pattern Application Worksheet (Lab 5.3), Anti-Pattern Cases (Lab 5.4 Task 1) |
| **Executive Summary** | \[2–3 sentences: overall design quality, top risks, overall verdict — written concisely as a CTO-level email summary\] |
| **Design Quality Score** | Maintainability: \[ /10\] · Testability: \[ /10\] · Scalability: \[ /10\] · Security: \[ /10\] · Total: \_\_ /40 |
| **CRITICAL Issues** *(must fix before SDR approval)* | \[List issues with ID, short description, affected component, severity justification. Must include at minimum: Confused Deputy in JudgeService + IDOR in submissions\] |
| **HIGH Issues** *(should fix before release)* | \[List\] |
| **MEDIUM Issues** *(fix in next sprint)* | \[List\] |
| **LOW / Technical Debt** | \[List\] |
| **Strengths** | \[Good design decisions — not everything is bad\] |
| **SDR Verdict** | \[ \] APPROVED · \[ \] APPROVED WITH CONDITIONS · \[ \] REJECTED |
| **Approval Conditions** | \[If not APPROVED: list specific, verifiable requirements — not a wish-list\] |
| **Next Review Trigger** | \[Conditions that trigger the next SDR cycle — e.g., when adding an external API integration, when changing the auth mechanism\] |

> [!NOTE]
> The SDR Report is a living document — format may vary by team. The key requirements are: issues correctly classified by severity with evidence, and a verdict with justification. CODING WAR currently has multiple critical issues — the verdict should not be APPROVED without conditions.

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Anti-Pattern Analysis — 4 cases | **40** | Each case: correct threat vector (3 pts) + explanation of "why structural, not a bug" (3 pts) + practical refactoring proposal (4 pts) |
| SDR Report — Executive Summary + Issues | **30** | Summary is readable by non-technical stakeholders; issues correctly classified by severity with justification |
| SDR Report — Verdict + Conditions | **20** | Verdict is not APPROVED without conditions (CODING WAR currently has multiple critical issues); conditions are specific and verifiable |
| Overall Report quality | **10** | Professional tone, consistent terminology, no contradictions between issues and verdict |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-5.4.md](../solutions/sol-5.4.md)*
