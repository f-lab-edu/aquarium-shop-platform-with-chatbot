import datetime
import re
from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.apis.dependencies import get_session
from src.apis.exceptions import (
    AlreadyRegisteredEmailException,
    InvalidPhoneFormatException,
    PasswordMissingDigitException,
    PasswordMissingLetterException,
    PasswordTooShortException,
)
from src.apis.users.utils import pwd_context
from src.models.user import User, UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
    phone: Optional[str] = None

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
    email: EmailStr
    created_at: datetime.datetime


async def handler(
    user_data: UserCreate, session: Annotated[AsyncSession, Depends(get_session)]
) -> CreateUserResponse:
    stmt = select(User).where(User.email == user_data.email)
    result = await session.exec(stmt)
    existing_user = result.one_or_none()
    if existing_user:
        raise AlreadyRegisteredEmailException()

    hashed_password = pwd_context.hash(user_data.password)

    try:
        new_user = User(
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
        id=new_user.id, email=new_user.email, created_at=new_user.created_at
    )
