from fastapi import status

from src.apis.exceptions.custom_exceptions import BaseCustomException


class PasswordMissingDigitException(BaseCustomException):
    """비밀번호에 숫자가 포함되지 않은 경우 예외"""

    def __init__(self, message: str = "비밀번호는 최소 하나의 숫자를 포함해야 합니다."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)
