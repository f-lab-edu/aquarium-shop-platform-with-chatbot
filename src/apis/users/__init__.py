from fastapi import APIRouter, status

from src.apis.users import create_refresh_token, create_user, post_login

user_router = APIRouter(tags=["users"])

user_router.add_api_route(
    methods=["POST"],
    path="/users",
    endpoint=create_user.handler,
    response_model=create_user.CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
)

user_router.add_api_route(
    methods=["POST"],
    path="/login",
    endpoint=post_login.handler,
    response_model=post_login.Token,
    status_code=status.HTTP_200_OK,
)

user_router.add_api_route(
    methods=["POST"],
    path="/token/refresh",
    endpoint=create_refresh_token.handler,
    response_model=post_login.Token,
    status_code=status.HTTP_200_OK,
)
