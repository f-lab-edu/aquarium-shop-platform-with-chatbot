from fastapi import APIRouter, status

from src.apis.users import create_user, login

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
    endpoint=login.handler,
    response_model=login.Token,
    status_code=status.HTTP_200_OK,
)
