"""
Auth Pydantic Schemas
Equivalent to: Zod schemas in backend/src/utils/schemas.ts (auth section)
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "Bearer"
    user: "UserBrief"


class UserBrief(BaseModel):
    id: str
    username: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    refreshToken: str


class VerifyEmailRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str
