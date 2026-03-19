# Solution 6.7 — Full SDR Practice: From Design to Verdict

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.

---

## Task 3 — SDR Verdict (Reference)

| Section | Reference Answer |
|---------|----------------|
| **SDR Verdict** | ☑ **APPROVED WITH CONDITIONS** |
| **Blocking Conditions** | (1) Issue #1: Account lockout must be implemented and tested (test: `test_account_lockout_after_5_failures` must pass) before design is approved. (2) Issue #2: Code review must confirm `Depends(verify_submission_owner)` is present on ALL submission endpoints — provide code diff as evidence. (3) Issue #3: Backend RBAC for admin destructive operations must be designed (not UI-only) — provide design doc for 2-person approval workflow. |
| **Non-Blocking Requirements** | HIGH: Issue #4 (sandbox verification — add CIS benchmark to security test plan). HIGH: Issue #5 (update CDR-003 to ES256). HIGH: Issue #8 (add DELETE-denied test for audit log). MEDIUM: Issues #6, #7. |
| **Strengths** | (1) Envelope Encryption design is architecturally sound — DEK/CMK separation provides strong defense in depth. (2) Interface Catalogue demonstrates security thinking was applied from the beginning of design, not bolted on. (3) TLS configuration (nginx config) is thorough — TLS 1.3, HSTS, OCSP stapling, session tickets disabled. (4) 4 of 6 assumptions are well-documented with verification methods and fallbacks — good traceability practice. |
| **Next SDR Trigger** | Mini-SDR to verify blocking conditions resolved (target: 2 weeks). Full re-SDR if: auth mechanism changes (e.g., add OAuth/SSO), judge engine is replaced, new admin capabilities are added with elevated privileges. |
| **Executive Summary** | CODING WAR's design was reviewed covering authentication, submission pipeline, judging, and admin interfaces. Three critical design issues were identified: missing account lockout, unconfirmed IDOR protection, and insufficient admin access controls. Design approval is deferred until these three issues are resolved — estimated 1–2 sprints. The cryptographic architecture and TLS configuration are well-designed and do not require revision. |

---

## Task 4 — Disagreement Analysis

**Why documenting a disagreement has value (≥3 reasons):**

1. **Traceability:** If an incident occurs 6 months later related to the disputed issue, the documented disagreement provides context: "we knew this was a risk, the designer argued X, the reviewer argued Y, and we chose option A." This prevents finger-pointing and enables faster root cause analysis.

2. **Future accountability:** The team member who "won" the disagreement is now accountable for the outcome. If the disagreement was "we don't need to verify gVisor" and a sandbox escape later occurs, the documented record shows who made the decision and why — enabling learning without blame.

3. **Institutional memory:** Team members leave. The documented disagreement preserves reasoning that might otherwise be lost. A new team member reviewing the design sees not just the decision but the alternatives that were considered and rejected — preventing them from naively "fixing" something that was deliberately designed.

4. **Escalation trigger:** A documented unresolved disagreement creates a clear escalation path — if the same issue appears in a security incident report, the unresolved disagreement record provides the audit trail for a post-incident review committee.

---

*Back to the lab: [labs/lab-6.7.md](../labs/lab-6.7.md)*
