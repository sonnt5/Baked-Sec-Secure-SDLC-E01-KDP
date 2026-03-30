"""
Authentication Service
Equivalent to: backend/src/services/authService.ts
SDRD: SDD 5.1 (Argon2id password hashing)
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import argon2
import bcrypt
from jose import jwt, JWTError

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("auth_service")

# Argon2id configuration per SDD spec (memory=64MB, iterations=3, parallelism=4)
_argon2_hasher = argon2.PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MB
    parallelism=4,
    type=argon2.Type.ID,
)


# ──────────────────────────── Password Hashing ────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password using Argon2id (SDD 5.1 spec)."""
    return _argon2_hasher.hash(password)


def _is_bcrypt_hash(hashed: str) -> bool:
    """Check if a password hash is a legacy bcrypt hash."""
    return hashed.startswith(("$2b$", "$2a$", "$2y$"))


def needs_rehash(hashed: str) -> bool:
    """Check if a hash needs to be re-hashed with Argon2id."""
    return _is_bcrypt_hash(hashed)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a hash.
    Supports both Argon2id (new) and bcrypt (legacy) for backward compatibility.
    """
    try:
        if _is_bcrypt_hash(hashed):
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        return _argon2_hasher.verify(hashed, password)
    except (argon2.exceptions.VerifyMismatchError, argon2.exceptions.VerificationError, ValueError):
        return False


# ──────────────────────────── JWT Tokens ────────────────────────────

def generate_access_token(user_id: str, role: str) -> str:
    """Generate an access token (JWT) with configurable expiration."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expiry_minutes
    )
    payload = {
        "userId": user_id,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def generate_refresh_token(user_id: str) -> tuple[str, str]:
    """Generate a refresh token (JWT) with longer expiration. Returns (token, jti)."""
    import uuid as _uuid
    jti = str(_uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.refresh_token_expiry_minutes
    )
    payload = {
        "userId": user_id,
        "jti": jti,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_refresh_secret, algorithm="HS256"), jti


def verify_access_token(token: str) -> dict | None:
    """Verify and decode an access token. Returns payload or None."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return {"userId": payload["userId"], "role": payload["role"]}
    except JWTError:
        return None


def verify_refresh_token(token: str) -> dict | None:
    """Verify and decode a refresh token. Returns payload (with jti) or None."""
    try:
        payload = jwt.decode(token, settings.jwt_refresh_secret, algorithms=["HS256"])
        return {"userId": payload["userId"], "jti": payload.get("jti", ""), "exp": payload.get("exp")}
    except JWTError:
        return None


# ──────────────────────────── Verification Tokens ────────────────────────────

def generate_email_verification_token() -> tuple[str, datetime]:
    """Generate an email verification token with 24-hour expiration."""
    token = str(uuid4())
    expiry = datetime.now(timezone.utc) + timedelta(
        hours=settings.email_verification_expiry_hours
    )
    return token, expiry


def generate_password_reset_token() -> tuple[str, datetime]:
    """Generate a password reset token with 1-hour expiration."""
    token = str(uuid4())
    expiry = datetime.now(timezone.utc) + timedelta(
        hours=settings.password_reset_expiry_hours
    )
    return token, expiry
