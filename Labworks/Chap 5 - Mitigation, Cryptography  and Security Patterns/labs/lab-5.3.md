# Lab 5.3 — Security Design Patterns: Pattern Application Worksheet

> **Chapter 5 · Mitigations, Security Patterns, and Cryptography**
> Input: Design artifacts Ch.3–5.2 | Output: Pattern Application Worksheet + Pattern Selection Matrix

> [!NOTE]
> **Artifact for this lab:** Pattern Application Worksheet — a table applying 15 security patterns to CODING WAR, with a Pattern Selection Matrix linking pattern → threat → control point → evidence. This artifact bridges the threat model and the concrete design.

## Learning Objectives

- Identify the right pattern for each type of risk — not applied randomly.
- Understand the trade-offs of each pattern and why they are appropriate for the specific context.
- Link patterns to threats → control points → evidence following the chain: threat → pattern → control point → evidence.
- Recognize when NOT to apply a pattern (over-engineering risk).

## Context

Security Design Patterns are a shared vocabulary that lets a team express secure design decisions without re-explaining them from scratch every time. When an architect says *"apply Complete Mediation at the API Gateway"*, a developer immediately understands a centralized AuthZ check is required — no side door can bypass it. This lab builds a Pattern Application Worksheet — a living document that is updated as the system evolves.

---

## Task 1 — Pattern Quick Reference

Complete the table summarizing 15 patterns across 5 groups. The *"When NOT to use"* column is as important as *"When to use"* — many crypto and design mistakes come from applying the wrong pattern to the wrong context.

| # | Pattern | Core Goal | Main Trade-off | Specific Example in CODING WAR |
|---|---------|----------|---------------|-------------------------------|
| **Group 1: Design Attributes** | | | | |
| 1 | **Economy of Design** | Reduce complexity — fewer components = smaller attack surface | May lack flexibility for future requirements | Single API Gateway for auth/rate-limit instead of each service implementing its own |
| 2 | **Transparent Design** | Security does not depend on the secrecy of the design | Public design requires the design to actually be strong | JWT signing uses ES256 (public algorithm) — security comes from the private key, not algorithm secrecy |
| **Group 2: Exposure Minimization** | | | | |
| 3 | **Least Privilege** | User/service has only the required permissions (Who/What/Which) | Increases complexity in permission management | DB: `ro_user` for query-only routes; JudgeService has no DB write access |
| 4 | **Least Information** | Only expose data needed for the purpose | Response schemas become more complex | `SubmissionPublicResponse`: 6 fields instead of returning the full ORM object |
| 5 | **Secure by Default** | System starts in a safe state | Requires explicit action to enable features | `CORS_ORIGINS=[]` by default; `DEBUG=False`; admin requires MFA with no exceptions |
| 6 | **Allowlists over Blocklists** | Define what is allowed; deny everything else | Allowlist must be maintained comprehensively | Language validator: `{'python','cpp','java'}` — not blocking `'shell','bash','perl'...` |
| 7 | **Avoid Predictability** | IDs/tokens cannot be guessed | Performance overhead of CSPRNG | `submission.public_id = secrets.token_urlsafe(32)` instead of an auto-increment integer |
| 8 | **Fail Securely** | On error, default to denying access | Debug mode is harder — need separate observability | Auth service timeout → 503, not allow-by-default; generic error messages to client |
| **Group 3: Strong Enforcement** | | | | |
| 9 | **Complete Mediation** | Every access goes through a centralized guard | Single point of failure if not HA | All routes — including /export and /admin — go through API Gateway + Auth middleware |
| 10 | **Least Common Mechanism** | Minimize shared infrastructure between tenants/users | Uses more resources than a shared approach | Cache keys include `user_id`: `'submission:{user_id}:{sub_id}'` — no shared cache entries |
| **Group 4: Redundancy** | | | | |
| 11 | **Defense in Depth** | Multiple independent layers — one layer failing is not a disaster | Complexity, false sense of security if layers are not independent | Submission: Rate limit → JWT auth → Schema validation → Sandbox execution → Audit log |
| 12 | **Separation of Privilege** | High-risk action requires ≥2 independent approvals | UX friction, workflow complexity | Bulk delete contest data: requires 2 admin approvals within 60 seconds, different roles |
| **Group 5: Trust & Responsibility** | | | | |
| 13 | **Reluctance to Trust** | Verify before trusting — including internal requests | Overhead of verification, latency | OrderService recalculates price server-side — does not trust client-sent price/score |
| 14 | **Accept Security Responsibility** | Each component clearly defines its own security guarantees | Documentation overhead | `SubmissionCreate` schema guarantees: language in allowlist, code ≤64KB — documented contract |
| 15 | **\[Add your own pattern\]** | | | \[Fill in CODING WAR example\] |

---

## Task 2 — Pattern Selection Matrix (Main Artifact)

Build a Pattern Selection Matrix linking each threat to the chosen pattern(s), the control point in the architecture, and the verifying evidence. This artifact demonstrates the *threat → pattern → control point → evidence* chain.

| Threat ID | STRIDE | Pattern(s) Selected | Why this pattern for this threat? | Control Point in Architecture | Evidence / Test |
|-----------|--------|--------------------|------------------------------------|------------------------------|----------------|
| **TH-01** | S | Allowlists + Fail Securely + Least Information | Allowlist: only accept valid credential format; Fail Securely: lockout after N fails; Least Information: don't reveal user existence via error message | API Gateway rate limiter + Auth Service lockout logic + Uniform error responses | `test_login_rate_limit_429`, `test_account_lockout_15min`, `test_invalid_user_same_response_as_wrong_password` |
| **TH-02** | E | Least Privilege + Complete Mediation | Least Privilege: contestant can only access own submissions; Complete Mediation: every access goes through ownership check | `SubmissionController.verify_submission_owner()` dependency | `test_contestant_cannot_access_other_submission`, `test_admin_can_access_any_submission` |
| **TH-03** | D + E | Defense in Depth + Least Privilege | Defense in Depth: rate limit → schema validate → sandbox → resource limit; Least Privilege: judge runs as unprivileged user in isolated container | API layer + Pydantic validator + gVisor sandbox + resource limits | `test_submission_rate_limit`, `test_sandbox_network_isolation`, `test_cpu_limit_enforced` |
| **TH-05** | R | Transparent Design + Separation of Privilege | Transparent Design: audit log content does not depend on secrecy; Separation of Privilege: executor cannot delete audit trail | AuditLogMiddleware + append-only storage + separate log admin role | `test_admin_action_creates_audit_entry`, `test_audit_log_cannot_be_deleted_by_app_user` |
| **MC-01 (Password Reset Enumeration)** | I | Avoid Predictability + Least Information + Fail Securely | Avoid Predictability: token from CSPRNG; Least Information: uniform response; Fail Securely: rate limit both valid and invalid emails | `PasswordResetService.create_token()` + constant-time response + rate limit | `test_reset_response_identical_for_existing_nonexisting_email`, `test_reset_token_entropy_128bit` |
| \[Threat from Risk Register\] | | | | | |
| \[Threat from Risk Register\] | | | | | |

---

## Task 3 — Pattern Application Code (FastAPI — Defense in Depth for submission)

The following code implements the Defense in Depth pattern for the submission endpoint. Each `Depends()` is an independent layer in the defense:

```python
# app/api/submissions.py
# Defense in Depth: Layers 1→5 for POST /submissions
# Each layer is independent — one layer failing does not bypass another

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from app.core.security import get_current_user, verify_contest_enrollment
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.submission_service import SubmissionService

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix='/api/v1')

@router.post('/submissions', response_model=SubmissionResponse)
@limiter.limit('10/hour')  # Layer 2: Rate Limit (Reduce)
async def create_submission(
    request: Request,
    data: SubmissionCreate,            # Layer 3: Pydantic validation (Allowlists, size limits)
    current_user=Depends(get_current_user),       # Layer 1: JWT AuthN (Reduce)
    contest=Depends(verify_contest_enrollment),   # Layer 4: Object AuthZ (Resist)
    service: SubmissionService = Depends(get_submission_service),
):
    # Layer 5: Business logic + sandbox (Resist) — handled by JudgeService
    # Layer 6 (implicit): AuditLogMiddleware logs every request (Recover)
    return await service.create(data, current_user, contest)

# Separation of Privilege: bulk operations require 2 approvals
@router.delete('/contests/{contest_id}/submissions')
async def bulk_delete_submissions(
    contest_id: str,
    approver1=Depends(require_role('admin')),  # First admin
    approval2_token: str = Header(...),        # Second admin's time-limited token
):
    if not await validate_second_approval(approval2_token, contest_id, approver1.id):
        raise HTTPException(403, 'Requires two-person approval within 60s')
    # ...
```

Analyze the code above and answer these questions:

**Question 1:** List all 6 layers of Defense in Depth in the submission flow — including the "implicit" layer (not directly visible in this code).

**Question 2:** Why must each layer be "independent"? If Layer 3 (Pydantic validation) is bypassed, do Layers 4 and 5 still provide protection?

**Question 3:** Implement the `verify_contest_enrollment()` dependency: the user must be enrolled, and the contest must be active (`now` is between `start` and `end`). Write the complete Python function.

**Question 4:** Separation of Privilege for `bulk_delete`: what does `validate_second_approval()` need to check? Write pseudocode or Python.

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| Pattern Quick Reference (15 patterns — CODING WAR examples) | **30** | Examples are specific, not redefinitions of the pattern. Vague examples like "implement authentication" do not count — must have detail |
| Pattern Selection Matrix (≥7 threats) | **35** | threat→pattern link is logical (3 pts), control point is specific (1 pt), evidence is testable (1 pt) |
| Code analysis (4 questions) | **20** | Q1: all 6 layers (5 pts), Q2: reasoning on independence (5 pts), Q3+Q4: working code/pseudocode (10 pts) |
| Overall quality | **15** | Pattern selection logic demonstrates understanding — not random application |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-5.3.md](../solutions/sol-5.3.md)*
