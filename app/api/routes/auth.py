"""
Coffee Shop API - Authentication Routes

API endpoints for user authentication: signup, login, token refresh, and email verification.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    VerifyRequest,
)
from app.schemas.user import UserResponse
from app.services.user import UserService
from app.services.verification import VerificationService
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,

    summary="Register a new user",
    description="""
    Register a new user account with email and password.
    
    After successful registration:
    - A verification code is generated and printed to the console (demo mode)
    - The user account is created with 'is_verified=false' status
    - User must verify their email using the /auth/verify endpoint
    
    **Note**: In production, the verification code would be sent via email/SMS.
    """
)
async def signup(request: SignupRequest, 
                db: AsyncSession = Depends(get_db)) -> UserResponse:
    """Register a new user and send verification code."""
    user_service = UserService(db)
    
    # Check if email already exists
    existing_user = await user_service.get_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate verification code
    verification_code = VerificationService.generate_code()
    
    # Create user
    user = await user_service.create(
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
        verification_code=verification_code,
    )
    
    # Send verification email (prints to console in demo mode)
    VerificationService.send_verification_email(request.email, verification_code)
    
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and get tokens",
    description="""
    Authenticate a user with email and password.
    
    Returns:
    - **access_token**: JWT token for API authorization (expires in 15 minutes)
    - **refresh_token**: JWT token for obtaining new access tokens (expires in 7 days)
    
    Use the access token in the Authorization header: `Bearer <access_token>`
    """
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    user_service = UserService(db)
    
    # Find user by email
    user = await user_service.get_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse,
    summary="Refresh access token",
    description="""
    Exchange a valid refresh token for a new pair of access and refresh tokens.
    
    Use this endpoint when the access token has expired.
    The refresh token must be valid and not expired.
    """
)
async def refresh_token(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token using refresh token."""
    # Decode and validate refresh token
    payload = decode_token(request.refresh_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify this is a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify user still exists
    user_service = UserService(db)
    user = await user_service.get_by_id(int(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new tokens
    # Rotate refresh token as well for security
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.post("/verify", response_model=UserResponse,
    summary="Verify user email",
    description="""
    Verify user's email address using the verification code.
    
    The verification code was provided during registration (printed to console in demo mode).
    After successful verification, the user's 'is_verified' status is set to true.
    """
)
async def verify_email(
    request: VerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Verify user email with verification code."""
    user_service = UserService(db)
    
    # Find user by email
    user = await user_service.get_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Validate verification code
    if not VerificationService.validate_code(user.verification_code, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Mark user as verified
    user = await user_service.verify(user)
    
    return UserResponse.model_validate(user)
