"""
Coffee Shop API - API Dependencies

FastAPI dependencies for authentication, authorization, and database access.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.services.user import UserService
from app.core.security import decode_token


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Dependency that extracts and validates the current user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header.
        db: Database session.
        
    Returns:
        The authenticated User object.
        
    Raises:
        HTTPException: If token is invalid or user not found (401 Unauthorized).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    # Verify this is an access token, not a refresh token
    if payload.get("type") != "access":
        raise credentials_exception
    
    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get_by_id(int(user_id))
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency that ensures the current user has admin privileges.
    
    Args:
        current_user: The authenticated user from get_current_user.
        
    Returns:
        The admin User object.
        
    Raises:
        HTTPException: If user is not an admin (403 Forbidden).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency that ensures the current user has verified their email.
    
    Args:
        current_user: The authenticated user from get_current_user.
        
    Returns:
        The verified User object.
        
    Raises:
        HTTPException: If user is not verified (403 Forbidden).
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]
CurrentVerifiedUser = Annotated[User, Depends(get_current_verified_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
