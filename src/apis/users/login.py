import jwt
import hashlib

from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from redis.asyncio import Redis
from pydantic import BaseModel

from src import config
from src.database import get_session, get_redis
from src.models.user import User
from src.apis.exceptions.user_exceptions import InvalidCredentialsException
from src.apis.users.utils import pwd_context


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

    jwt_secret = config.jwt.secret
    access_payload = {
        "sub": str(user.id),
        "role": user.role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=config.jwt.access_expire_minutes),
    }
    access_token = jwt.encode(access_payload, jwt_secret, algorithm="HS256")

    refresh_payload = {
        "sub": str(user.id),
        "role": user.role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(days=config.jwt.refresh_expire_days),
    }
    refresh_token = jwt.encode(refresh_payload, jwt_secret, algorithm="HS256")

    hashed_refresh = hashlib.sha256(refresh_token.encode()).hexdigest()
    await redis_client.setex(
        f"user:{user.id}:refresh:{hashed_refresh}",
        config.jwt.refresh_expire_days * 24 * 60 * 60,  # days to seconds
        "1",
    )

    return Token(access_token=access_token, refresh_token=refresh_token)
