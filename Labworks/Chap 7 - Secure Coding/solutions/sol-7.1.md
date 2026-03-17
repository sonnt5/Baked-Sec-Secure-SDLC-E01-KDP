# Solution 7.1 — Design Invariants → Code Contracts

> [!WARNING]
> **Reference Solution** — Complete the lab on your own before consulting this.

---

## Task 2 — CI-08 (Team entry example)

| ID | Design Assumption | Code Invariant | Enforcement Location | Violation Detection | Priority / ASVS |
|----|------------------|----------------|---------------------|--------------------|--------------------|
| **CI-08** | Password reset tokens are single-use and expire after 15 minutes | `PasswordResetRepository.consume_token()` marks tokens as `used=True` atomically; reuse returns `None`; tokens older than 900s are rejected regardless | `app/repositories/password_reset_repo.py`: `consume_token()` uses atomic `UPDATE ... WHERE used=False AND created_at > now()-900s RETURNING id` | Unit test: `test_reset_token_cannot_be_used_twice`; unit test: `test_reset_token_expired_after_15min` | High / ASVS V7.4 |

---

## Task 3 — VC-03 (Team chain example: SRI → CDN compromise → admin credential theft)

| Step | Bug | Severity (isolated) | Asset | Chain |
|------|-----|--------------------|----|------|
| 1 | Syntax highlighter JS loaded from CDN without SRI hash | Low | Frontend security | → Enables 2 |
| 2 | CDN compromised; attacker injects keylogger into `syntax-highlighter.min.js` | High | Admin browser session | → Enables 3 |
| 3 | Admin logs in; keylogger captures username + password + MFA token within 30s TOTP window | High | Admin credentials | → Enables 4 |
| 4 | Attacker uses credentials within TOTP window → full admin access → manipulate verdicts, export all data | **Critical** | All HVAs | ⚠️ Final impact |

**Fix:** SRI hash on all external scripts. CSP `script-src 'self'` blocks unapproved CDN scripts. Self-host critical JS. ASVS V3.6.1.

---

## Discussion Answers

**Q1:** A test proves current behavior once; a code invariant prevents future violations. If CI-04 only exists as a test for `sandbox_runner.py`, a developer can add `admin_debug.py` with `subprocess.run(shell=True)` and the test still passes. The SAST rule catches the violation in `admin_debug.py` immediately on every future PR. Without the enforcement location, the invariant has no force beyond the moment it was written.

**Q2:** Chain severity exceeds individual severity because the chain eliminates compensating controls. IDOR (High) alone is partially mitigated by opaque IDs making enumeration hard. Add missing audit log (High) and the attacker has no forensic risk. Add CI-03 violation (no MFA for admin) and the attacker escalates from read-only data theft to full verdict manipulation — a capability no individual bug provides.

**Q3:** The Code Contract Document serves as institutional memory. A new developer consulting it during PR review immediately sees CI-03 with its enforcement mechanism (`@require_admin_mfa` decorator) and violation detection (checklist + unit test) — without needing to read the full SDR report. Without the document, invariants live only in the heads of the original team and vanish when people leave.

---

## Code References

Lab 7.1 does not use dedicated code files — the Code Contract Document and Vulnerability Chain Analysis are text artifacts. The SAST rules that enforce CI-01–CI-06 live in [`code/semgrep-rules/coding-war-custom.yaml`](../code/semgrep-rules/coding-war-custom.yaml).

---

*Back to the lab: [labs/lab-7.1.md](../labs/lab-7.1.md)*
