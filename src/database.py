from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
import redis.asyncio as redis

from src import config


# PostgreSQL 엔진 생성 - 환경별 설정 적용
engine = create_async_engine(
    url=config.db.url,
    echo=config.db.echo,
    pool_size=config.db.pool_size,
    max_overflow=config.db.max_overflow,
    pool_pre_ping=True,
    pool_recycle=config.db.pool_recycle,
)

# Redis 연결
redis_client = redis.from_url(config.redis.url, decode_responses=True)


async def get_session() -> AsyncSession:
    """데이터베이스 세션 의존성"""
    async with AsyncSession(engine) as session:
        yield session


async def get_redis() -> redis.Redis:
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
