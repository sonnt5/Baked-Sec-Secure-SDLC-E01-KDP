# app/core/cookie_config.py — FIXED version
# Lab 7.4: Secure Session Cookie Configuration (ASVS V3.3)
#
# All three mandatory cookie security attributes are set:
#   HttpOnly — V3.3.2: prevents XSS-based cookie theft via document.cookie
#   Secure   — V3.3.1: HTTPS-only transmission
#   SameSite — V3.3.3: CSRF mitigation for same-site flows

from fastapi import Response

# ---------------------------------------------------------------------------
# Standard config — used for all session cookies in same-site flows
# ---------------------------------------------------------------------------
COOKIE_CONFIG: dict = {
    "httponly": True,        # V3.3.2: JS cannot access — blocks XSS token theft
    "secure":   True,        # V3.3.1: HTTPS only — never sent over plaintext HTTP
    "samesite": "lax",       # V3.3.3: Lax = CSRF protection for most state changes
                             # while still allowing navigation from external links.
                             # 'strict' would break shared login links.
    "path":     "/",
    "domain":   None,        # explicit None = host-only (no *.domain.com scope)
}

# ---------------------------------------------------------------------------
# Cross-site config — ONLY for OAuth/SSO flows that genuinely need cross-site
# ---------------------------------------------------------------------------
# SameSite=None requires Secure=True by browser policy.
CROSS_SITE_COOKIE_CONFIG: dict = {
    "httponly": True,
    "secure":   True,
    "samesite": "none",      # only when cross-site is explicitly required
    "path":     "/",
}


def set_session_cookie(response: Response, session_id: str) -> None:
    """Set a session cookie with all required security attributes.

    max_age (seconds) is preferred over Expires (UTC datetime) because
    max_age is clock-skew-resistant — the browser measures from receipt,
    not from an absolute UTC timestamp.
    ASVS V3.3 compliant.
    """
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=3600,   # 1 hour; adjust to match JWT access token TTL
        **COOKIE_CONFIG,
    )


# ---------------------------------------------------------------------------
# Anti-patterns — never do these
# ---------------------------------------------------------------------------
# response.set_cookie("session", value)             # No security attributes at all
# response.set_cookie(..., samesite="strict")       # Breaks login from external links
# response.set_cookie(..., httponly=False)           # XSS can steal the token
# response.set_cookie(..., secure=False)             # Sent over HTTP — interceptable
