"""
Coffee Shop API - User Model

SQLAlchemy model for the User entity with role-based access control.
"""

import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration for access control."""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """User model for registered users with role-based access control."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False)
    
    first_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True)
    
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    verification_code: Mapped[str | None] = mapped_column(
        String(6), nullable=True)
    
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
