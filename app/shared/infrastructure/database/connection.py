# 📄 File: app/shared/infrastructure/database/connection.py
#
# 🧭 Purpose (Layman Explanation):
# Sets up the connection to our database so the plant care app can save and retrieve
# information about users, plants, and care schedules.
#
# 🧪 Purpose (Technical Summary):
# Database connection management with SQLAlchemy async engine, session handling,
# and connection pooling for PostgreSQL via Supabase.
#
# 🔗 Dependencies:
# - sqlalchemy (ORM and database toolkit)
# - asyncpg (PostgreSQL async driver)
# - app.shared.config.settings (database configuration)
#
# 🔄 Connected Modules / Calls From:
# - app.main (database initialization during startup)
# - All repository implementations (database operations)
# - Database migration scripts (schema management)

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.shared.config.settings import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Database base class for models
Base = declarative_base()

# Global database engine and session maker
engine = None
async_session_maker = None


async def init_database() -> None:
    """
    Initialize database connection and session maker.
    
    Creates async engine with proper connection pooling
    and configures session factory for dependency injection.
    """
    global engine, async_session_maker
    
    try:
        settings = get_settings()
        
        # For now, we'll use a simple database URL
        # In production, this would be properly configured with Supabase
        database_url = "postgresql+asyncpg://postgres:password@localhost/plantcare"
        
        # Create async engine
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,  # Log SQL queries in debug mode
            pool_size=20,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # Create session maker
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("✅ Database connection initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database connection: {e}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Provides async database session for FastAPI dependency injection.
    Automatically handles session cleanup and error rollback.
    
    Yields:
        AsyncSession: Database session
    """
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database() -> None:
    """
    Close database connections.
    
    Cleanup function called during application shutdown
    to properly close all database connections.
    """
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("🔄 Database connections closed")


# Health check function
async def check_database_health() -> dict:
    """
    Check database connection health.
    
    Returns:
        dict: Database health status
    """
    try:
        if engine is None:
            return {
                "status": "unhealthy",
                "error": "Database not initialized"
            }
        
        # Test connection with simple query
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "postgresql"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "postgresql", 
            "error": str(e)
        }