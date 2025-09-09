import re
import datetime
from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
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
from src.database import get_session
from src.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
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


class CreateAdminResponse(BaseModel):
    id: int
    username: str
    created_at: datetime.datetime


async def handler(
    admin_data: AdminCreate, session: Annotated[AsyncSession, Depends(get_session)]
) -> CreateAdminResponse:
    stmt = select(User).where(User.email == admin_data.email)
    result = await session.exec(stmt)
    existing_user = result.one_or_none()
    if existing_user:
        raise AlreadyRegisteredEmailException()

    stmt = select(User).where(User.username == admin_data.username)
    result = await session.exec(stmt)
    existing_username = result.one_or_none()
    if existing_username:
        raise AlreadyRegisteredUsernameException()

    hashed_password = pwd_context.hash(admin_data.password)

    try:
        new_user = User(
            username=admin_data.username,
            email=admin_data.email,
            password=hashed_password,
            role=UserRole.ADMIN,
            phone=admin_data.phone,
        )
    except ValueError as e:
        # TODO: 해당 에러 처리를 어떻게 할지 고민하기
        raise HTTPException(status_code=400, detail=str(e))

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return CreateAdminResponse(
        id=new_user.id, username=new_user.username, created_at=new_user.created_at
    )
