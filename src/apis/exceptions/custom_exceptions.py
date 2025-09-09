from typing import Any, Dict, List, Optional
from fastapi import status


class BaseCustomException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int,
        type: str = "custom_error",
        loc: Optional[List[str]] = None,
        input: Optional[Any] = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.type = type
        self.loc = loc or ["unknown"]
        self.input = input
        self.ctx = ctx or {}
        super().__init__(self.message)

    def to_response(self) -> Dict[str, List[Dict[str, Any]]]:
        """FastAPI의 기본 에러 응답 형식과 유사한 JSON 구조를 반환"""

        error_detail = {
            "type": self.type,
            "loc": self.loc,
            "msg": self.message,
            "input": self.input,
            "ctx": self.ctx,
        }
        return {
            "detail": [dict((k, v) for k, v in error_detail.items() if v is not None)]
        }


class UnauthorizedException(BaseCustomException):
    """인증되지 않은 접근에 대한 예외"""

    def __init__(self, message: str = "인증되지 않은 사용자입니다."):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)
