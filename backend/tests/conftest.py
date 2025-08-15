"""
Shared test fixtures and configuration for all tests.
"""

import asyncio
import uuid
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Test database URL - using SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
TEST_DATABASE_URL_SYNC = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_engine():
    """Create async database engine for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def sync_engine():
    """Create sync database engine for testing."""
    engine = create_engine(
        TEST_DATABASE_URL_SYNC,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    yield engine
    engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing."""
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def sync_session(sync_engine):
    """Create sync database session for testing."""
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_admin_user():
    """Create mock admin user data."""
    return {
        "id": str(uuid.uuid4()),
        "email": "admin@test.com",
        "username": "admin",
        "full_name": "Test Admin",
        "is_active": True,
        "is_superuser": True,
        "tenant_id": "test-tenant",
    }


@pytest.fixture
def mock_regular_user():
    """Create mock regular user data."""
    return {
        "id": str(uuid.uuid4()),
        "email": "user@test.com",
        "username": "user",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
        "tenant_id": "test-tenant",
    }


@pytest.fixture
def mock_tenant_id():
    """Mock tenant ID for testing."""
    return "test-tenant"


@pytest.fixture
def mock_headers(mock_tenant_id):
    """Mock headers for API requests."""
    return {
        "X-Tenant-ID": mock_tenant_id,
        "Accept-Language": "en",
        "Content-Type": "application/json",
    }


# Create a simple test app without complex dependencies
@pytest.fixture
def test_app():
    """Create simple test FastAPI application."""
    from fastapi import FastAPI
    
    app = FastAPI(title="Test API")
    
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    return app


@pytest.fixture
def client(test_app) -> Generator[TestClient, None, None]:
    """Create test client."""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_admin_client(client, mock_admin_user):
    """Create authenticated admin client with mocked auth."""
    # For now, just return the client since we don't have auth setup
    yield client


@pytest.fixture
def authenticated_user_client(client, mock_regular_user):
    """Create authenticated regular user client with mocked auth."""
    # For now, just return the client since we don't have auth setup
    yield client


# Database cleanup fixtures
@pytest.fixture(autouse=True)
async def clean_db(async_session):
    """Clean database before each test."""
    # This runs before each test to ensure clean state
    yield
    
    # Clean up after test
    try:
        await async_session.rollback()
    except:
        pass


# Configuration for pytest-asyncio
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "db: mark test as requiring database"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Skip tests if certain dependencies are not available
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Mark database tests
        if "async_session" in item.fixturenames or "sync_session" in item.fixturenames:
            item.add_marker(pytest.mark.db)
        
        # Mark API tests
        if "client" in item.fixturenames:
            item.add_marker(pytest.mark.api)
        
        # Mark integration tests
        if any(fixture in item.fixturenames for fixture in ["test_app", "authenticated_admin_client"]):
            item.add_marker(pytest.mark.integration)