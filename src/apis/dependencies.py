from sqlmodel.ext.asyncio.session import AsyncSession


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
