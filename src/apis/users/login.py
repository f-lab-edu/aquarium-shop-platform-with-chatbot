import hashlib

from typing import Annotated
from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from redis.asyncio import Redis
from pydantic import BaseModel

from src import config
from src.apis.dependencies import get_session, get_redis
from src.models.user import User
from src.apis.exceptions import InvalidCredentialsException
from src.apis.users.utils import pwd_context
from src.apis.users.jwt_token_factory import (
    generate_access_token,
    generate_refresh_token,
)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


async def handler(
    login_data: UserLogin,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> Token:
    statement = select(User).where(User.username == login_data.username)
    result = await session.exec(statement)
    user = result.one_or_none()

    if not user:
        raise InvalidCredentialsException()

    if not pwd_context.verify(login_data.password, user.password):
        raise InvalidCredentialsException()

    access_token = generate_access_token(user_id=str(user.id), role=user.role)
    refresh_token = generate_refresh_token(user_id=str(user.id), role=user.role)

    hashed_refresh = hashlib.sha256(refresh_token.encode()).hexdigest()
    await redis_client.setex(
        f"user:{user.id}:refresh:{hashed_refresh}",
        config.jwt.refresh_expire_days * 24 * 60 * 60,  # days to seconds
        "1",
    )

    return Token(access_token=access_token, refresh_token=refresh_token)
