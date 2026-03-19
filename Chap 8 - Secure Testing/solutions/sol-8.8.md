# Solution 8.8 — Penetration Testing: Scoping & Findings

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. The approach shown here is one valid path.

---

## Key Insights

### What separates a professional finding from a weak one

A weak finding: "The login endpoint may be vulnerable to user enumeration."

A strong finding states the evidence as a reproducible procedure:
> POST `{"email":"alice@test.com","password":"wrong"}` → `{"error_code":"AUTH_INVALID","message":"Invalid credentials"}`
> POST `{"email":"nobody@notreal.com","password":"wrong"}` → `{"error_code":"USER_NOT_FOUND","message":"No account found"}`
> The two error codes differ. An attacker iterating through email addresses can distinguish valid from invalid accounts.

The second finding can be reproduced by someone who was not present. The first cannot. Evidence is what makes a finding actionable.

### Sandbox isolation — why clean results are also findings

When the sandbox escape test produces no escape, that is positive evidence — not a null result. "gVisor correctly blocked all four escape attempts: outbound network (TLE returned, no DNS observed), `/etc/passwd` read (RE returned, no file content in verdict), `/proc` enumeration (RE returned), fork bomb (MLE/TLE within 5s, host process count unchanged)." This evidence supports the Coverage Matrix row for TH-03. Document it.

### The CVSS vector — justify it, not just state it

A CVSS score without a vector is not useful. For user enumeration (PT-001): `AV:N` because exploitable over the network; `AC:L` because no special conditions are required; `PR:N` because no authentication is needed; `UI:N` because no user interaction is required; `S:U` because the vulnerability does not cross privilege boundaries; `C:L` because only account existence is disclosed; `I:N`; `A:N`. Base score 5.3 — Medium. If you disagree with any of these, explain why and recalculate.

### Discussion answers

**Q1 — User enumeration already identified in Lab 7.5:** It should still be a pentest finding, because: Lab 7.5 identified the vulnerability in code review; the pentest confirms it is still present and exploitable at runtime. If the fix from Lab 7.5 was applied, the pentest would produce no finding — confirming the fix worked. If the pentest produces a finding, the fix was not applied or was incomplete. The pentest is verification, not duplication.

**Q2 — Sandbox isolation — can you conclude it is secure?** No. You can conclude that the specific escape techniques you attempted did not succeed. Security claims require a statement of scope: "No escape found using techniques X, Y, Z in 30 minutes of testing." New gVisor vulnerabilities are published periodically; each update requires re-testing. A quarterly pentest is a reasonable cadence, not a one-time certification.

**Q3 — What unit tests cannot detect that pentest can:** Chained attacks that span multiple requests and multiple accounts. The vulnerability chain VC-01 from Lab 7.1 requires: user enumeration (one request), rate limit bypass via distributed IPs (multiple requests from multiple sources), account takeover (authenticated request). A unit test can verify each individual control in isolation. Only a pentest can attempt the full chain end-to-end in a realistic environment.

---

*Back to the lab: [labs/lab-8.8.md](../labs/lab-8.8.md)*
