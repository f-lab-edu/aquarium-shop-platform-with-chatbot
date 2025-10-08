import hashlib
from typing import Annotated

from fastapi import Depends, Response
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src import config
from src.apis.dependencies import get_redis, get_session
from src.apis.exceptions import InvalidCredentialsException
from src.apis.users.utils import pwd_context
from src.models.user import User
from src.services.auth import generate_access_token, generate_refresh_token


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


async def handler(
    login_data: UserLogin,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> Token:
    statement = select(User).where(User.email == login_data.email)
    result = await session.exec(statement)
    user = result.one_or_none()

    if not user:
        raise InvalidCredentialsException()

    if not pwd_context.verify(login_data.password, user.password):
        raise InvalidCredentialsException()

    access_token = generate_access_token(
        user_id=str(user.id), email=user.email, role=user.role
    )
    refresh_token = generate_refresh_token(
        user_id=str(user.id), email=user.email, role=user.role
    )

    hashed_refresh = hashlib.sha256(refresh_token.encode()).hexdigest()
    await redis_client.setex(
        f"user:{user.id}:refresh:{hashed_refresh}",
        config.jwt.refresh_expire_days * 24 * 60 * 60,  # days to seconds
        "1",
    )

    # Refresh token을 httpOnly cookie로 설정
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=config.app.use_secure_cookies,  # 프로덕션에서만 True
        samesite="strict" if config.app.is_production else "lax",
        max_age=config.jwt.refresh_expire_days * 24 * 60 * 60,  # 7일 (초 단위)
        path="/",  # 모든 경로에서 접근 가능
    )

    return Token(access_token=access_token)
