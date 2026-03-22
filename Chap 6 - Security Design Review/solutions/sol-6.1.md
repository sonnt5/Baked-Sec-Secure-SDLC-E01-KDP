# Solution 6.1 — Evidence-Based Design: CAE Chain & Assumption Register

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.
> Complete the lab on your own before consulting this.

---

## Task 1 — CAE Model Analysis Answers

**Question 1:** If Evidence ① (the pytest test) does not exist, the claim cannot be SDR-approved. The SDR process requires testable evidence — a claim without a running test means the reviewer has no way to independently verify the mechanism works. An Argument alone describes *intent*, not *proof*. Without the test, the claim has the same evidential weight as saying "we believe the system is secure."

**Question 2:** If an internal admin script queries the DB directly without going through `verify_submission_owner()`, this violates **Complete Mediation** — the pattern requires that *every* access path goes through the centralized guard, with no side doors. The claim would no longer be valid because the Argument states "every GET /submissions/{id} request passes through verify_submission_owner()" — a single exception invalidates the universal claim.

**Question 3:**
- **MUST HAVE:** ① (pytest test) — the only machine-verifiable proof the mechanism works. ② (admin exception test) — the Argument claims admin is the exception; without this test, the exception itself is unverified.
- **NICE TO HAVE:** ③ (code review checklist item) — useful for process traceability but cannot substitute for a running test. ④ (log sample) — provides operational evidence but may be stale.

---

## Task 2 — CAE Table (Reference Entries)

### CAE-01: Credential Stuffing Prevention

| Element | Content |
|---------|---------|
| **Claim** | CODING WAR prevents automated credential stuffing: an attacker using a botnet of up to 10,000 IPs cannot exceed 30 password attempts per user account per hour without triggering lockout. |
| **Argument** | Three independent controls: (1) Rate limiting at API Gateway: max 10 req/min/IP via Redis sliding window (per SDD 3.3: 1 req/10s baseline, adjusted for security). (2) Account lockout: 5 consecutive failures per email/10min → 15min lock. (3) Uniform error response: identical message and timing for valid/invalid credentials — prevents user enumeration. Patterns: Defense in Depth (three independent layers), Fail Securely (lockout as safe default), Least Information (no credential existence disclosure). |
| **Evidence** | ① `tests/security/test_rate_limiting.py::test_login_rate_limit_returns_429_after_10_rpm` ② `tests/security/test_account_lockout.py::test_locked_after_5_failures` ③ `tests/security/test_account_lockout.py::test_lockout_resets_after_15min` ④ `tests/security/test_user_enumeration.py::test_response_identical_valid_invalid_user` ⑤ Prometheus alert rule: `login_failures_total > 50 in 5m` |

### CAE-02: IDOR Prevention

| Element | Content |
|---------|---------|
| **Claim** | No authenticated contestant can read, modify, or delete another contestant's submission via any submission-related API endpoint. |
| **Argument** | Every submission endpoint uses `Depends(verify_submission_owner)`, which checks `submission.user_id == current_user.id` before returning data. Admin access routed through a separate `/admin/submissions/{id}` endpoint with audit logging. Enforced at Trust Boundary B2 before business logic runs. Pattern: Complete Mediation (every access), Least Privilege (contestant access own only). |
| **Evidence** | ① `tests/security/test_idor.py::test_contestant_cannot_read_another_contestant_submission_returns_403` ② `tests/security/test_idor.py::test_admin_can_read_any_submission_with_audit_log` ③ Code review checklist #7: "All object endpoints have ownership check" ④ Code diff: `Depends(verify_submission_owner)` present on all 3 submission GET/PUT/DELETE routes |

### CAE-03: Code Execution Isolation

| Element | Content |
|---------|---------|
| **Claim** | Code submitted by contestants cannot read test case files, access other contestants' data, make outbound network calls, or persist state outside the /tmp directory during execution. |
| **Argument** | gVisor (runsc) runtime blocks all syscalls not on the approved list via seccomp profile — prevents direct filesystem access outside sandbox. Network namespace isolation (network_mode: none per SDD 3.2.2): judge container has no internet route — outbound blocked by default deny. Resource limits: CPU=1 core, memory=256MB, wall time=30s, SIGKILL on exceed (Cgroups v2 per SDD 5.1). Filesystem: read-only except /tmp. Pattern: Defense in Depth (4 independent isolation layers), Least Privilege (judge runs as uid 10001 per SDD 7.1). |
| **Evidence** | ① `tests/judge/test_sandbox.py::test_outbound_network_blocked_from_judge_container` ② `tests/judge/test_sandbox.py::test_file_outside_tmp_cannot_be_written` ③ `tests/judge/test_resource_limits.py::test_infinite_loop_killed_within_30s` ④ `tests/judge/test_sandbox.py::test_fork_bomb_blocked_by_seccomp` ⑤ CIS Docker Benchmark report for judge container (Assumption ASS-03 verification) |

---

## Task 3 — Assumption Register (Filled Assumptions 4–6)

| # | Assumption | Verification Method | Fallback if Wrong | Owner | Metric | Status |
|---|-----------|--------------------|--------------------|-------|--------|--------|
| **4** | PostgreSQL is only accessible from the app server — no direct internet access to port 5432 | Firewall rule audit; `nmap` scan from external IP; `pg_hba.conf` review | Immediately block port 5432; rotate DB credentials; audit recent connections | DevOps | 0 connections from non-app-server IPs in `pg_log` | Unverified |
| **5** | All critical scripts are self-hosted at static.coding-war.io and verified with SRI (Subresource Integrity) during build — no third-party CDN dependencies for security-critical components | SRI hash verification; automated SCA scan weekly; content hash monitoring; CSP script-src 'self' enforcement | Block any third-party scripts via CSP; incident response if unexpected script detected | Frontend + Security | SRI hash matches for all scripts; 0 CSP violations; all scripts served from static.coding-war.io | Unverified |
| **6** | All admin accounts are protected with MFA — no admin uses password-only auth | Admin account audit; verify MFA enforcement in auth settings; test login without MFA token fails | Force MFA enrollment; temporarily disable MFA-less admin accounts | Security + Auth Team | 0 admin accounts with `mfa_enabled = false` | Unverified |

**Question 4:** Assumption #3 (gVisor sandbox isolation) — if wrong, a contestant could execute arbitrary commands on the judge server, read all test cases, access DB credentials, and pivot to the app server. Unlike a misconfigured firewall, a sandbox escape during a live contest could compromise the entire system before detection.

**Question 5:** An unverified Assumption Register makes the team's trust model explicit and visible. Without it, assumptions are implicit — no one knows to question them. With it, SDR reviewers can immediately see what has been assumed vs. verified, assign owners and deadlines, and include assumption verification in the security testing plan. It transforms unknown unknowns into known unknowns.

**Question 6:** Escalate an assumption to a verified constraint when: (1) its failure causes a CRITICAL security impact, (2) it is a prerequisite for another security claim, or (3) the system is approaching production and the assumption remains unverified.

---

*Back to the lab: [labs/lab-6.1.md](../labs/lab-6.1.md)*
