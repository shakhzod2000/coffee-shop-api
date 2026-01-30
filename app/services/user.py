"""
Coffee Shop API - User Service

Business logic for user operations (CRUD).
"""

from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash


class UserService:
    """Service class for user-related database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> User | None:
        """Get a user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit).order_by(User.id)
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Get total count of users."""
        result = await self.db.execute(select(func.count(User.id)))
        return result.scalar_one()
    
    async def create(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        verification_code: str | None = None,
    ) -> User:
        """Create a new user with hashed password."""
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            verification_code=verification_code,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def update(
        self,
        user: User,
        first_name: str | None = None,
        last_name: str | None = None,
        password: str | None = None,
    ) -> User:
        """Update user fields. Only non-None values are updated."""
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if password is not None:
            user.hashed_password = get_password_hash(password)
        
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def verify(self, user: User) -> User:
        """Mark user as verified and clear verification code."""
        user.is_verified = True
        user.verification_code = None
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user: User) -> None:
        """Delete a user."""
        await self.db.delete(user)
        await self.db.flush()
    
    async def delete_unverified_older_than(self, days: int) -> int:
        """Delete unverified users older than specified days. Returns count."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(User).where(
                User.is_verified == False,
                User.created_at < cutoff_date
            )
        )
        users_to_delete = result.scalars().all()
        count = len(list(users_to_delete))
        
        for user in users_to_delete:
            await self.db.delete(user)
        
        await self.db.flush()
        return count
