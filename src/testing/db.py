from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel


def build_test_engine(
    url: str = "sqlite+aiosqlite:///:memory:", echo: bool = False
) -> AsyncEngine:
    """
    테스트 전용 SQLite 엔진 생성

    - :memory: 사용 시 StaticPool로 커넥션 공유
    - prod 설정/`src.config`에 의존하지 않음
    """
    engine_params = {"url": url, "echo": echo}

    if url.startswith("sqlite") and ":memory:" in url:
        engine_params["poolclass"] = StaticPool

    return create_async_engine(**engine_params)


async def create_all(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_all(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
