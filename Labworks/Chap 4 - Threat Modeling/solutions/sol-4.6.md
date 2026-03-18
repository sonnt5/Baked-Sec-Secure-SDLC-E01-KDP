# Solution 4.6 — OWASP Step 4: Risk Register, Prioritization & Q4 Review

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — Risk Register (Additional Threats)

| Threat ID | STRIDE | Threat Summary | L (1–5) | I (1–5) | Risk Score | Risk Level | Mitigation Status | Residual Risk |
|-----------|--------|---------------|---------|---------|-----------|-----------|------------------|--------------|
| **TH-06** | S | JWT algorithm confusion (RS256/HS256) | 2 | 5 | 10 | High | Partially mitigated (RS256 per SDD) | Medium — needs explicit audit |
| **TH-07** | I | Test case key guessing | 1 | 4 | 4 | Medium | Fully mitigated | Low |
| **TH-08** | I | Scoreboard user enumeration | 4 | 2 | 8 | Medium | Partially mitigated | Low-Medium |
| **TH-09** | D | Registration flood | 3 | 3 | 9 | High | Partially mitigated | Medium |
| **TH-10** | T | XSS via problem description | 2 | 3 | 6 | Medium | Partially mitigated | Low-Medium |

---

## Task 3 — Mitigation Plans (Completed)

### TH-01 / MC-01 — Credential Stuffing

| Strategy | Mitigation Actions | Implementation Notes | Owner + Sprint |
|----------|------------------|---------------------|---------------|
| **🛡️ Reduce L** | Implement rate limiting: 10 req/min/IP; account lockout after 5 failures (15-min lock); CAPTCHA after 3 failures | Use Redis sliding window counter; lockout resets via email confirmation | Backend Auth Team · Sprint 1 |
| **💥 Reduce I** | Mandate MFA for all admin accounts; offer TOTP 2FA for contestants; enforce Argon2id (64MB, 4 iterations, 2 parallelism) per SDD | TOTP via Google Authenticator or Authy; store TOTP secret encrypted in DB | Backend Auth Team · Sprint 2 |
| **👁️ Increase D** | Log ALL login attempts (success + failure) with IP, user-agent, timestamp; alert on >50 failures/hour from same IP | Use structured logging (JSON); ship to SIEM; alert via PagerDuty on threshold | Security/Infra Team · Sprint 1 |

### TH-03 / MC-02 — DoS + RCE via Submission

| Strategy | Mitigation Actions | Implementation Notes | Owner + Sprint |
|----------|------------------|---------------------|---------------|
| **🛡️ Reduce L** | Enable gVisor sandbox for all judge executions; implement seccomp profile blocking all non-essential syscalls; disable outbound network in judge container | Use `runsc` (gVisor) in Docker; test with PoC exploit code before deploy | Infra/Judge Team · Sprint 1 |
| **💥 Reduce I** | Hard limits: CPU=1 core, memory=256MB, wall time=30s, file writes=limited; SIGKILL on exceed; separate judge node from app server | Implement via Docker resource flags + gVisor quotas; test with `stress` tool | Infra Team · Sprint 1 |
| **👁️ Increase D** | Monitor outbound network from judge nodes (should be ZERO); alert on any external DNS query; syscall anomaly detection | eBPF-based network monitoring; Falco for syscall alerts | Security/Infra Team · Sprint 2 |

### TH-02 / MC-03 — IDOR on Submissions

| Strategy | Mitigation Actions | Implementation Notes | Owner + Sprint |
|----------|------------------|---------------------|---------------|
| **🛡️ Reduce L** | Add object-level ownership check on all submission endpoints: `assert submission.user_id == jwt.sub`; make check a shared middleware | Apply to GET, PUT, DELETE /submissions/{id}; code review checklist item | Backend Team · Sprint 1 (1 day) |
| **💥 Reduce I** | Admin access to any submission only via dedicated `/admin/submissions/{id}` endpoint with separate audit log (admin_audit_logs table); contestants cannot access admin endpoint | Separate route with Admin role check + mandatory audit log entry to admin_audit_logs table | Backend Team · Sprint 1 |
| **👁️ Increase D** | Log all submission access: `{user_id, submission_id, owned_by, accessed_at}` to admin_audit_logs; alert if user accesses >10 submissions not owned by them in 1 minute | Pattern detection via log analysis; rate limit 10 req/min/user on /submissions/{id} | Security Team · Sprint 2 |

### TH-05 — Missing Admin Audit Log

| Strategy | Mitigation Actions | Implementation Notes | Owner + Sprint |
|----------|------------------|---------------------|---------------|
| **🛡️ Reduce L** | Implement append-only audit log (admin_audit_logs table per SDD) for all admin actions: create/edit/delete problem, contest, user; log who, what, when, from where | Use dedicated admin_audit_logs table with immutable append-only constraint or separate object storage (S3 with Object Lock) | Backend Team · Sprint 1 |
| **💥 Reduce I** | Admin actions require secondary approval for destructive operations (delete problem, ban user); two-person rule | Implement approval workflow for DELETE operations; email notification to CISO | Backend Team · Sprint 2 |
| **👁️ Increase D** | Alert on anomalous admin activity: bulk deletes, off-hours access, unusual IP; monthly audit log review by Security team | SIEM correlation rules; automated anomaly detection | Security Team · Sprint 1 |

---

## Task 4 — Q4 Evidence Checklist (Reference Answers)

| Q4 OWASP Check | Status | Evidence / Notes |
|----------------|--------|-----------------|
| Is there a DFD showing the system being modeled? | ✓ | DFD Level-0 and Level-1 completed in Lab 4.2; stored in `assets/CODING_WAR_ThreatModel_OWASP.json` |
| Is there a documented threat list? | ✓ | 10 threats in DREAD table (Lab 4.4); expanded in Risk Register (Lab 4.6) |
| Is there a control list for each threat? | ✓ | STRIDE Mitigation Techniques table (Lab 4.5, Task 1); Mitigation Plan (Lab 4.6, Task 3) |
| Do all Critical/High threats have a Mitigation Plan with an owner? | ✓ | TH-01, TH-02, TH-03, TH-05, MC-02 all have 3-strategy plans with owners |
| Does the Threat Profile correctly classify threats? | ✓ | 2 Non-mitigated, 7 Partially, 1 Fully mitigated (Lab 4.5, Task 3) |
| Does the Asset Register cover all DFD assets? | Partial | 10 assets registered; need to verify all DFD data stores are included |
| Does every trust boundary have ≥1 analyzed threat? | ✓ | B1–B4 all have STRIDE analysis in Lab 4.4, Task 2 |
| Do Misuse Cases have measurable detection criteria? | ✓ | MC-01 through MC-04 all have threshold-based detection criteria |
| Are scope assumptions documented? | ✓ | Lab 4.1, Task 1 — Scope Summary field filled in |
| Do deferred threats have justification? | ✗ | No threats have been formally deferred — this section is incomplete |
| Is the Threat Model linked to SRS requirements? | Partial | Entry Points linked to FRs; NFRs (performance) not explicitly traced |
| Is the DFD consistent with Architecture Design (Lab 3.2)? | ✓ | DFD components match Architecture Diagram components; trust boundaries align with deployment zones |
| Were Exit Points analyzed? | ✓ | 8 Exit Points in Lab 4.2, Task 6 |
| Are External Dependencies documented? | ✓ | 7 dependencies in Lab 4.2, Task 7 |

---

*Back to the lab: [labs/lab-4.6.md](../labs/lab-4.6.md)*
