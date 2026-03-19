# Solution 8.6 — DAST: OWASP ZAP API Scan

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. The approach shown here is one valid path.

---

## Key Insights

### Why OpenAPI matters for ZAP

Without the spec, ZAP crawls by following links — a strategy that works for server-rendered HTML but fails for REST APIs. A FastAPI application that accepts `POST /submissions` with a JSON body containing `language`, `source_code`, `problem_id`, and `contest_id` is invisible to a crawler unless the OpenAPI spec tells ZAP those fields exist. Without the spec, ZAP would only find the endpoints that appear in HTML responses, which is roughly zero for an API-first application.

### DF-001 — why CSRF is a False Positive here

CSRF attacks work because browsers automatically include cookies on cross-origin requests. An attacker can make a victim's browser send a request to CODING WAR while the victim is logged in — the browser includes the session cookie, and the server accepts it.

CODING WAR's API uses Bearer tokens in the `Authorization` header. Browsers do not automatically include custom headers on cross-origin requests. A cross-origin script would need explicit CORS permission to set `Authorization: Bearer ...`, which CODING WAR's CORS policy does not grant to arbitrary origins. Therefore, a forged cross-origin request cannot include the Bearer token and cannot authenticate. CSRF protection is genuinely not needed for Bearer JWT APIs.

The condition under which it would be needed: if CODING WAR adds a server-rendered admin console that uses cookie-based sessions, those endpoints would require CSRF protection. Document this in the False Positive justification — not just "not applicable" but "not applicable *because* Bearer JWT; would become applicable if cookie auth is added."

### SAST vs DAST — structural coverage difference

SAST sees code. DAST sees runtime behaviour. A static analysis tool can find `db.execute(f"... {sort_field}")` in the source. It cannot observe that a middleware is bypassing the authentication check at runtime, or that a cached response is being served without the security headers that the middleware adds. DAST also catches configuration issues that exist in deployed infrastructure but are not visible in code: a misconfigured nginx that strips the CSP header, a load balancer that drops the Secure cookie flag.

When both SAST and DAST catch the same issue (DF-002 = SF-001), combined confidence is higher — two independent tools operating on different representations of the system agree. The combined severity should reflect this: not just the higher of the two, but a higher confidence in that severity level.

### Discussion answers

**Q1 — DAST finding already caught by SAST:** Do not close as Duplicate without action. The DAST finding is additional evidence that the vulnerability is exploitable at runtime, not just visible in source code. It should be linked to the SAST finding as a second evidence source. When the fix is applied, both the SAST re-scan and a targeted ZAP re-test should be in the closure criteria.

**Q2 — Contaminated staging from active scan:** Before running an active scan, snapshot the staging database. After the scan, restore the snapshot. Alternatively, use a separate staging database seeded with data that is expected to be dirtied and discarded after each scan. The process control is: active scan runs in an isolated environment that is reset after use.

**Q3 — ZAP cannot test JWT algorithm confusion:** This is a fundamental DAST limitation for cryptographic vulnerabilities. ZAP does not understand JWT semantics — it cannot craft a token with `alg=none` and a forged payload because it does not know what the JWT structure means. This class of vulnerability requires a tool that understands the protocol (a unit test with a crafted token, or a specialised JWT test tool), not a generic HTTP fuzzer. The Coverage Matrix must reflect this: TH-08 is covered by unit tests, not DAST.

---

*Back to the lab: [labs/lab-8.6.md](../labs/lab-8.6.md)*
