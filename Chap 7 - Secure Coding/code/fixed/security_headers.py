# app/middleware/security_headers.py — FIXED version
# Lab 7.4: Security Headers Middleware (ASVS V3.4)
#
# Sets all required browser security headers on every response.
# A per-request nonce is generated for the Content-Security-Policy
# so that approved inline scripts can use it without 'unsafe-inline'.

import secrets

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach browser security headers to every HTTP response.

    ASVS V3.4 controls implemented:
      V3.4.1 — Content-Security-Policy (nonce-based, no unsafe-inline)
      V3.4.2 — Strict-Transport-Security (HSTS, 1 year, preload)
      V3.4.3 — X-Content-Type-Options: nosniff
      V3.4.4 — X-Frame-Options: DENY  (also covered by CSP frame-ancestors)
      V3.4.5 — Referrer-Policy: strict-origin-when-cross-origin
      Additional — Permissions-Policy (disable unneeded browser APIs)
    """

    async def dispatch(self, request: Request, call_next):
        # Generate a cryptographically random per-request nonce.
        # Templates reference this via request.state.csp_nonce.
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        response = await call_next(request)

        # V3.4.1 — CSP: nonce-based allowlist, no unsafe-inline
        response.headers["Content-Security-Policy"] = (
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none';"          # also prevents clickjacking
        )

        # V3.4.2 — HSTS: 1 year, all subdomains, preload list eligible
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # V3.4.3 — Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # V3.4.4 — Prevent clickjacking (belt-and-suspenders with CSP)
        response.headers["X-Frame-Options"] = "DENY"

        # V3.4.5 — Limit Referer header to origin only on cross-origin requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Additional — disable browser features CODING WAR never uses
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        return response
