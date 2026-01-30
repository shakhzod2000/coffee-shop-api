"""
Coffee Shop API - Roles Module

Role-based access control utilities and dependencies.
"""

from fastapi import HTTPException, status

from app.models.user import User, UserRole


def require_admin(current_user: User) -> User:
    """
    Verify that the current user has admin privileges.
    
    Args:
        current_user: The authenticated user.
        
    Returns:
        The user if they are an admin.
        
    Raises:
        HTTPException: If the user is not an admin (403 Forbidden).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def require_verified(current_user: User) -> User:
    """
    Verify that the current user has verified their email.
    
    Args:
        current_user: The authenticated user.
        
    Returns:
        The user if they are verified.
        
    Raises:
        HTTPException: If the user is not verified (403 Forbidden).
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user


def can_modify_user(current_user: User, target_user_id: int) -> bool:
    """
    Check if the current user can modify the target user.
    
    Admin users can modify any user. Regular users can only modify themselves.
    
    Args:
        current_user: The authenticated user.
        target_user_id: The ID of the user to be modified.
        
    Returns:
        True if modification is allowed, False otherwise.
    """
    if current_user.role == UserRole.ADMIN:
        return True
    return current_user.id == target_user_id
