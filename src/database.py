from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from redis.asyncio import Redis

from src import config

# 데이터베이스 엔진 생성
engine_params = {"url": config.db.url, "echo": config.db.echo}

# SQLite가 아닌 경우에만 PostgreSQL 전용 설정 추가
if not config.db.url.startswith("sqlite"):
    engine_params.update(
        {
            "pool_size": config.db.pool_size,
            "max_overflow": config.db.max_overflow,
            "pool_pre_ping": True,
            "pool_recycle": config.db.pool_recycle,
        }
    )

engine = create_async_engine(**engine_params)

# Redis 연결
redis_client = Redis.from_url(config.redis.url, decode_responses=True)


async def get_session() -> AsyncSession:
    """데이터베이스 세션 의존성"""
    async with AsyncSession(engine) as session:
        yield session


async def get_redis() -> Redis:
    """Redis 클라이언트 의존성"""
    return redis_client


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
