from fastapi import APIRouter, status

from src.apis.users import create_admin_user

user_router = APIRouter(tags=["users"])

user_router.add_api_route(
    methods=["POST"],
    path="/users/create-admin-user",
    endpoint=create_admin_user.handler,
    response_model=create_admin_user.CreateAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
