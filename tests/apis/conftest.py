import os
import pytest_asyncio
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import create_db_and_tables, engine
from src.main import app

# 테스트용 SQLite 설정
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    await create_db_and_tables()

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        yield ac


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
