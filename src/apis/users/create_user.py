import re
import datetime
from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.exceptions import (
    AlreadyRegisteredEmailException,
    AlreadyRegisteredUsernameException,
    PasswordMissingDigitException,
    UsernameTooShortException,
    InvalidUsernameFormatException,
    UsernameTooLongException,
    PasswordMissingLetterException,
    PasswordTooShortException,
    InvalidPhoneFormatException,
)
from src.apis.dependencies import get_session
from src.models.user import User, UserRole
from src.apis.users.utils import pwd_context


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole
    phone: Optional[str] = None

    @field_validator("username")
    def validate_username(cls, value):
        if len(value) < 3:
            raise UsernameTooShortException()
        if len(value) > 50:
            raise UsernameTooLongException()
        if not re.match(r"^[a-zA-Z0-9]+$", value):
            raise InvalidUsernameFormatException()
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 5:
            raise PasswordTooShortException()
        if not re.search(r"[0-9]", value):
            raise PasswordMissingDigitException()
        if not re.search(r"[A-Za-z]", value):
            raise PasswordMissingLetterException()
        return value

    @field_validator("phone")
    def validate_phone(cls, value):
        if value is None:
            return value
        pattern = (
            r"^(?:\+82\d{1,2}|0\d{2})-\d{3,4}-\d{4}$|^(?:\+82\d{1,2}|0\d{2})\d{7,8}$"
        )
        if not re.match(pattern, value):
            raise InvalidPhoneFormatException()
        return value


class CreateUserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime.datetime


async def handler(
    user_data: UserCreate, session: Annotated[AsyncSession, Depends(get_session)]
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

    try:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            role=user_data.role,
            phone=user_data.phone,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return CreateUserResponse(
        id=new_user.id, username=new_user.username, created_at=new_user.created_at
    )
