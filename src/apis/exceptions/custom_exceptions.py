from fastapi import status


class BaseCustomException(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UnauthorizedException(BaseCustomException):
    """인증되지 않은 접근에 대한 예외"""

    def __init__(self, message: str = "인증되지 않은 사용자입니다."):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class AlreadyRegisteredEmailException(BaseCustomException):
    """이미 가입된 이메일 예외"""

    def __init__(self, message: str = "이미 등록된 이메일입니다."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class AlreadyRegisteredUsernameException(BaseCustomException):
    """이미 가입된 Username 예외"""

    def __init__(self, message: str = "이미 등록돤 아이디입니다."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)
