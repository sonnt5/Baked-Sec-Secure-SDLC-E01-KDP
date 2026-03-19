# Solution 6.5 — Privacy by Design & Trade-off Management

> [!WARNING]
> **Reference Solution** — This is a reference answer, not the only correct one.

---

## Task 2 — Trade-off Decision Log (Reference Answers)

### SR-D01: JWT Access Token Expiry

| Field | Reference Answer |
|-------|----------------|
| **Options** | A) 5-minute expiry (max security, poor UX — re-login every few minutes during contest). B) 15-minute expiry + refresh token (balanced — used in current design). C) 24-hour expiry (good UX, max stolen token window). |
| **Decision** | Option B: 15-minute access token + 7-day refresh token with rotation and revocation. |
| **Rationale** | 5 minutes is too disruptive during a contest — a contestant mid-submission would be forced to re-authenticate. 24 hours is too long a window for a stolen token. 15 minutes with silent refresh via refresh token (rotation on use, revoke on password change) gives the security property of short expiry with the UX of longer sessions. This matches industry practice (Auth0, Google, GitHub all use short access + long refresh). |
| **Residual Risk** | If a refresh token is stolen, the attacker has access for up to 7 days unless the user changes their password. Monitoring: alert on refresh token use from new IP/device within 1 hour of prior use. |
| **Review Trigger** | If a refresh token theft incident occurs; if the system moves to a multi-device context where single-token revocation becomes harder. |

### SR-D02: Source Code Encryption — Encrypt Everything

| Field | Reference Answer |
|-------|----------------|
| **Options** | A) Encrypt all submissions (100% coverage, +50ms/submission, ~$150/50k contest). B) Encrypt only after contest ends (submissions encrypted post-contest in batch). C) No encryption (access control only, no cost). |
| **Decision** | Option A: Encrypt all submissions at creation time. |
| **Rationale** | The cost ($150/contest) is negligible compared to the value of the data and the reputational damage of a breach. Option B creates a window where live contest submissions are unencrypted — the highest-risk moment. The 50ms latency is absorbed into the judging pipeline (already takes 5–30s) and is not user-visible. Consistency: if encryption is only for completed contests, the design becomes complex (different code paths for live vs historical) and error-prone. |
| **Residual Risk** | KMS unavailability blocks submission creation (not just decryption). Mitigation: circuit breaker with short retry — if KMS unavailable for >5s, return 503 to user rather than storing unencrypted. |
| **Review Trigger** | If contest scale grows to >500k submissions/contest and KMS cost becomes significant; if KMS latency degrades p95 judging latency. |

### SR-D03: Admin 2-Person Approval

| Field | Reference Answer |
|-------|----------------|
| **Options** | A) 2-person approval for all admin operations. B) 2-person approval only for destructive/bulk operations (>50 records, verdict modification, data export). C) Single-admin for all operations. |
| **Decision** | Option B: scoped 2-person approval. |
| **Rationale** | Option A would block operations during contests when a co-admin may be unavailable — unacceptable operational constraint. Option C provides no insider threat protection. Option B targets the highest-risk operations (where mistakes are irreversible or have large blast radius) while leaving routine operations (view logs, read contest data) as single-admin. This is consistent with the principle of proportional controls. |
| **Residual Risk** | Single-admin operations (e.g., modifying a single user's data) remain a risk for targeted insider abuse. Monitoring: alert on unusual patterns (off-hours access, accessing data not related to current contest). |
| **Review Trigger** | If an insider threat incident occurs with single-admin operations; if compliance requirements mandate 2-person rule for all admin access. |

### SR-D04: Rate Limiting — 10/hour

| Field | Reference Answer |
|-------|----------------|
| **Options** | A) 5/hour (strict DoS prevention, disrupts active training). B) 10/hour (current — moderate protection, allows 1 submission per 6 min). C) 30/hour (permissive — matches training usage, weaker DoS protection). |
| **Decision** | Option B (10/hour) with contest-specific override. |
| **Rationale** | 5/hour is too restrictive for legitimate users training for a contest. 30/hour provides insufficient DoS protection — 500 users × 30 = 15,000 submissions/hour, which could overwhelm the judge queue. 10/hour is a reasonable middle ground. Add a contest-specific override: during a live contest, the rate limit can be raised to 20/hour by the contest organizer (they accept the operational risk). Outside contest hours: keep at 10/hour. |
| **Residual Risk** | Rate limit can be circumvented by distributing submissions across multiple accounts (multi-accounting). Monitoring: flag users with submission-to-acceptance ratio < 5% (possible stress-testing or DoS). |
| **Review Trigger** | If judge queue depth consistently exceeds 2x normal during peak hours; if legitimate user complaints about rate limit increase significantly. |

---

*Back to the lab: [labs/lab-6.5.md](../labs/lab-6.5.md)*
