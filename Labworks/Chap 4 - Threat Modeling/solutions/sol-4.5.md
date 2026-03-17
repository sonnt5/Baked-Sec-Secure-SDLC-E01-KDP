# Solution 4.5 — OWASP Step 3: Countermeasures, Misuse Cases & Threat Profile

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — STRIDE Mitigation Techniques (Completed)

| STRIDE | OWASP Standard Techniques | Applied to CODING WAR | Implementation Status |
|--------|--------------------------|----------------------|----------------------|
| **S** | 1. Appropriate authentication 2. Protect secret data 3. Don't store secrets | (1) JWT with RS256 or HS256 + secret rotation; MFA for Admin accounts; bcrypt min cost 12 for passwords. (2) JWT signing secret in Vault/Secret Manager. (3) No plaintext passwords in DB, logs, or code. | \[✓\] TLS ✓ · bcrypt planned · \[✗\] MFA MISSING · Rate limit MISSING |
| **T** | 1. Authorization 2. Hashes/MACs 3. Digital signatures 4. Tamper-resistant protocols | (1) Object-level AuthZ for all resource access. (2) HMAC on message queue messages to detect tampering. (3) TLS for all data flows. (4) Parameterized SQL queries; input validation on all API inputs. | \[✓\] TLS ✓ · Parameterized queries: needs audit · \[✗\] HMAC on queue MISSING · Object-level AuthZ MISSING |
| **R** | 1. Digital signatures 2. Timestamps 3. Audit trails | (1) Append-only audit log for all admin actions (problem/user/contest changes). (2) NTP-synced timestamps on all log entries. (3) Immutable log storage (write-once S3 bucket or separate log service). | \[✗\] Admin audit log MISSING completely |
| **I** | 1. Authorization 2. Privacy-enhanced protocols 3. Encryption 4. Protect secrets 5. Don't store secrets | (1) Role-based access control; object-level checks. (2) TLS everywhere (in transit); AES-256 at rest for sensitive fields. (3) Generic error messages to clients; stack traces suppressed. (4) PII minimization — don't collect phone numbers. | \[✓\] TLS ✓ · \[✗\] Encryption at rest MISSING · Generic errors MISSING |
| **D** | 1. Appropriate authentication 2. Appropriate authorization 3. Filtering/Throttling 4. Quality of service | (1) Rate limiting: 30 submissions/hour/user. (2) Resource limits per sandbox: CPU 1 core, memory 256MB, time 30s. (3) Circuit breaker on JudgeWorker queue. (4) Queue depth monitoring; auto-scale workers on backlog. | \[✗\] Rate limit MISSING · Resource limits PLANNED · Circuit breaker MISSING |
| **E** | 1. Run with least privilege | (1) JudgeWorker runs as non-root (uid 65534). (2) Service accounts have minimal DB permissions (read-only for most, read/write only for submission service). (3) Object-level AuthZ on /submissions/{id} endpoint. | \[✗\] Object-level AuthZ MISSING · \[~\] Least privilege for service accounts: partially implemented |

---

## Task 3 — Threat Profile (Additional Threats)

| Threat ID | Summary | Mitigation Status | Evidence | Residual Risk | Action |
|-----------|---------|------------------|---------|--------------|--------|
| **TH-06** | JWT alg:none bypass | ⚠️ PARTIALLY | JWT library used: ✓, but explicit alg validation: NEEDS AUDIT | HIGH — may be exploitable | Audit JWT library config; add explicit `algorithms=["HS256"]` |
| **TH-07** | Test case key guessing | ✅ FULLY | UUID-based storage keys: ✓, Internal-only access to MinIO: ✓ | LOW | Monitor access logs |
| **TH-08** | Scoreboard user enumeration | ⚠️ PARTIALLY | Scoreboard is public by design: ✓, Rate limit: MISSING | MEDIUM | Add rate limit + optional pseudonym mode |
| **TH-09** | Registration flood | ⚠️ PARTIALLY | Email verification: ✓, CAPTCHA: MISSING | MEDIUM | Add CAPTCHA + registration rate limit per IP |
| **TH-10** | XSS via problem description | ⚠️ PARTIALLY | Markdown rendering: ✓, CSP header: MISSING | MEDIUM | Add strict CSP header; sanitize admin HTML input |

**Threat Profile Summary:**

| 🔴 Non-mitigated | ⚠️ Partially mitigated | ✅ Fully mitigated |
|-----------------|----------------------|------------------|
| 2 threats: TH-02 (IDOR), TH-05 (Missing audit log) | 6 threats: TH-01, TH-03, TH-04, TH-06, TH-08, TH-09, TH-10 | 1 threat: TH-07 (Test case key guessing) |

---

*Back to the lab: [labs/lab-4.5.md](../labs/lab-4.5.md)*
