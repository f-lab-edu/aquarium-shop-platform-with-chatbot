from typing import Any

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

from src import config


def _build_engine_params(url: str, echo: bool) -> dict[str, Any]:
    params: dict[str, Any] = {"url": url, "echo": echo}
    if url.startswith("sqlite"):
        return params

    params.update(
        {
            "pool_size": config.db.pool_size,
            "max_overflow": config.db.max_overflow,
            "pool_pre_ping": True,
            "pool_recycle": config.db.pool_recycle,
        }
    )
    return params


def create_engine_from_config() -> AsyncEngine:
    return create_async_engine(**_build_engine_params(config.db.url, config.db.echo))


engine = create_engine_from_config()

# Redis 연결
redis_client = Redis.from_url(config.redis.url, decode_responses=True)


async def create_db_and_tables() -> None:
    """데이터베이스 테이블 생성"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """데이터베이스 연결 종료"""
    await engine.dispose()


async def close_redis() -> None:
    """Redis 연결 종료"""
    await redis_client.close()
