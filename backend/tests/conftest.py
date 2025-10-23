"""
Pytest Configuration for Async Database Testing

Provides fixtures and setup for running async database tests with clean isolation.
"""

import os
import sys
from pathlib import Path

# Add project directories to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir / "src"))

import pytest
import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.pool import StaticPool

# Import SQLAlchemy base
from src.database.base import Base


# Use in-memory SQLite for testing to ensure complete isolation
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async testing."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create an async SQLAlchemy engine for each test.

    Uses in-memory SQLite with StaticPool to ensure complete test isolation.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables and dispose engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Create an async database session for each test function.

    Provides a clean, isolated session for testing.
    """
    AsyncSessionLocal = async_sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def db_session(async_session: AsyncSession) -> AsyncSession:
    """
    Alias for async_session to maintain compatibility.
    """
    return async_session


@pytest.fixture(scope="function")
def sample_contact_data():
    """
    Provides sample contact data for testing.
    """
    from datetime import datetime

    return {
        "telegram_id": 123456789,
        "username": "test_user",
        "first_name": "John",
        "last_name": "Doe",
        "display_name": "John Doe",
        "phone": "+1234567890",
        "bio": "Test contact for unit testing",
        "profile_photo_path": "/test/photo.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
