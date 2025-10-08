import hashlib
from typing import Annotated

from fastapi import Cookie, Depends, Response
from pydantic import BaseModel
from redis.asyncio import Redis

from src.apis.dependencies import get_redis
from src.apis.exceptions import UnauthorizedException
from src.services.auth import decode_and_validate


class LogoutResponse(BaseModel):
    message: str


async def handler(
    response: Response,
    redis_client: Annotated[Redis, Depends(get_redis)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> LogoutResponse:
    if not refresh_token:
        raise UnauthorizedException("리프레시 토큰이 없습니다.")

    payload = decode_and_validate(refresh_token, token_kind="리프레시 토큰")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("리프레시 토큰에 사용자 정보가 없습니다.")

    hashed_refresh = hashlib.sha256(refresh_token.encode()).hexdigest()
    key = f"user:{user_id}:refresh:{hashed_refresh}"
    await redis_client.delete(key)

    # Cookie 삭제 (Max-Age=0)
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        secure=False,  # 개발 환경에서는 False (프로덕션에서는 True)
        samesite="lax",  # 개발 환경에서는 lax (프로덕션에서는 strict)
        max_age=0,  # 즉시 삭제
        path="/",
    )

    return LogoutResponse(message="로그아웃 성공")
