# Solution 6.6 — SDR Process & Preparation

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.

---

## Task 2c — Reference Review Questions (Completed Examples)

**Group Q1 — Scope & Design Intent**

| Q | Question | Red Flags if Answer is Weak |
|---|---------|---------------------------|
| Q1 | Trust boundary B3 (Services → Data) — who specifically can cross this boundary? Is there any service that should not cross it but does? | Red flag: "the app server can access the DB" — not specific enough. Strong answer: lists each service (AuthService → User DB read, SubmissionService → Submission DB read/write, JudgeService → TestCase DB read-only via pre-signed URL) with explicit deny for others. |
| Q2 | Scoring and verdicts are High Value Assets — how many code paths can currently write to the verdict table? Is there any path that doesn't go through the judge service? | Red flag: "only the judge service can write verdicts" without being able to name the specific code path. Strong answer: `JudgeService.save_result()` in `app/judge/service.py:L142`; admin can also update via `/admin/verdicts/{id}` (which requires 2-person approval). No other paths. |
| Q3 | The Interface Catalogue shows I3 (JudgeService) uses a one-time job token. What is the TTL of this token? What happens if the token is not used? | Red flag: "it expires" without specifics. Strong answer: TTL = 60s from job assignment; if unused, job returns to queue; no token reuse possible (deleted after use or expiry). |

**Group Q2 — Threats & Risks**

| Q | Question | Red Flags |
|---|---------|----------|
| Q1 | Scenario: contestant escapes sandbox. Can they (a) read test cases? (b) submit fake verdict? (c) affect others? | Red flag: "the sandbox prevents this" — circular reasoning. Strong answer: (a) No — test cases in separate MinIO with access only via pre-signed URL with contest_id scope; judge container has no direct MinIO access. (b) No — verdict upload requires one-time job token tied to specific submission_id. (c) Possible via resource exhaustion if resource limits not enforced — TH-03 partially mitigated. |
| Q4 | One unverified assumption is that the JWT secret is not in source code. If this assumption were found to be false today, what is your incident response? | Red flag: "we would fix it." Strong answer: Specific steps: (1) Rotate JWT secret in KMS immediately, (2) Invalidate all active sessions (purge Redis token store), (3) Force re-login for all users, (4) Audit git history for other leaked secrets, (5) Post-incident: add gitleaks to pre-commit hooks. |

---

*Back to the lab: [labs/lab-6.6.md](../labs/lab-6.6.md)*
