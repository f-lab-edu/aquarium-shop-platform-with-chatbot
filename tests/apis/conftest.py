import pytest_asyncio
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session
from src.main import app
from src.testing.db import build_test_engine, create_all, drop_all

# 테스트용 SQLite 설정 (전역 엔진 생성: StaticPool로 in-memory 공유)
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
test_engine = build_test_engine(TEST_DB_URL, echo=False)


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async def override_get_session():
        async with AsyncSession(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    async with AsyncSession(test_engine) as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def reset_db():
    # 각 테스트마다 스키마 리셋
    await drop_all(test_engine)
    await create_all(test_engine)
    yield
