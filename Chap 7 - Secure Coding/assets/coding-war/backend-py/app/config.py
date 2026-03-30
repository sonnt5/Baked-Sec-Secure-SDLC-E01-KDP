"""
Application Configuration
Validates environment variables using Pydantic Settings.
Equivalent to: backend/src/utils/env.ts
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Coding War API"
    app_version: str = "1.0.0"
    debug: bool = False
    port: int = 3000
    environment: str = Field(default="development", alias="NODE_ENV")
    cors_origin: str = "http://localhost:5173,http://localhost:5174"
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/coding_war"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None

    # Authentication
    jwt_secret: str = "default-secret-change-in-production"
    jwt_refresh_secret: str = "default-refresh-secret-change-in-production"
    access_token_expiry_minutes: int = 7 * 24 * 60  # 7 days
    refresh_token_expiry_minutes: int = 30 * 24 * 60  # 30 days

    # Email
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    email_from: str = "noreply@codingwar.dev"
    email_verification_expiry_hours: int = 24
    password_reset_expiry_hours: int = 1

    # S3 / MinIO
    s3_endpoint: str = "http://localhost:9000"
    s3_region: str = "us-east-1"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_bucket_name: str = "coding-war-testcases"
    s3_presigned_url_expiry: int = 300  # seconds

    # Judge System
    judge_concurrency: int = 3
    judge_timeout: int = 30000  # ms
    judge_hmac_secret: str | None = None  # For distributed judge (ADR-002)

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origin.split(",")]

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"
        return f"redis://{self.redis_host}:{self.redis_port}"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton settings instance
settings = Settings()
