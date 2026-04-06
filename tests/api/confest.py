# tests/api/conftest.py

import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.base import Base
import app.models  # noqa: F401 — ensures all models are registered before create_all

from main import app


# Use TEST_DATABASE_URL from .env
TEST_DB = settings.test_database_url


@pytest_asyncio.fixture(scope="session")
async def engine():
    e = create_async_engine(TEST_DB)
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
        yield s
        await s.rollback()


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncClient:
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c
    app.dependency_overrides.clear()


# Reusable helper — registers a user and returns their auth headers
async def register_and_login(client: AsyncClient, suffix: str = "") -> dict:
    payload = {
        "username": f"testuser{suffix}",
        "email": f"testuser{suffix}@example.com",
        "password": "Str0ngPass!",
        "display_name": f"Test User {suffix}",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}