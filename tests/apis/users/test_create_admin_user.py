import datetime
import logging

import pytest
from fastapi import status
from httpx import AsyncClient
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


# `POST /users` API가 성공적으로 동작한다.
@pytest.mark.asyncio
async def test_create_admin_user_successfully(
    client: AsyncClient, session: AsyncSession
):
    # when
    # `POST /users` API를 호출한다.
    response = await client.post(
        "/users",
        json={
            "email": "admin@example.com",
            "password": "password1",  # NOSONAR
            "role": UserRole.ADMIN,
            "phone": "010-1234-5678",
        },
    )

    # then
    # 응답 상태 코드가 201이어야 한다.
    assert response.status_code == status.HTTP_201_CREATED

    # 응답 본문이 예상한 형식과 같아야 한다.
    data = response.json()
    assert "id" in data
    assert data["email"] == "admin@example.com"
    assert "created_at" in data

    # 서버 내에 User 데이터가 저장되어 있어야 한다.
    user = await session.get(User, data["id"])
    assert user.email == "admin@example.com"
    assert user.role == UserRole.ADMIN
    assert user.phone == "010-1234-5678"
    assert pwd_context.verify("password1", user.password)  # NOSONAR
    assert user.created_at == datetime.datetime.fromisoformat(data["created_at"])


# `POST /users` API가 이미 등록된 이메일로 인해 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_existing_email(
    client: AsyncClient, session: AsyncSession
):
    # given
    # 기존 유저를 생성한다.
    existing_user = User(
        email="admin@example.com",
        password=pwd_context.hash("password1"),  # NOSONAR
        role=UserRole.ADMIN,
    )
    session.add(existing_user)
    await session.commit()
    await session.refresh(existing_user)

    # when
    response = await client.post(
        "/users",
        json={
            "email": "admin@example.com",
            "role": UserRole.ADMIN,
            "password": "password1",  # NOSONAR
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"][0]["msg"] == "이미 등록된 이메일입니다."


# `POST /users` API가 비밀번호 유효성 검사 실패로 인해 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_password_validation(client: AsyncClient):
    # when
    response = await client.post(
        "/users",
        json={
            "email": "admin@example.com",
            "role": UserRole.ADMIN,
            "password": "password",  # 숫자 없음  # NOSONAR
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"][0]["msg"] == "비밀번호는 최소 하나의 숫자를 포함해야 합니다."


# `POST /users` API가 이메일 형식 유효성 검사 실패로 인해 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_email_validation(client: AsyncClient):
    # when
    response = await client.post(
        "/users",
        json={
            "email": "invalid_email",
            "role": UserRole.ADMIN,
            "password": "password1",  # NOSONAR
        },
    )

    # then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# `POST /users` API가 phone 형식 invalid로 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_invalid_phone_format(client: AsyncClient):
    # when
    response = await client.post(
        "/users",
        json={
            "email": "admin@example.com",
            "role": UserRole.ADMIN,
            "password": "password1",  # NOSONAR
            "phone": "1234567890",  # invalid 형식
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"][0]["msg"]
        == "유효한 전화번호 형식이 아닙니다. 예: 010-1234-5678 또는 +821012345678"
    )
