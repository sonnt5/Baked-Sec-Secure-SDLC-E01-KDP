"""
Security Headers Middleware
Equivalent to: helmet() in backend/src/index.ts
Gap Fix: CSP per-request nonce + HSTS preload
Pattern from: assets/code/fixed/security_headers.py (ASVS V3.4)
"""

import secrets

from app.config import settings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Paths that need relaxed CSP for Swagger UI
_DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Set security headers on every response.
    ASVS V3.4 controls:
      V3.4.1 — CSP (nonce-based per request, no unsafe-inline)
      V3.4.2 — HSTS (1 year, includeSubDomains, preload)
      V3.4.3 — X-Content-Type-Options: nosniff
      V3.4.4 — X-Frame-Options: DENY
      V3.4.5 — Referrer-Policy
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate a unique nonce for this request (ASVS V3.4.1)
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        response = await call_next(request)

        # HSTS — 1 year, includeSubDomains, preload (ASVS V3.4.2)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # MIME sniffing prevention (ASVS V3.4.3)
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Clickjacking prevention (ASVS V3.4.4)
        response.headers["X-Frame-Options"] = "DENY"

        # Referrer control (ASVS V3.4.5)
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy — disable unneeded browser APIs
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # Content Security Policy
        if request.url.path in _DOCS_PATHS and settings.environment != "production":
            # Relaxed CSP for Swagger UI in development (CDN + inline scripts)
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "connect-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "frame-ancestors 'none'"
            )
        else:
            # Strict nonce-based CSP for all API responses (ASVS V3.4.1)
            response.headers["Content-Security-Policy"] = (
                f"default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}'; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'"
            )

        # Remove server identification header
        if "server" in response.headers:
            del response.headers["server"]

        return response
