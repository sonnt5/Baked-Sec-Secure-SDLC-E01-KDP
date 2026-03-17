# Lab 7.4 — Web-Specific Issues: XSS, CSRF & Secure Cookies

> **Chapter 7 · Secure Coding Foundations · OWASP ASVS v5.0.0 Aligned**
> Input: Auth + Scoreboard endpoints | Output: Secure Web Code + ASVS V3 Assessment

> [!NOTE]
> **OWASP ASVS v5.0.0:** V3.2 Unintended Content Interpretation (XSS prevention), V3.3 Cookie Setup (HttpOnly/Secure/SameSite), V3.4 Browser Security Mechanism Headers (CSP, HSTS, X-Content-Type-Options), V3.5 Browser Origin Separation (CSRF, CORS).

## Learning Objectives

- Understand 3 XSS output contexts (HTML text, HTML attribute, JavaScript) and their different encoding rules.
- Design CSRF protection for CODING WAR — CSRF tokens vs SameSite cookies.
- Configure secure session cookies per ASVS V3.3.
- Design security headers per ASVS V3.4.

---

## Task 1 — XSS Context Analysis

XSS is not a single vulnerability type — the context determines the encoding rule. Analyze 3 output contexts in CODING WAR:

| Context | CODING WAR Example | What Attacker Can Inject | Required Protection | ASVS + Implementation |
|---------|-------------------|-------------------------|--------------------|-----------------------|
| **HTML Text Context** | Problem statement rendered: `<div>{{problem.title}}</div>` | `<script>steal()</script>` — becomes executable if not HTML-encoded | HTML entity encoding: `<` → `&lt;` `>` → `&gt;` `&` → `&amp;` `"` → `&quot;` `'` → `&#x27;` | ASVS V1.2.1 + V3.2: Jinja2 with `autoescape=True` (default in HTML templates). NEVER use `|safe` filter on user content. |
| **HTML Attribute Context** | Submission status: `<span class="status-{{status.value}}">` | Close the attribute and inject new ones: `admin data-role="admin"`. Even in attribute context, can inject event handlers if no quotes. | HTML attribute encoding (encode more chars than HTML text); always quote attributes: `class="{{var}}"` not `class={{var}}` | ASVS V1.2.1: always use quoted attributes in templates. Jinja2 autoescape handles this. |
| **JavaScript Context** | Inline score in JS: `<script>var score = {{user.score}};</script>` | `0; alert(1); //` — attacker closes JS statement and injects code | JSON encoding for JavaScript context: `json.dumps()` not `str()`. NEVER use `f'var x = {value}'` in script tags. | ASVS V1.2.3: use `json.dumps()` for all values in JS context. Prefer data-attributes + JavaScript parsing over inline JS. |

Study [`code/fixed/security_headers.py`](../code/fixed/security_headers.py) — the CSP nonce implementation prevents inline script injection at the browser level.

**Exercise:** In Jinja2, what is the difference between `{{ problem.title }}` and `{{ problem.title | safe }}`? When would `| safe` be acceptable, and when is it dangerous?

---

## Task 2 — CSRF Protection Design

CODING WAR is API-first (FastAPI + JSON) with a separate frontend. Analyze the CSRF threat and design protection:

| Design Element | CODING WAR CSRF Protection Design |
|---------------|----------------------------------|
| **Threat Assessment** | CODING WAR state-changing endpoints: `POST /submissions`, `POST /contests/{id}/register`, `POST /admin/*`. Current design: JWT in `Authorization` header — Bearer tokens are NOT automatically sent by browsers (unlike cookies), so standard CSRF is NOT applicable for API endpoints using Bearer JWT. |
| **When CSRF IS applicable** | If CODING WAR has ANY browser-cookie-based session (e.g., for the admin console web UI), those endpoints need CSRF protection. Password reset flows using cookie-based sessions also need CSRF tokens. |
| **Primary Defense (API)** | Use `Authorization: Bearer <JWT>` header instead of cookie-based auth for API calls. Browsers cannot forge `Authorization` headers in cross-site requests — this is inherent CSRF protection for APIs. ASVS V3.5.1. |
| **SameSite Cookie Policy** | If session cookies are used (admin console): `SameSite=Lax` (default, prevents CSRF for most state-changing requests). `SameSite=None; Secure` only for cross-site SSO flows. `SameSite=Strict` is too restrictive (breaks link-clicking from external pages). ASVS V3.3.1. |
| **CSRF Token (if cookies used)** | FastAPI CSRF middleware: generate token per-session, embed in forms, validate on POST/PUT/DELETE. Use `secrets.token_urlsafe(32)` for token generation. Store in server-side session (not cookie) to prevent browser-side access. |

**Key insight to document:** A developer asks "do I need to add CSRF tokens to the CODING WAR submission API?" Write a 2-3 sentence answer explaining why the current Bearer JWT design is inherently CSRF-safe, and under what specific condition CSRF protection would become necessary.

---

## Task 3 — Secure Cookie Configuration (ASVS V3.3)

Study [`code/fixed/cookie_config.py`](../code/fixed/cookie_config.py).

For each of the three mandatory attributes, explain:

| Attribute | Value in CODING WAR | What attack does it prevent? | What breaks if you omit it? |
|-----------|--------------------|-----------------------------|----------------------------|
| `httponly=True` | | | |
| `secure=True` | | | |
| `samesite="lax"` | | | |

Also answer: Why is `samesite="strict"` not used even though it is "more secure"?

---

## Task 4 — Security Headers Design (ASVS V3.4)

Study [`code/fixed/security_headers.py`](../code/fixed/security_headers.py).

Complete the analysis table for each header:

| Header | Value in CODING WAR | ASVS Control | Attack Prevented |
|--------|--------------------|--------------|--------------------|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' 'nonce-{nonce}'; ...` | V3.4.1 | XSS: prevents inline script execution, restricts script sources. `frame-ancestors 'none'` also prevents clickjacking. |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | V3.4.2 | |
| `X-Content-Type-Options` | `nosniff` | V3.4.3 | |
| `X-Frame-Options` | `DENY` | V3.4.4 | |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | V3.4.5 | |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=()` | V3.4 additional | |

**Exercise:** The middleware generates a fresh `nonce` per request using `secrets.token_urlsafe(16)`. Why must this nonce be per-request rather than per-session or static?

---

## Task 5 — ASVS V3 Assessment

| ASVS ID | Control | Status | Evidence |
|---------|---------|--------|---------|
| **3.2.1** | HTML response includes X-Content-Type-Options: nosniff | Yes | `SecurityHeadersMiddleware` sets nosniff. Test: verify header present on all HTML responses. |
| **3.2.2** | Content rendered by the browser cannot be controlled by attacker (CSP) | Partial | CSP implemented with nonce. Gap: audit for `eval()` usage, inline event handlers in legacy templates. |
| **3.3.1** | Session cookies have Secure attribute | Yes | `COOKIE_CONFIG` sets `secure=True`. |
| **3.3.2** | Session cookies have HttpOnly attribute | Yes | `COOKIE_CONFIG` sets `httponly=True`. |
| **3.3.3** | Session cookies use SameSite attribute | Yes | `COOKIE_CONFIG` sets `samesite='lax'`. |
| **3.4.1** | CSP header defined; blocks inline script execution without nonce/hash | Partial | CSP with nonce implemented. Gap: need CSP violation reporting endpoint. |
| **3.4.2** | HSTS header present for HTTPS | Yes | HSTS: `max-age=31536000; includeSubDomains`. |
| **3.5.1** | CSRF defenses implemented (SameSite and/or CSRF tokens) | Yes (API) | API: Bearer JWT in Authorization header — inherently CSRF-safe. Cookie-based flows: SameSite=Lax. |
| **3.6.1** | External JavaScript loaded with SRI hash integrity attribute | Partial | No external JS currently. If added: must use `integrity=sha384-...` attribute. |

---

## Grading Criteria

| Criterion | Points | Description |
|-----------|--------|-------------|
| XSS Context Analysis (3 contexts) | **25** | Each context: attack vector specific (3 pts), encoding rule correct (3 pts), code example implements correctly (4 pts) |
| CSRF Protection Design | **20** | Correctly identifies Bearer JWT as inherent CSRF protection (5 pts); SameSite analysis accurate (5 pts); admin console case addressed (10 pts) |
| Secure Cookie Configuration analysis | **20** | All 3 attributes explained with attack prevented; reasoning for `samesite='lax'`; cross-site exception noted |
| Security Headers analysis | **20** | All 6 headers with attack prevented; nonce-per-request reasoning explained |
| ASVS V3 Assessment | **15** | Honest Partial assessments with gaps; no unjustified "Yes" entries; test conditions specified |
| **Total** | **100** | |

---

*See the reference solution at [solutions/sol-7.4.md](../solutions/sol-7.4.md)*
