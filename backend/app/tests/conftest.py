from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

TEST_DB_PATH = Path(__file__).resolve().parents[2] / "test.db"

# Tests run only on SQLite, independent from development/prod database settings.
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", f"sqlite+aiosqlite:///{TEST_DB_PATH}")
os.environ["REDIS_URL"] = "redis://localhost:6379/9"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["EXPOSE_DEBUG_TOKENS"] = "true"
os.environ["DEBUG"] = "false"

from app.db.base import Base  # noqa: E402
from app.db.init_db import import_models  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database() -> AsyncGenerator[None, None]:
    import_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def truncate_tables() -> AsyncGenerator[None, None]:
    yield
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator:
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
