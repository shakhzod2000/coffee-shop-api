"""
Coffee Shop API - Authentication Schemas

Pydantic schemas for authentication-related request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """User registration request schema."""
    
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters"
    )
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)


class LoginRequest(BaseModel):
    """User login request schema."""
    
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema after successful authentication."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Token refresh request schema."""
    
    refresh_token: str


class VerifyRequest(BaseModel):
    """Email verification request schema."""
    
    email: EmailStr
    code: str = Field(
        ..., min_length=6, max_length=6, description="6-digit verification code"
    )
