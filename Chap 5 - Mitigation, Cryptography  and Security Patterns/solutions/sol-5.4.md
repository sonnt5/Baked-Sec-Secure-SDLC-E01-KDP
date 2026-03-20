# Solution 5.4 — Anti-Patterns & Secure Design Review Report

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — Anti-Pattern Analysis

### Case 1: Confused Deputy in JudgeService

| Analysis | Content |
|----------|---------|
| **Why more dangerous than IDOR?** | A typical IDOR is a missing authorization check — fixable with one `assert` statement. The Confused Deputy is structural: JudgeService is a high-privilege deputy (DB read-all + filesystem access) that executes low-privilege code (contestant submissions). The vulnerability exists regardless of any individual check — it is inherent in the architecture where untrusted code runs with the service's own OS-level permissions. |
| **Proposed refactoring** | Isolate the execution environment completely: (1) gVisor + seccomp restricts syscalls so even if contestant code runs, it cannot access the filesystem outside `/tmp`. (2) Network namespace isolation prevents exfiltration. (3) The comparison of output vs expected happens in a separate, privileged `VerdictEvaluator` that never receives raw contestant code — it only receives the sanitized stdout string after execution. |
| **Implementation sketch** | ```python # Fixed: JudgeRunner executes with minimal privilege # VerdictEvaluator operates on output strings only — never touches source code class VerdictEvaluator: def compare(self, actual_stdout: str, expected: str) -> str: # Never parses for magic strings — pure comparison return 'AC' if actual_stdout.strip() == expected.strip() else 'WA' ``` |

### Case 2: Backflow of Trust in Verdict Evaluation

| Analysis | Content |
|----------|---------|
| **Why dangerous?** | Unlike Confused Deputy (where a privileged service executes untrusted code), Backflow of Trust is a data flow problem: output from a zero-trust source (contestant code's stdout) flows upward to influence a business-critical decision (contest verdict). The current code treats `'VERDICT=AC'` in stdout as a signal — meaning any contestant can print that string and receive an AC verdict regardless of correctness. This is not a missing check; it is a fundamentally wrong decision boundary: who is allowed to make the verdict decision? |
| **Fixed design** | The verdict decision must be made exclusively by trusted components using trusted inputs: (1) exit code from the isolated runner process, (2) execution time (measured externally), (3) memory usage (measured externally), (4) exact byte-for-byte output comparison. The contestant's stdout is treated as untrusted output — compared but never parsed for semantic meaning. |
| **Code fix** | ```python async def evaluate_result(code_output: str, expected_output: str) -> str: # Only trusted comparison — no parsing, no magic strings # stdout is treated as opaque bytes for comparison purposes only return 'AC' if code_output.strip() == expected_output.strip() else 'WA' ``` |

### Case 3: Third-Party Hooks

**Mitigations for Third-Party JS:**
1. **Subresource Integrity (SRI):** `<script src="..." integrity="sha384-<hash>" crossorigin="anonymous">` — browser rejects the script if the file hash doesn't match.
2. **Content Security Policy:** `Content-Security-Policy: script-src 'self' 'sha384-<hash>'` — whitelist only specific scripts by hash.
3. **Self-host critical scripts:** syntax-highlighter.js should be vendored and served from `static.coding-war.io` — eliminates CDN dependency.
4. **Pin versions:** never use `/latest.min.js` — always pin to a specific version like `/v10.2.1/highlight.min.js`.

**Unpatchable Component risk:** chat-widget.js has no version pinning and no SRI. If the CDN is compromised or the vendor abandons the project, there is no mechanism to detect malicious changes (no hash check) and no ability to patch (no source access). This is the Unpatchable Component anti-pattern layered on top of Third-Party Hook risk.

### Case 4: Unpatchable Components

**Why "backward compatibility" is insufficient justification:** Backward compatibility is a product requirement, not a security requirement. The correct response is to escalate the conflict to a product decision: "Python 2.7 EOL means we accept permanent unpatched CVEs in our judge infrastructure. This is a product decision with security implications." Options include: (1) migration to Python 3 (preferred), (2) Python 2.7 in an extremely isolated sandbox with extra compensating controls explicitly acknowledged as risk acceptance, (3) a deprecation timeline with 6-month notice to problem setters. Silently keeping Python 2.7 because "we don't want to break things" is not documented risk acceptance — it is undocumented vulnerability accumulation.

---

## Task 2 — SDR Report (Reference Verdict)

| Section | Reference Answer |
|---------|----------------|
| **Executive Summary** | CODING WAR's design demonstrates solid foundational architecture (event-driven judging, modular separation) but contains two critical structural vulnerabilities — a Confused Deputy in JudgeService and an IDOR on the submission endpoint — that must be remediated before the system handles real contest data. The crypto implementation contains 6 identified mistakes that require immediate fixes. Verdict: APPROVED WITH CONDITIONS. |
| **CRITICAL Issues** | CI-01: Confused Deputy in JudgeService — contestant code executes with judge process privileges; sandbox escape possible. CI-02: IDOR on GET /submissions/{id} — missing object ownership check; any contestant can read any other contestant's code. CI-03: 6 crypto mistakes (CM-01 through CM-06) — SHA-256 passwords, ECB encryption, predictable reset tokens, hardcoded JWT secret, keyless webhook verification, static AES nonce. |
| **HIGH Issues** | HI-01: Missing admin audit log — no non-repudiation for admin actions. HI-02: JWT alg:none not explicitly rejected — needs library config audit. HI-03: Third-party scripts loaded without SRI — supply chain attack vector. |
| **Strengths** | Event-driven judging architecture (good scalability, right async pattern). Defense in Depth framework in submission flow (6 layers designed). Repository pattern enabling testable service layer. STRIDE analysis complete with threat tree. |
| **Verdict** | ☑ **APPROVED WITH CONDITIONS** |
| **Approval Conditions** | (1) Fix IDOR on submission endpoint (≤1 day). (2) Implement gVisor sandbox for JudgeService (1 sprint). (3) Fix all 6 crypto mistakes (1 sprint). (4) Implement append-only admin audit log (1 sprint). Only then should the system proceed to security testing. |

---

*Back to the lab: [labs/lab-5.4.md](../labs/lab-5.4.md)*
