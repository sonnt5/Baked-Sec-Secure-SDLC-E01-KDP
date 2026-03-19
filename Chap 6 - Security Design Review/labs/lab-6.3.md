# Lab 6.3 — Interface Catalogue & PEP/PDP Design

> **Chapter 6 · Security Design and Review**
> Input: Architecture Ch.3 + DFD Ch.4 | Output: Interface Catalogue + PEP/PDP Design Doc

> [!NOTE]
> **Artifacts for this lab:** (1) Interface Catalogue — recording every important interface using 4 required elements: Caller, Operation/Resource, Authority/Privilege, Boundary/Channel. (2) PEP/PDP Design Document — detailing where enforcement and decision occur, with quota/limits design.

## Learning Objectives

- Build a complete Interface Catalogue following the Chapter 6 standard: Caller, Operation, Authority, Boundary.
- Identify misuse/abuse cases for each interface — not just the happy path.
- Design PEP/PDP placement accurately, with quotas and limits expressed in business-meaningful terms.
- Identify shared infrastructure risks and third-party hook risks in the design.

## Context

An Interface Catalogue is the *"contract of access"* for a system. A reviewer in an SDR should not need to guess "who can call this API with what permissions" — they look it up in the catalogue. When the catalogue does not exist, the SDR must spend extra time reconstructing it — a sign the design is not ready for review.

---

## Task 1 — Interface Catalogue (Main Artifact)

Build the Interface Catalogue for CODING WAR. Each entry requires 4 mandatory elements: (1) Caller identity & trust level, (2) Operation & resource with data classification, (3) Authority & privilege requirements, (4) Boundary & channel.

| ID | ① Caller (Who + Trust Level) | ② Operation & Resource (Data Class) | ③ Authority & Privilege (Min required + Max impact) | ④ Boundary & Channel | Key Controls & Misuse Risk |
|----|------------------------------|-------------------------------------|---------------------------------------------------|--------------------|--------------------------|
| **I1** | Contestant (authenticated) — Trust: Internet (B1 crossing) | POST /api/v1/submissions — Upload source code (data: source_code = Sensitive; contest_id, language = Internal) | Min: JWT valid + role=contestant + contest enrollment. Max impact: 1 submission creation, ~64KB resource use; NO verdict manipulation, NO test case access | HTTPS (TLS 1.3) → nginx → API Gateway (B1) → FastAPI submission handler (B2) | Rate limit: 10/hour/user. Input validation: language allowlist, size ≤64KB. Sandbox isolation prevents RCE escape. Misuse: DoS via heavy submissions, side-channel test case leakage via timing. |
| **I2** | Admin (authenticated) — Trust: Internal (VPN/IP allowlist required) | GET/POST/DELETE /admin/* — All system management operations (data: all user data, test cases, contest config = HVA) | Min: JWT valid + role=admin + MFA session active + IP in allowlist. Max impact: CRITICAL — can delete contests, export all user data, modify verdicts | HTTPS + IP whitelist → Admin Console (B1 restricted) → FastAPI admin handler | 2-person approval for bulk ops (Separation of Privilege). Full audit log on every action. Rate limit: strict. Misuse: insider threat — admin abuse to manipulate results or exfiltrate data. |
| **I3** | Judge Service (internal service) — Trust: Internal Service Mesh | Message queue consumer → download test cases → upload verdict (data: test cases = HVA; verdict = Sensitive; execution metrics = Internal) | Min: Valid mTLS cert (`judge-service.coding-war.internal`) + message schema valid + one-time job token. Max impact: verdict for ONE submission only; NO cross-submission access | Internal service mesh (mTLS) → Message Queue (B2) → Judge Service → Sandbox (B3) | Content-addressed artifact download (sha256 verified). Verdict upload requires job token (replay-proof). Misuse: fake judgehost submitting fraudulent verdicts; side-channel via test case access. |
| **I4** | Anonymous User (unauthenticated) — Trust: Internet | GET /api/v1/problems, GET /api/v1/contests — public problem/contest listings (data: problem statements = Public; contest metadata = Internal) | Min: None (public endpoints). Max impact: read-only public data only; no contestant data, no test cases visible | HTTPS → nginx → API Gateway (B1) → FastAPI read handler | Rate limit: 30/min/IP. CDN cacheable. Misuse: scraping all problems; DDoS via concurrent requests. |
| **I5** | Contestant (authenticated) — Trust: Internet (B1) | GET /api/v1/submissions/{public_id} — view own submission result (data: verdict, execution metrics = Sensitive; source_code = conditionally visible) | Min: JWT valid + `submission.user_id == jwt.sub` (OR role=admin). Max impact: own submission data only | HTTPS → API Gateway (B1) → FastAPI with object-level AuthZ (B2) | Object-level ownership check (IDOR prevention). Source code only visible to owner + admin. Misuse: IDOR to access other contestants' submissions. |
| **I6** | Scoreboard Service (internal service) — Trust: Internal | Read contest rankings from DB (data: aggregated scores = Internal; contestant usernames = pseudonymous) | Min: Valid DB read-only service account. Max impact: read aggregated leaderboard data only; NO individual submission details, NO PII | Internal DB connection (B3) with read-only credentials | Row-level policy: only aggregated score data, no raw submissions. Rate limit for external scoreboard API. Misuse: user enumeration via public scoreboard. |
| **I7** | \[Team adds — webhooks/external integration if applicable\] | | | | |

---

## Task 2 — Misuse/Abuse Cases from the Interface Catalogue

Based on the Interface Catalogue, list ≥5 specific misuse cases. Each case must be linked to an interface ID, attacker type, and the design control that prevents it:

| Misuse Case | Linked Interface | Attacker Type | Attack Vector | Current Control | Gap (if any) |
|------------|-----------------|-------------|--------------|----------------|-------------|
| Contestant submits fork-bomb to deplete judgehost resources, slowing judging for others | I1 | Authenticated contestant | POST /submissions with code: `while True: os.fork()` | Resource limits (CPU/mem/time) in sandbox; gVisor seccomp blocks fork bomb | Verify: seccomp profile actually blocks `fork()`; chaos test needed |
| Attacker enumerates other contestants' submissions by iterating public_ids | I5 | Authenticated attacker | GET /submissions/sub_XXXX with brute force | Opaque IDs (CSPRNG, 256-bit entropy = not enumerable); rate limiting | Verify: IDs are actually unpredictable; rate limit on /submissions/{id} |
| Fake judgehost submits fraudulent verdict to manipulate contest results | I3 | Insider / compromised host | POST /judgehost/verdict with fabricated results | mTLS cert authentication; one-time job token | Verify: job token cannot be reused; mTLS cert validation enforced |
| Admin exfiltrates all user data without approval | I2 | Malicious insider admin | GET /admin/users/export | Audit log records action; 2-person approval for bulk export | 2-person approval needs implementing; audit log must be verified immutable |
| \[Team adds\] | | | | | |
| \[Team adds\] | | | | | |

---

## Task 3 — PEP/PDP Design with Business-Meaningful Quotas

Design the detailed PEP/PDP for 3 critical flows. Quotas must be expressed in business terms (not just "max 10 req/sec").

### PEP-01: Submission Flow (I1 — /submissions)

| Field | Content |
|-------|---------|
| **PEP Location** | API Gateway + nginx rate limiter + FastAPI `Depends()` chain |
| **PDP Location** | Auth Service (JWT validation) + DB ownership check (`submission.user_id == jwt.sub`) |
| **Quotas / Limits / Caps (Business Terms)** | Max 10 submissions/hour/user (business: prevent DoS; 1 per 6 min = normal competitive pace). Max 64KB source code (business: legitimate solutions rarely exceed this). Max 1 submission/5sec/user (burst protection). Contest-level: max 500 submissions/hour/contest (prevents judgehost overload). |
| **Enforcement Mechanism** | `@limiter.limit('10/hour')` on submission endpoint; Pydantic validates code size; contest enrollment check via `Depends()` |
| **Audit Requirements** | Every submission logged: `user_id` (opaque), `contest_id`, `language`, `submission_id` (opaque), `timestamp`, `verdict` (on completion) |

### PEP-02: Admin Operations (I2 — /admin/*)

| Field | Content |
|-------|---------|
| **PEP Location** | IP allowlist middleware + MFA session check + API Gateway |
| **PDP Location** | RBAC role check (role=admin) + 2-person approval for destructive operations |
| **Quotas / Limits / Caps (Business Terms)** | Max 1 bulk operation/hour/admin account (business: batch admin actions should be rare and deliberate). Bulk operation threshold: >50 records requires 2-person approval (business: limit blast radius of error/abuse). Rate limit: max 100 admin API calls/minute (admin is not a batch processing account). |
| **Enforcement Mechanism** | Admin IP allowlist middleware runs before auth; Separation of Privilege for bulk ops; MFA session TTL = 30min |
| **Audit Requirements** | ALL admin actions logged; destructive operations require a justification field; audit log is append-only, admin cannot delete own log entries |

### PEP-03: \[Team designs third flow\]

| Field | Content |
|-------|---------|
| **PEP Location** | \[Fill in\] |
| **PDP Location** | \[Fill in\] |
| **Quotas / Limits / Caps (Business Terms)** | \[Express in business terms: "Max X per Y for business reason Z"\] |
| **Enforcement Mechanism** | \[Fill in implementation\] |
| **Audit Requirements** | \[Fill in audit requirements\] |

---

## Task 4 — Shared Infrastructure & Third-Party Hooks Analysis

| Component | Type | Risk if Uncontrolled | Mitigation Design | Residual Risk |
|-----------|------|---------------------|------------------|--------------|
| **Redis Cache (shared between Auth + Submission services)** | Shared Infrastructure | Tenant data leakage if cache keys collide; DoS if one service exhausts shared cache | Namespace cache keys: `'submission:{user_id}:{sub_id}'` — no cross-service key collision; separate Redis DB indexes per service; eviction policy per namespace | Cache poisoning via key prediction — need CSPRNG in key generation |
| **RabbitMQ Message Queue (submission → judge)** | Shared Infrastructure | Fake job injection if producer auth not enforced; judge processing wrong tenant's jobs | mTLS for producer auth; HMAC signature on messages; schema validation at consumer; topic ACLs: only submission-service can publish to `submission.created` | Message replay if nonce not enforced |
| **Syntax highlighter JS library (CDN)** | Third-Party Hook | Supply chain attack: CDN compromised → malicious JS on contestant/admin pages → XSS, session theft | Subresource Integrity (SRI) hash in script tag; Content Security Policy (CSP) blocks inline scripts; pin to specific version (not 'latest.min.js') | Zero-day in pinned version before detection; need automated SCA alerting |
| **Email service (SMTP provider for password reset)** | Third-Party Hook | Email interception; provider compromise leaking reset tokens; SMTP relay abuse | Reset tokens: CSPRNG 256-bit, store only hash; short TTL (15min); single-use; TLS for SMTP; DKIM/SPF config | Token in email transit is briefly exposed — acceptable with short TTL |
| \[Add component\] | | | | |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Interface Catalogue — 6+ interfaces × 4 elements | **36** | Each interface: all 4 elements complete. Missing data classification or max impact = insufficient |
| Misuse/Abuse Cases — ≥5 cases | **20** | Each case: linked to interface ID, realistic attacker, current control assessed honestly (gaps acknowledged) |
| PEP/PDP Design — 3 flows × 5 fields | **30** | Quotas expressed in business terms (not just req/sec); audit requirements specific |
| Shared Infra & Third-Party Analysis | **14** | Risks identified realistically, mitigations are addressable, residual risk acknowledged |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-6.3.md](../solutions/sol-6.3.md)*
