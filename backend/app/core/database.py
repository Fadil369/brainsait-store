"""
Database configuration and session management
"""

import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

from .config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=NullPool if "sqlite" in settings.DATABASE_URL else None,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create declarative base
Base = declarative_base()


async def init_db():
    """Initialize database connection"""
    try:
        async with engine.begin() as conn:
            # Import all models here to ensure they are registered
            from app.models import invoices, orders, payments, products, users

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_db():
    """Close database connections"""
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


@asynccontextmanager
async def get_db_session():
    """Get database session context manager"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db():
    """Dependency to get database session"""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
