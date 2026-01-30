"""
Coffee Shop API - Security Module

JWT token handling and password hashing utilities.
"""

from datetime import datetime, timedelta
from typing import Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify.
        hashed_password: The bcrypt-hashed password to compare against.
        
    Returns:
        True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password to hash.
        
    Returns:
        The bcrypt-hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The payload data to encode in the token.
        expires_delta: Optional custom expiration time.
        
    Returns:
        The encoded JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    return encoded_jwt


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: The payload data to encode in the token.
        expires_delta: Optional custom expiration time.
        
    Returns:
        The encoded JWT refresh token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token to decode.
        
    Returns:
        The decoded payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
