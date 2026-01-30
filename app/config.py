"""
Coffee Shop API - Configuration Module

Application settings loaded from environment variables using Pydantic Settings.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Database
    database_url: str = "postgresql+asyncpg://coffee_shop:coffee_shop@db:5432/coffee_shop"
    
    # JWT Settings
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Redis (for Celery)
    redis_url: str = "redis://redis:6379/0"
    
    # Verification settings
    verification_code_expire_hours: int = 24
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
