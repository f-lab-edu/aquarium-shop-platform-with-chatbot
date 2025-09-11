from typing import Annotated, Optional

import jwt
from fastapi import Depends, Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src import config
from src.apis.exceptions import (
    AuthorizationHeaderMissingException,
    InactiveOrInvalidUserException,
    InvalidTokenException,
    TokenExpiredException,
)
from src.database import engine, redis_client
from src.models.user import User

# Swagger Authorize 버튼을 활성화하기 위한 HTTP Bearer 보안 스키마
bearer_scheme = HTTPBearer(auto_error=False)


async def get_session() -> AsyncSession:
    """데이터베이스 세션 의존성"""
    async with AsyncSession(engine) as session:
        yield session


async def get_redis() -> Redis:
    """Redis 클라이언트 의존성"""
    return redis_client


class CurrentUser(BaseModel):
    id: int
    username: str
    role: str


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Security(bearer_scheme)
    ] = None,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> CurrentUser:
    token: Optional[str] = None

    # Swagger Authorize에서 설정된 Bearer 토큰 사용
    if credentials and credentials.scheme and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    else:
        raise AuthorizationHeaderMissingException()

    try:
        payload = jwt.decode(token, config.jwt.secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()

    user_id = int(payload.get("sub")) if payload.get("sub") is not None else None
    if user_id is None:
        raise InvalidTokenException("토큰 payload에 사용자 정보가 없습니다.")

    statement = (
        select(User.id, User.username, User.role, User.is_active)
        .where(User.id == user_id)
        .limit(1)
    )
    result = await session.exec(statement)
    row = result.one_or_none()
    if not row:
        raise InactiveOrInvalidUserException()

    user_id_value, username_value, role_value, is_active_value = row
    if not is_active_value:
        raise InactiveOrInvalidUserException()

    return CurrentUser(
        id=user_id_value,
        username=username_value or "",
        role=str(role_value),
    )
