# app/middleware/security_headers.py — VULNERABLE version
# Lab 7.4: Missing Browser Security Headers (ASVS V3.4)
# DO NOT USE IN PRODUCTION — educational purposes only
#
# Bug demonstrated:
#   No security headers set on HTTP responses.
#   The application is vulnerable to:
#     - XSS via inline script injection (no CSP)
#     - Clickjacking (no X-Frame-Options)
#     - MIME sniffing attacks (no X-Content-Type-Options)
#     - HTTPS downgrade attacks (no HSTS)
#     - Referer leakage (no Referrer-Policy)

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class NoSecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that does nothing — no security headers are set.

    BUG (ASVS V3.4):
      This middleware exists as a placeholder but sets no browser security
      headers on any response. As a result:

      - CSP is absent: any injected <script> tag executes freely.
        A stored XSS in a problem title would run as the victim's origin.

      - X-Frame-Options is absent: the application can be embedded in an
        <iframe> on an attacker's site, enabling clickjacking attacks against
        the scoreboard or admin console.

      - X-Content-Type-Options is absent: a browser may MIME-sniff a
        response with Content-Type: text/plain and execute it as JavaScript.

      - HSTS is absent: a network attacker can strip HTTPS and downgrade
        the connection to HTTP, exposing session cookies and credentials.

      - Referrer-Policy is absent: submission IDs, contest URLs, and user
        profile paths are sent as the Referer header to any external resource
        (analytics, CDN scripts), leaking internal application structure.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # BUG: no security headers are added to the response
        return response
