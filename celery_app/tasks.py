"""
Coffee Shop API - Celery Tasks

Background tasks for user management, including automatic cleanup of unverified users.
"""

import os
import asyncio
from sqlalchemy import create_engine, select, delete, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from celery_app.celery import celery


# Sync database URL (Celery uses sync operations)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://coffee_shop:coffee_shop@db:5432/coffee_shop"
)

# Convert async URL to sync URL for Celery
SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")


@celery.task(name="celery_app.tasks.cleanup_unverified_users")
def cleanup_unverified_users():
    """
    Periodic task that runs hourly to remove unverified users older than 2 days.
    
    NOTE: This uses synchronous SQLAlchemy because Celery workers don't natively support asyncio (The code inside each task runs line-by-line (no await)). 
    In a more complex setup, we can use celery-aio-pool or run async code with asyncio.run().
    """
    
    # Create sync engine for Celery
    engine = create_engine(SYNC_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    
    # Calculate cutoff date (2 days ago)
    cutoff_date = datetime.utcnow() - timedelta(days=2)
    
    try:
        with Session() as session:
            # Count users to be deleted
            unverified_count = session.execute(
                text("""
                    SELECT COUNT(*) FROM users 
                    WHERE is_verified = false AND created_at < :cutoff
                """),
                {"cutoff": cutoff_date}
            )
            count = unverified_count.scalar()
            
            if count > 0:
                # Delete unverified users older than 2 days
                session.execute(
                    text("""
                        DELETE FROM users 
                        WHERE is_verified = false AND created_at < :cutoff
                    """),
                    {"cutoff": cutoff_date}
                )
                session.commit()
                
                print(f"[Cleanup Task] Deleted {count} unverified users older than 2 days")
            else:
                print("[Cleanup Task] No unverified users to delete")
            
            return {
                "status": "success",
                "deleted_count": count,
                "cutoff_date": cutoff_date.isoformat(),
            }
            
    except Exception as e:
        print(f"[Cleanup Task] Error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
        }
