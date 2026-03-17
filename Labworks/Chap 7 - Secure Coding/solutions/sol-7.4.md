# Solution 7.4 — XSS, CSRF & Secure Cookies

> [!WARNING]
> **Reference Solution** — Complete the lab on your own before consulting this.

---

## Key Answers

**Jinja2 `{{ title }}` vs `{{ title | safe }}`:** Without `| safe`, Jinja2 with `autoescape=True` HTML-encodes the value — `<script>` becomes `&lt;script&gt;` and renders as text. With `| safe`, Jinja2 marks the value as already-safe HTML and renders it verbatim — any `<script>` tag in `title` executes. `| safe` is only acceptable when the value is produced by trusted server-side code (e.g., a Markdown→HTML renderer with a strict allowlist). Never use `| safe` on any value that contains or could contain user input.

**CSRF key insight:** *"Do I need CSRF tokens on the submission API?"* — No, because the submission API uses `Authorization: Bearer <JWT>`. The browser's Same-Origin Policy prevents cross-origin JavaScript from reading or setting the `Authorization` header. A malicious site cannot forge a request with a valid Bearer token it doesn't possess. CSRF protection becomes necessary if and only if CODING WAR switches to cookie-based session authentication for any endpoint, because cookies are automatically sent by the browser on cross-origin requests (subject to SameSite).

**Why `samesite="strict"` is not used:** `SameSite=Strict` prevents the cookie from being sent on ANY cross-site request, including navigation from an external link. If a user clicks a "login to CODING WAR" link from another site, they arrive at CODING WAR with no session cookie and must log in again even if they have a valid session. `SameSite=Lax` allows the cookie on top-level navigation (clicking a link) but blocks it on form submissions and XHR from other sites — this covers the CSRF cases that matter while preserving usable login-link behavior.

**Why nonce must be per-request:** If the nonce were per-session, an attacker who performs XSS once (before the session cookie is set) could capture the nonce and use it in all future requests within the session. Per-request nonces mean each page load has a fresh nonce — a captured nonce from one response is useless for the next request.

---

**Cookie attribute analysis:**

| Attribute | Attack prevented | If omitted |
|-----------|-----------------|-----------|
| `httponly=True` | XSS-based cookie theft via `document.cookie` — JavaScript cannot access the cookie | XSS payload can steal the session cookie and replay it from attacker's machine |
| `secure=True` | Network interception over HTTP — cookie only sent over HTTPS | Cookie sent over plaintext HTTP on non-HTTPS networks; MITM can steal it |
| `samesite="lax"` | CSRF — cross-site POST forms cannot automatically include the session cookie | Malicious site can embed a form that posts to `/submissions` with the victim's session cookie |

---

*Back to the lab: [labs/lab-7.4.md](../labs/lab-7.4.md)*
