from typing import Annotated, Optional

from fastapi import Depends
from pydantic import BaseModel, EmailStr
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session
from src.apis.exceptions import (
    AlreadyRegisteredEmailException,
    AlreadyRegisteredUsernameException,
)
from src.apis.users.create_user import CreateUserResponse
from src.apis.users.utils import pwd_context
from src.models.user import User, UserRole


class AdminUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: Optional[str] = None


async def handler(
    user_data: AdminUserCreate, session: Annotated[AsyncSession, Depends(get_session)]
) -> CreateUserResponse:
    stmt = select(User).where(User.email == user_data.email)
    result = await session.exec(stmt)
    existing_user = result.one_or_none()
    if existing_user:
        raise AlreadyRegisteredEmailException()

    stmt = select(User).where(User.username == user_data.username)
    result = await session.exec(stmt)
    existing_username = result.one_or_none()
    if existing_username:
        raise AlreadyRegisteredUsernameException()

    hashed_password = pwd_context.hash(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        role=UserRole.ADMIN,
        phone=user_data.phone,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return CreateUserResponse(
        id=new_user.id, username=new_user.username, created_at=new_user.created_at
    )
