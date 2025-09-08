from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.apis.exceptions.custom_exceptions import BaseCustomException


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(BaseCustomException)
    async def custom_exception_handler(request: Request, exc: BaseCustomException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """예상치 못한 예외 처리"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "서버 내부 오류가 발생했습니다."},
        )
