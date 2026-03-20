# Solution 8.4 — Supply Chain Security: SCA + Container + Secrets

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. The approach shown here is one valid path.

---

## Key Insights

### Exploitability assessment — the critical step

A CVE score of CRITICAL does not mean the vulnerability is critical in your system. The relevant question is: is the vulnerable code path reachable with attacker-controlled input in CODING WAR's actual usage? A memory corruption CVE in a C extension that is never called by the Python code CODING WAR uses is not an actionable finding. Document the assessment — not just "exploitable" or "not exploitable" but which call sites were checked and what they do.

### passlib migration

The correct migration from `passlib[argon2]` to `argon2-cffi` preserves existing hashes — the PHC string format is compatible. The only breaking change is argument order in `verify()`: `passlib` takes `(plaintext, hash)` while `argon2-cffi` takes `(hash, plaintext)`. If this is reversed in the migration, every password verification silently fails — a security regression that might not be caught if tests only check successful verification.

### detect-secrets baseline management

The `.secrets.baseline` file records which strings were reviewed and why they are not real secrets. It must be committed and kept up to date — a stale baseline where strings are marked false-positive without review is not better than no baseline. The CI check (`detect-secrets scan --baseline .secrets.baseline`) only catches *new* secrets added after the baseline was created. It does not re-evaluate previously dismissed findings.

### Discussion answers

**Q1 — CRITICAL CVE in deprecated endpoint:** Patch now. The endpoint exists in the codebase and is reachable. "It will be removed next sprint" is a prediction, not a guarantee. If the sprint slips or the endpoint is not removed, the vulnerability remains. The effort to patch is lower than the effort to justify and track the exception.

**Q2 — 15 MEDIUM OS CVEs in base image:** Rebuild if any CVE is in a library that handles untrusted input (network parsers, compression, TLS). Defer if all CVEs are in utilities that never process attacker-controlled data. Document the reasoning. "No incidents in 6 months" is not evidence of safety — it is evidence of no detected exploitation.

**Q3 — Stale baseline risk:** A baseline that has not been audited in 6 months may contain dismissed secrets that were real secrets at the time. Team members who dismissed findings may have left. The correct practice is to periodically re-audit dismissed findings and rotate any credentials that were exposed, even if they were later dismissed as "test-only."

---

*Back to the lab: [labs/lab-8.4.md](../labs/lab-8.4.md)*
