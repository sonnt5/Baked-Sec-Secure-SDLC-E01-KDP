# Solution 7.4 — XSS, CSRF & Browser Security Headers

> [!NOTE]
> **Reference Solution** — Work through the lab independently before reading this. Your approach may differ and still be correct.

---

## Key Insights

### XSS is context-dependent — not one rule

| Context | Why standard HTML escaping fails | Correct protection |
|---------|----------------------------------|-------------------|
| HTML text (`<div>{{ title }}</div>`) | HTML entity encoding works here — `<` becomes `&lt;` | Jinja2 auto-escaping (sufficient if enabled) |
| HTML attribute (`class="status-{{ value }}"`) | An attacker can close the attribute and inject: `" onmouseover="alert(1)` — Jinja2 auto-escaping handles this if `autoescape=True`, but only if the value is not marked `safe` | Jinja2 auto-escaping; never use `| safe` for user data |
| JavaScript context (`var score = {{ score }};`) | HTML entity encoding produces valid HTML but broken JavaScript. `&lt;` in a `<script>` block is not interpreted as `<` — but `json.dumps()` is not applied, so `</script>` in a string terminates the script tag | `json.dumps()` — not HTML encoding; `json.dumps()` produces a JavaScript literal that is safe in a script context |

Jinja2's `autoescape=True` handles HTML text and attribute contexts correctly. It does **not** handle JavaScript contexts — `{{ score | tojson }}` (which calls `json.dumps()`) is required there.

### CSRF and Bearer JWT

A CSRF attack works by inducing a victim's browser to make a request to the target site while the victim is authenticated. The browser automatically includes cookies with cross-origin requests — so any endpoint that relies on cookies for authentication is CSRF-vulnerable.

Bearer tokens are sent in the `Authorization` header. Browsers do not automatically include custom headers in cross-origin requests — a cross-origin script must explicitly set the header, which requires CORS to allow it. Since CODING WAR's CORS policy does not allow arbitrary origins to set the `Authorization` header, CSRF via Bearer JWT is not possible.

CSRF protection becomes necessary if CODING WAR ever adds an admin console that uses cookie-based sessions (for SSO or similar), or if it adds server-side rendered pages where form submissions authenticate via cookies.

### CSP nonce — why per-request

A nonce is only meaningful if an attacker cannot predict it. If the nonce is per-session, an attacker who can observe any response from the session (via XSS or network sniffing) learns the nonce for all future requests in that session — bypassing the CSP entirely. Per-request nonces provide no predictable surface to exploit.

### Cookie attribute purposes

| Attribute | Missing → enables |
|-----------|------------------|
| `HttpOnly` | `document.cookie` readable from JavaScript — XSS payload can exfiltrate the session cookie |
| `Secure` | Cookie sent over HTTP — passive network observer on university Wi-Fi reads the session token |
| `SameSite=Lax` | Cookie sent on cross-origin form submissions — CSRF against cookie-authenticated endpoints |

`SameSite=Strict` is not used for the login flow because it breaks navigation from external links: if a user clicks a link to CODING WAR from an email or another site, `Strict` causes the session cookie to be omitted on the first request, forcing a re-login. `Lax` allows the cookie on top-level navigations (link clicks) but blocks it on subresource requests.

---

*Back to the lab: [labs/lab-7.4.md](../labs/lab-7.4.md)*
