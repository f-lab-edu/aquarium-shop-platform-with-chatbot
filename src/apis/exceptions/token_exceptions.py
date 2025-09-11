from src.apis.exceptions import UnauthorizedException


class AuthorizationHeaderMissingException(UnauthorizedException):
    def __init__(self, message: str = "Authorization 헤더가 필요합니다."):
        super().__init__(message=message)
        self.code = "auth_header_missing"


class InvalidBearerFormatException(UnauthorizedException):
    def __init__(
        self,
        message: str = "Authorization 헤더 형식이 잘못되었습니다. 'Bearer <token>'을 사용하세요.",
    ):
        super().__init__(message=message)
        self.code = "invalid_bearer_format"


class TokenExpiredException(UnauthorizedException):
    def __init__(self, message: str = "토큰이 만료되었습니다."):
        super().__init__(message=message)
        self.code = "token_expired"


class InvalidTokenException(UnauthorizedException):
    def __init__(self, message: str = "유효하지 않은 토큰입니다."):
        super().__init__(message=message)
        self.code = "invalid_token"


class InactiveOrInvalidUserException(UnauthorizedException):
    def __init__(self, message: str = "유효하지 않거나 비활성화된 사용자입니다."):
        super().__init__(message=message)
        self.code = "inactive_or_invalid_user"
