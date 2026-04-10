# tests/api/conftest.py

import pytest
import pytest_asyncio
import uuid
from typing import AsyncGenerator

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.security import hash_password, create_access_token, create_refresh_token
from app.core.redis import init_redis, close_redis
from app.models.base import Base
from app.models.user import User
from app.models.project import Project, ProjectStage
import app.models  # noqa: F401 — ensures all models are registered before create_all

from main import app


# Use TEST_DATABASE_URL from .env
TEST_DB = settings.test_database_url


# ============================================================================
# Utility Functions
# ============================================================================


def truncate_password(pwd: str, max_bytes: int = 72) -> str:
    """
    Truncate password safely to bcrypt's 72-byte limit while handling UTF-8.
    
    Bcrypt truncates passwords at 72 bytes. This helper ensures that passwords
    are safely truncated without breaking UTF-8 sequences.
    
    Args:
        pwd: The password string to truncate
        max_bytes: Maximum bytes allowed (default: 72 for bcrypt)
        
    Returns:
        The password, truncated if necessary, safe for bcrypt hashing
        
    Examples:
        >>> truncate_password("ShortPass")  # No change
        'ShortPass'
        >>> truncate_password("x" * 100)  # Truncated to 72 bytes
        'xxxxxxxx...'
        >>> truncate_password("Пас密碼" * 10)  # Safe UTF-8 truncation
        'Пас密...' (truncated at safe boundary)
    """
    encoded = pwd.encode('utf-8')
    if len(encoded) > max_bytes:
        # Truncate and safely decode, ignoring incomplete UTF-8 sequences
        return encoded[:max_bytes].decode('utf-8', errors='ignore')
    return pwd


@pytest_asyncio.fixture(scope="session")
async def engine():
    e = create_async_engine(
        TEST_DB,
        pool_size=20,              # Larger pool for parallel fixtures
        max_overflow=10,           # Allow overflow connections
        pool_pre_ping=True,        # Validate connections before checkout
        echo=False,                # Set to True for SQL debugging
    )
        
    async with e.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield e
    async with e.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await e.dispose()


@pytest_asyncio.fixture()
async def db_session(engine) -> AsyncSession:
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as s:
        # Start a transaction that will explicitly rollback after test
        async with s.begin_nested():  # SAVEPOINT
            yield s
            # Implicit rollback when context exits
        # Session closes, any uncommitted changes are lost


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncClient:
    app.dependency_overrides[get_db] = lambda: db_session
    # Initialize Redis for tests (it will be mocked if not available)
    try:
        await init_redis()
    except Exception:
        # Redis may not be running in test environment — continue anyway
        pass
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c
    app.dependency_overrides.clear()
    try:
        await close_redis()
    except Exception:
        pass


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture()
def test_user_data():
    """Standard test user data. Password must be <=72 bytes for bcrypt."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Pass123!",  # 8 bytes — safe for bcrypt
        "display_name": "Test User",
    }


@pytest_asyncio.fixture()
async def test_user(db_session: AsyncSession, test_user_data) -> User:
    """Create a test user in the database."""
    # Ensure password is short enough for bcrypt (max 72 bytes)
    password = truncate_password(test_user_data["password"])
    
    user = User(
        id=uuid.uuid4(),
        username=test_user_data["username"].lower(),
        email=test_user_data["email"].lower(),
        password_hash=hash_password(password),
        display_name=test_user_data["display_name"],
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def test_user_2(db_session: AsyncSession) -> User:
    """Create a second test user for collaboration testing."""
    password = truncate_password("Pass123!")
    user = User(
        id=uuid.uuid4(),
        username="collaborator",
        email="collaborator@example.com",
        password_hash=hash_password(password),
        display_name="Collaborator User",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def inactive_user(db_session: AsyncSession) -> User:
    """Create an inactive test user."""
    password = truncate_password("Pass123!")
    user = User(
        id=uuid.uuid4(),
        username="inactiveuser",
        email="inactive@example.com",
        password_hash=hash_password(password),
        display_name="Inactive User",
        is_active=False,
        is_verified=False,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def unverified_user(db_session: AsyncSession) -> User:
    """Create an unverified test user."""
    password = truncate_password("Pass123!")
    user = User(
        id=uuid.uuid4(),
        username="unverifieduser",
        email="unverified@example.com",
        password_hash=hash_password(password),
        display_name="Unverified User",
        is_active=True,
        is_verified=False,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def auth_token(test_user: User) -> str:
    """Generate an access token for the test user."""
    return create_access_token(str(test_user.id))


@pytest_asyncio.fixture()
async def auth_token_2(test_user_2: User) -> str:
    """Generate an access token for the second test user."""
    return create_access_token(str(test_user_2.id))


@pytest_asyncio.fixture()
async def refresh_token(test_user: User) -> str:
    """Generate a refresh token for the test user."""
    return create_refresh_token(str(test_user.id))


@pytest_asyncio.fixture()
async def test_project_data():
    """Standard test project data."""
    return {
        "title": "Test Project",
        "description": "A test project for unit tests",
        "stage": ProjectStage.BUILDING,
        "support_tags": ["Bug fixes", "Documentation"],
        "tech_stack": ["Python", "FastAPI"],
        "repo_url": "https://github.com/test/project",
        "live_url": "https://test.example.com",
    }


@pytest_asyncio.fixture()
async def test_project(db_session: AsyncSession, test_user: User, test_project_data) -> Project:
    """Create a test project."""
    project = Project(
        id=uuid.uuid4(),
        owner_id=test_user.id,
        owner=test_user,
        **test_project_data,
        is_public=True,
    )
    db_session.add(project)
    await db_session.flush()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture()
async def private_project(db_session: AsyncSession, test_user: User) -> Project:
    """Create a private test project."""
    project = Project(
        id=uuid.uuid4(),
        owner_id=test_user.id,
        owner=test_user,
        title="Private Project",
        description="A private test project",
        stage=ProjectStage.IDEA,
        support_tags=[],
        tech_stack=["React"],
        is_public=False,
    )
    db_session.add(project)
    await db_session.flush()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture()
async def completed_project(db_session: AsyncSession, test_user: User) -> Project:
    """Create a completed test project."""
    from datetime import datetime, timezone
    project = Project(
        id=uuid.uuid4(),
        owner_id=test_user.id,
        owner=test_user,
        title="Completed Project",
        description="A completed test project",
        stage=ProjectStage.COMPLETED,
        support_tags=[],
        tech_stack=["Node.js"],
        is_public=True,
        completed_at=datetime.now(timezone.utc),
    )
    db_session.add(project)
    await db_session.flush()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture()
async def authorization_header(auth_token: str) -> dict:
    """Format auth token as request header."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture()
async def authorization_header_2(auth_token_2: str) -> dict:
    """Format second auth token as request header."""
    return {"Authorization": f"Bearer {auth_token_2}"}


# Reusable helper — registers a user and returns their auth headers
async def register_and_login(client: AsyncClient, suffix: str = "") -> dict:
    payload = {
        "username": f"testuser{suffix}",
        "email": f"testuser{suffix}@example.com",
        "password": truncate_password("Pass123!"),  # Safe for bcrypt
        "display_name": f"Test User {suffix}",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
