"""
Coffee Shop API - Main Application

FastAPI application entry point with route configuration and startup events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import create_tables
from app.api.routes import auth_router, users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Creates database tables
    - Shutdown: Cleanup (if needed)
    """
    # Startup
    await create_tables()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Coffee Shop API",
    description="User management API with authentication, authorization, and email verification.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# Include routers
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/",
    summary="Health check",
    description="Simple health check endpoint to verify the API is running.",
    tags=["Health"]
)
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Coffee Shop API is running"}


@app.get("/health",
    summary="Detailed health check",
    description="Returns detailed health status of the API.",
    tags=["Health"]
)
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Coffee Shop API",
    }
