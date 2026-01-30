"""
Coffee Shop API - User Management Routes

API endpoints for user management: profile, listing, updating, and deleting users.
"""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, CurrentAdminUser, DbSession
from app.schemas.user import UserResponse, UserUpdate, UserListResponse
from app.services.user import UserService
from app.core.roles import can_modify_user


router = APIRouter(tags=["Users"])


@router.get("/me", response_model=UserResponse,
    summary="Get current user profile",
    description="""
    Get the profile information of the currently authenticated user.
    
    Requires a valid access token in the Authorization header.
    """
)
async def get_current_user(curr_user: CurrentUser) -> UserResponse:
    """Get current authenticated user."""
    return UserResponse.model_validate(curr_user)


@router.get("/users", response_model=UserListResponse,
    summary="List all users (Admin only)",
    description="""
    Get a paginated list of all users in the system.
    
    **Access**: Admin users only.
    
    Query parameters:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
)
async def list_users(
    current_user: CurrentAdminUser,
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
) -> UserListResponse:
    """List all users (admin only)."""
    user_service = UserService(db)
    
    users = await user_service.get_all(skip=skip, limit=limit)
    total = await user_service.count()
    
    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
    )


@router.get("/users/{user_id}", response_model=UserResponse,
    summary="Get user by ID (Admin only)",
    description="""
    Get detailed information about a specific user by their ID.
    
    **Access**: Admin users only.
    """
)
async def get_user_by_id(
    user_id: int,
    curr_user: CurrentAdminUser,
    db: DbSession,
) -> UserResponse:
    """Get a specific user by ID (admin only)."""
    user_service = UserService(db)
    
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserResponse,
    summary="Update user profile",
    description="""
    Partially update a user's profile information.
    
    **Access**: 
    - Users can update their own profile
    - Admins can update any user's profile
    
    Only provided fields will be updated. Available fields:
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **password**: New password (will be hashed)
    """
)
async def update_user(
    user_id: int,
    request: UserUpdate,
    curr_user: CurrentUser,
    db: DbSession,
) -> UserResponse:
    """Update a user's profile (owner or admin)."""
    # Check authorization
    if not can_modify_user(curr_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this user"
        )
    
    user_service = UserService(db)
    
    # Get user to update
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user
    updated_user = await user_service.update(
        user=user,
        first_name=request.first_name,
        last_name=request.last_name,
        password=request.password,
    )
    
    return UserResponse.model_validate(updated_user)


@router.delete("/users/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (Admin only)",
    description="""
    Delete a user from the system.
    
    **Access**: Admin users only.
    
    **Warning**: This action is irreversible.
    """
)
async def delete_user(
    user_id: int,
    curr_user: CurrentAdminUser,
    db: DbSession,
) -> None:
    """Delete a user (admin only)."""
    user_service = UserService(db)
    
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == curr_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    await user_service.delete(user)
