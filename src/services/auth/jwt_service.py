from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt

from src import config
from src.apis.exceptions import UnauthorizedException


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def generate_access_token(
    user_id: str, role: str, now: Optional[datetime] = None
) -> str:
    current_time = now or _now_utc()
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": current_time,
        "exp": current_time + timedelta(minutes=config.jwt.access_expire_minutes),
    }
    return jwt.encode(payload, config.jwt.secret, algorithm="HS256")


def generate_refresh_token(
    user_id: str, role: str, now: Optional[datetime] = None
) -> str:
    current_time = now or _now_utc()
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": current_time,
        "exp": current_time + timedelta(days=config.jwt.refresh_expire_days),
    }
    return jwt.encode(payload, config.jwt.secret, algorithm="HS256")


def decode_and_validate(token: str, token_kind: str = "토큰") -> dict[str, Any]:
    allowed_algorithms = ["HS256"]
    try:
        return jwt.decode(token, config.jwt.secret, algorithms=allowed_algorithms)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(f"{token_kind}이 만료되었습니다.")
    except jwt.InvalidTokenError:
        raise UnauthorizedException(f"유효하지 않은 {token_kind}입니다.")
