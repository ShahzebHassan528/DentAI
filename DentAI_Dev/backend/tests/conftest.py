"""
Shared test fixtures for DentAI backend.

Uses an in-memory SQLite database (via aiosqlite) so no real
PostgreSQL connection is needed during testing.
"""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

# ── Import app + overridable dependency ───────────────────────────────────────
from app.main import app
from app.core.database import Base, get_db

# ── Import ALL models so Base.metadata knows every table ─────────────────────
from app.models.user import User, UserRole          # noqa: F401
from app.models.prediction import Prediction        # noqa: F401
from app.models.report import Report                # noqa: F401

# ── In-memory SQLite engine (shared for the entire test session) ──────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,           # single connection — required for in-memory SQLite
    echo=False,
)
_TestSession = async_sessionmaker(
    _engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Override FastAPI's get_db to use test SQLite DB ───────────────────────────
async def _override_get_db():
    async with _TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = _override_get_db


# ── Session-scoped event loop (required for session-scoped async fixtures) ────
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Create / drop tables once per test session ────────────────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── Shared HTTP client ────────────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── Register a patient and return its auth headers ───────────────────────────
@pytest_asyncio.fixture(scope="session")
async def patient_headers(client: AsyncClient) -> dict:
    resp = await client.post("/auth/register", json={
        "name": "Test Patient",
        "email": "patient_fixture@test.com",
        "password": "TestPass123!",
        "role": "patient",
    })
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Register a doctor and return its auth headers ────────────────────────────
@pytest_asyncio.fixture(scope="session")
async def doctor_headers(client: AsyncClient) -> dict:
    resp = await client.post("/auth/register", json={
        "name": "Test Doctor",
        "email": "doctor_fixture@test.com",
        "password": "TestPass123!",
        "role": "doctor",
    })
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
