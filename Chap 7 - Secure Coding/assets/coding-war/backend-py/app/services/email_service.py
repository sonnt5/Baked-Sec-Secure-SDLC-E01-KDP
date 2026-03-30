"""
Email Service
Equivalent to: backend/src/services/emailService.ts
"""

from email.message import EmailMessage

import aiosmtplib

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("email_service")


async def send_email(*, to: str, subject: str, html_body: str) -> None:
    """Send an email via SMTP."""
    msg = EmailMessage()
    msg["From"] = settings.email_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(html_body, subtype="html")

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_pass or None,
            use_tls=settings.smtp_port == 465,
            start_tls=settings.smtp_port == 587,
        )
        logger.info("Email sent", to=to, subject=subject)
    except Exception as e:
        logger.error("Failed to send email", to=to, error=str(e))
        # Don't fail the request — email is async/best-effort


async def send_verification_email(email: str, token: str) -> None:
    """Send email verification link."""
    verify_url = f"{settings.cors_origins[0]}/verify-email?token={token}"
    html = f"""
    <h2>Verify Your Email</h2>
    <p>Click the link below to verify your email address:</p>
    <a href="{verify_url}">Verify Email</a>
    <p>This link expires in {settings.email_verification_expiry_hours} hours.</p>
    """
    await send_email(to=email, subject="Verify your Coding War account", html_body=html)


async def send_password_reset_email(email: str, token: str) -> None:
    """Send password reset link."""
    reset_url = f"{settings.cors_origins[0]}/reset-password?token={token}"
    html = f"""
    <h2>Reset Your Password</h2>
    <p>Click the link below to reset your password:</p>
    <a href="{reset_url}">Reset Password</a>
    <p>This link expires in {settings.password_reset_expiry_hours} hour(s).</p>
    """
    await send_email(to=email, subject="Reset your Coding War password", html_body=html)
