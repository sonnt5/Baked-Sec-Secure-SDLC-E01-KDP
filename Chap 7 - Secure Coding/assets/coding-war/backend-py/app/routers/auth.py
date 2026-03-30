"""
Auth Router
Equivalent to: backend/src/routes/auth.routes.ts
6 endpoints: register, verify-email, login, refresh, forgot-password, reset-password
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.middleware.error_handler import AppError
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserBrief,
    VerifyEmailRequest,
)
from app.services.auth_service import (
    generate_access_token,
    generate_email_verification_token,
    generate_password_reset_token,
    generate_refresh_token,
    hash_password,
    needs_rehash,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)
from app.services.token_revocation_service import is_token_revoked, revoke_refresh_token
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("auth_router")


@router.post("/register", response_model=MessageResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """User registration with email verification."""
    # Check existing user
    existing = await db.execute(
        select(User).where((User.email == data.email) | (User.username == data.username))
    )
    if existing.scalar_one_or_none():
        raise AppError(409, "CONFLICT", "Email or username already exists")

    # Create user
    token, expiry = generate_email_verification_token()
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        email_verify_token=token,
        email_verify_expiry=expiry,
    )
    db.add(user)
    await db.flush()

    logger.info("User registered", user_id=str(user.id), username=user.username)
    # TODO: Send verification email via email service
    return MessageResponse(message="Registration successful. Please verify your email.")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(data: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    """Verify user email with token."""
    result = await db.execute(
        select(User).where(User.email_verify_token == data.token)
    )
    user = result.scalar_one_or_none()

    if not user or not user.email_verify_expiry or user.email_verify_expiry < datetime.now(timezone.utc):
        raise AppError(400, "INVALID_TOKEN", "Invalid or expired verification token")

    user.is_email_verified = True
    user.email_verify_token = None
    user.email_verify_expiry = None

    return MessageResponse(message="Email verified successfully")


# Dummy hash used when user doesn't exist — prevents timing-based email enumeration.
# Running verify_password against this ensures both code paths take the same time.
# Pattern from assets/code/fixed/error_handlers.py (ASVS V6.3.3)
_DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$dummysaltdummysalt$dummyhashplaceholder000000000000"


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """User login with JWT."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # Always run password verification — use dummy hash if user not found
    # This prevents timing attacks that could enumerate valid email addresses
    hash_to_check = user.password_hash if user else _DUMMY_HASH
    password_ok = verify_password(data.password, hash_to_check)

    if not user or not password_ok:
        raise AppError(401, "INVALID_CREDENTIALS", "Invalid email or password")

    # Rehash legacy bcrypt passwords to Argon2id
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(data.password)
        logger.info("Rehashed legacy password", user_id=str(user.id))

    access_token = generate_access_token(str(user.id), user.role.value)
    refresh_token, _ = generate_refresh_token(str(user.id))  # jti stored inside token

    return TokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        user=UserBrief(
            id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role.value,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token. Checks revocation blocklist before issuing new tokens."""
    payload = verify_refresh_token(data.refresh_token)
    if not payload:
        raise AppError(401, "INVALID_TOKEN", "Invalid or expired refresh token")

    # Gap fix #4: Check if this refresh token has been revoked (e.g. via logout)
    jti = payload.get("jti", "")
    if jti and await is_token_revoked(jti):
        raise AppError(401, "TOKEN_REVOKED", "Refresh token has been revoked")

    user_id = payload["userId"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise AppError(401, "USER_NOT_FOUND", "User not found")

    new_access = generate_access_token(str(user.id), user.role.value)
    new_refresh, _ = generate_refresh_token(str(user.id))

    return TokenResponse(
        accessToken=new_access,
        refreshToken=new_refresh,
        user=UserBrief(
            id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role.value,
        ),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(data: RefreshRequest):
    """
    Logout: revoke the provided refresh token.
    Gap fix #4: Revoked JTIs are stored in Redis until the token's natural expiry.
    Access tokens remain valid until they expire (short TTL handles this).
    """
    payload = verify_refresh_token(data.refresh_token)
    if payload and payload.get("jti") and payload.get("exp"):
        from datetime import datetime, timezone as _tz
        ttl = max(0, int(payload["exp"] - datetime.now(_tz.utc).timestamp()))
        await revoke_refresh_token(payload["jti"], ttl)
    # Always return success — don't reveal whether the token was valid
    return MessageResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Request password reset."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if user:
        token, expiry = generate_password_reset_token()
        user.password_reset_token = token
        user.password_reset_expiry = expiry
        # TODO: Send reset email via email service

    return MessageResponse(message="If the email exists, a password reset link has been sent.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password with token."""
    result = await db.execute(
        select(User).where(User.password_reset_token == data.token)
    )
    user = result.scalar_one_or_none()

    if not user or not user.password_reset_expiry or user.password_reset_expiry < datetime.now(timezone.utc):
        raise AppError(400, "INVALID_TOKEN", "Invalid or expired reset token")

    user.password_hash = hash_password(data.new_password)
    user.password_reset_token = None
    user.password_reset_expiry = None

    return MessageResponse(message="Password reset successfully")
