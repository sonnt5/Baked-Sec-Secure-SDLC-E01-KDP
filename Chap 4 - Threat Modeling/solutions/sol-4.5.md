# Solution 4.5 — OWASP Step 3: Countermeasures, Misuse Cases & Threat Profile

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — STRIDE Mitigation Techniques (Completed)

| STRIDE | OWASP Standard Techniques | Applied to CODING WAR | Implementation Status |
|--------|--------------------------|----------------------|----------------------|
| **S** | 1. Appropriate authentication 2. Protect secret data 3. Don't store secrets | (1) JWT with RS256 (asymmetric key per SDD) + MFA for Admin accounts; Argon2id (64MB, 4 iterations, 2 parallelism) for passwords per SDD. (2) JWT signing private key in Vault/Secret Manager. (3) No plaintext passwords in DB, logs, or code. | \[✓\] TLS ✓ · Argon2id planned · \[✗\] MFA MISSING · Rate limit MISSING |
| **T** | 1. Authorization 2. Hashes/MACs 3. Digital signatures 4. Tamper-resistant protocols | (1) Object-level AuthZ for all resource access. (2) HMAC on message queue messages to detect tampering. (3) TLS for all data flows; mTLS for internal service communication. (4) Parameterized SQL queries; input validation on all API inputs. | \[✓\] TLS ✓ · mTLS ✓ · Parameterized queries: needs audit · \[✗\] HMAC on queue MISSING · Object-level AuthZ MISSING |
| **R** | 1. Digital signatures 2. Timestamps 3. Audit trails | (1) Append-only audit log (admin_audit_logs table per SDD) for all admin actions. (2) NTP-synced timestamps on all log entries. (3) Immutable log storage (write-once S3 bucket or separate log service). | \[~\] Admin audit log: Database schema designed (SDD), code implementation pending |
| **I** | 1. Authorization 2. Privacy-enhanced protocols 3. Encryption 4. Protect secrets 5. Don't store secrets | (1) Role-based access control; object-level checks. (2) TLS everywhere (in transit); mTLS for internal services; AES-256 at rest for sensitive fields. (3) Generic error messages to clients; stack traces suppressed. (4) PII minimization — only collect username, email, password per SRS UC-01. | \[✓\] TLS ✓ · mTLS ✓ · \[✗\] Encryption at rest MISSING · Generic errors MISSING |
| **D** | 1. Appropriate authentication 2. Appropriate authorization 3. Filtering/Throttling 4. Quality of service | (1) Rate limiting: 30 submissions/hour/user. (2) Resource limits per sandbox: CPU 1 core, memory 256MB, time 30s (Cgroups v2 per SDD). (3) Circuit breaker on JudgeWorker queue. (4) Queue depth monitoring; auto-scale workers on backlog. | \[~\] Rate limit MISSING · Resource limits: Infrastructure designed (SDD) · Circuit breaker MISSING |
| **E** | 1. Run with least privilege | (1) JudgeWorker runs as non-root (uid 10001 per SDD). (2) Service accounts have minimal DB permissions (read-only for most, read/write only for submission service). (3) Object-level AuthZ on /submissions/{id} endpoint. | \[✗\] Object-level AuthZ MISSING · \[~\] Least privilege for service accounts: partially implemented |

---

## Task 3 — Threat Profile (Additional Threats)

| Threat ID | Summary | Mitigation Status | Evidence | Residual Risk | Action |
|-----------|---------|------------------|---------|--------------|--------|
| **TH-06** | JWT algorithm confusion | ⚠️ PARTIALLY | JWT library uses RS256 (per SDD): ✓, but explicit alg validation: NEEDS AUDIT | MEDIUM — may be exploitable if misconfigured | Audit JWT library config; add explicit `algorithms=["RS256"]` |
| **TH-07** | Test case key guessing | ✅ FULLY | UUID-based storage keys: ✓, Internal-only access to S3 with mTLS: ✓ | LOW | Monitor access logs |
| **TH-08** | Scoreboard user enumeration | ⚠️ PARTIALLY | Scoreboard is public by design: ✓, Rate limit: MISSING | MEDIUM | Add rate limit + optional pseudonym mode |
| **TH-09** | Registration flood | ⚠️ PARTIALLY | Email verification: ✓, CAPTCHA: MISSING | MEDIUM | Add CAPTCHA + registration rate limit per IP |
| **TH-10** | XSS via problem description | ⚠️ PARTIALLY | Markdown rendering: ✓, CSP header: MISSING | MEDIUM | Add strict CSP header; sanitize admin HTML input |

**Threat Profile Summary:**

| 🔴 Non-mitigated | ⚠️ Partially mitigated | ✅ Fully mitigated |
|-----------------|----------------------|------------------|
| 2 threats: TH-02 (IDOR), TH-05 (Missing audit log) | 6 threats: TH-01, TH-03, TH-04, TH-06, TH-08, TH-09, TH-10 | 1 threat: TH-07 (Test case key guessing) |

---

*Back to the lab: [labs/lab-4.5.md](../labs/lab-4.5.md)*
