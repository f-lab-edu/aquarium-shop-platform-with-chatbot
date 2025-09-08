from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, String


class UserRole(str, Enum):
    CUSTOMER = "customer"
    SELLER = "seller"
    ADMIN = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = Field(
        default=None, sa_type=String, max_length=100, unique=True
    )
    password: Optional[str] = Field(default=None, max_length=100)
    kakao_auth_token: Optional[str] = Field(default=None, max_length=100)
    role: UserRole = Field(default=UserRole.CUSTOMER)
    phone: Optional[str] = Field(default=None, max_length=20)
    points: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
