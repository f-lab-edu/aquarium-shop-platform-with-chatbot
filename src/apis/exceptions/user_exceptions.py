from fastapi import status

from src.apis.exceptions.custom_exceptions import BaseCustomException


class AlreadyRegisteredEmailException(BaseCustomException):
    """이미 가입된 이메일 예외"""

    def __init__(self, message: str = "이미 등록된 이메일입니다."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class AlreadyRegisteredUsernameException(BaseCustomException):
    """이미 가입된 Username 예외"""

    def __init__(self, message: str = "이미 등록된 아이디입니다."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class UsernameTooShortException(BaseCustomException):
    """Username이 너무 짧은 경우의 예외"""

    def __init__(self, message: str = "아이디는 최소 3자 이상이어야 합니다."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class UsernameTooLongException(BaseCustomException):
    """Username이 너무 긴 경우의 예외"""

    def __init__(self, message: str = "아이디는 최대 50자까지 가능합니다."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class InvalidUsernameFormatException(BaseCustomException):
    """Username 형식이 유효하지 않은 경우의 예외"""

    def __init__(self, message: str = "아이디는 알파벳, 숫자만 포함할 수 있습니다."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class PasswordMissingDigitException(BaseCustomException):
    """비밀번호에 숫자가 포함되지 않은 경우 예외"""

    def __init__(self, message: str = "비밀번호는 최소 하나의 숫자를 포함해야 합니다."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class PasswordTooShortException(BaseCustomException):
    """비밀번호가 너무 짧은 경우의 예외"""

    def __init__(self, message: str = "비밀번호는 최소 5자 이상이어야 합니다."):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class PasswordMissingLetterException(BaseCustomException):
    """비밀번호에 알파벳이 포함되지 않은 경우의 예외"""

    def __init__(
        self, message: str = "비밀번호는 최소 한 개의 알파벳을 포함해야 합니다."
    ):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class InvalidPhoneFormatException(BaseCustomException):
    """유효하지 않은 전화번호 형식의 예외"""

    def __init__(
        self,
        message: str = "유효한 전화번호 형식이 아닙니다. 예: 010-1234-5678 또는 +821012345678",
    ):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)
