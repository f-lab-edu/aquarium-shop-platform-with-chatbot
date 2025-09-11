import hashlib
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from redis.asyncio import Redis

from src import config
from src.apis.dependencies import get_redis
from src.apis.exceptions import UnauthorizedException
from src.apis.users.jwt_token_factory import (
    decode_and_validate,
    generate_access_token,
    generate_refresh_token,
)
from src.apis.users.post_login import Token


class RefreshRequest(BaseModel):
    refresh_token: str


async def handler(
    request: RefreshRequest,
    redis_client: Annotated[Redis, Depends(get_redis)],
) -> Token:
    refresh_token = request.refresh_token

    payload = decode_and_validate(refresh_token, token_kind="리프레시 토큰")

    user_id = payload.get("sub")
    role = payload.get("role")
    if not user_id:
        raise UnauthorizedException("리프레시 토큰에 사용자 정보가 없습니다.")

    # Redis에서 유효성 확인
    # TODO: 리프레시 토큰처리 규칙(black list or 만료) 확립후 로직 수정 필요
    hashed_refresh = hashlib.sha256(refresh_token.encode()).hexdigest()
    key = f"user:{user_id}:refresh:{hashed_refresh}"
    exists = await redis_client.get(key)
    if not exists:
        raise UnauthorizedException("이미 사용되었거나 유효하지 않은 리프레시 토큰입니다.")

    await redis_client.delete(key)

    access_token = generate_access_token(user_id=str(user_id), role=role)
    new_refresh_token = generate_refresh_token(user_id=str(user_id), role=role)

    new_hashed_refresh = hashlib.sha256(new_refresh_token.encode()).hexdigest()
    await redis_client.setex(
        f"user:{user_id}:refresh:{new_hashed_refresh}",
        config.jwt.refresh_expire_days * 24 * 60 * 60,
        "1",
    )

    return Token(access_token=access_token, refresh_token=new_refresh_token)
