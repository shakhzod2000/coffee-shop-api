"""
Coffee Shop API - User Schemas

Pydantic schemas for user-related request/response validation.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.user import UserRole


class UserResponse(BaseModel):
    """User data returned from API endpoints."""
    
    id: int
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    is_verified: bool
    role: UserRole
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """User update schema for PATCH requests. All fields optional."""
    
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None


class UserListResponse(BaseModel):
    """Paginated list of users."""
    
    users: list[UserResponse]
    total: int
