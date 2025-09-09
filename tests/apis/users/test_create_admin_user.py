import datetime
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext

from src.models.user import User, UserRole


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# `POST /users/create-admin-user` API가 성공적으로 동작한다.
@pytest.mark.asyncio
async def test_create_admin_user_successfully(
    client: AsyncClient, session: AsyncSession
):
    # when
    # `POST /users/create-admin-user` API를 호출한다.
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "password1",
            "phone": "010-1234-5678",
        },
    )

    # then
    # 응답 상태 코드가 201이어야 한다.
    assert response.status_code == status.HTTP_201_CREATED

    # 응답 본문이 예상한 형식과 같아야 한다.
    data = response.json()
    assert "id" in data
    assert data["username"] == "adminuser"
    assert "created_at" in data

    # 서버 내에 User 데이터가 저장되어 있어야 한다.
    user = await session.get(User, data["id"])
    assert user.username == "adminuser"
    assert user.email == "admin@example.com"
    assert user.role == UserRole.ADMIN
    assert user.phone == "010-1234-5678"
    assert pwd_context.verify("password1", user.password)
    assert user.created_at == datetime.datetime.fromisoformat(data["created_at"])


# `POST /users/create-admin-user` API가 이미 등록된 이메일로 인해 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_existing_email(
    client: AsyncClient, session: AsyncSession
):
    # given
    # 기존 유저를 생성한다.
    existing_user = User(
        username="existing",
        email="admin@example.com",
        password=pwd_context.hash("password1"),
        role=UserRole.ADMIN,
    )
    session.add(existing_user)
    await session.commit()
    await session.refresh(existing_user)

    # when
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "newuser",
            "email": "admin@example.com",
            "password": "password1",
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"][0]["msg"] == "이미 등록된 이메일입니다."


# `POST /users/create-admin-user` API가 이미 등록된 username으로 인해 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_existing_username(
    client: AsyncClient, session: AsyncSession
):
    # given
    # 기존 유저를 생성한다.
    existing_user = User(
        username="adminuser",
        email="existing@example.com",
        password=pwd_context.hash("password1"),
        role=UserRole.ADMIN,
    )
    session.add(existing_user)
    await session.commit()
    await session.refresh(existing_user)

    # when
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "adminuser",
            "email": "new@example.com",
            "password": "password1",
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"][0]["msg"] == "이미 등록된 아이디입니다."


# `POST /users/create-admin-user` API가 비밀번호 유효성 검사 실패로 인해 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_password_validation(client: AsyncClient):
    # when
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "password",  # 숫자 없음
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"][0]["msg"]
        == "비밀번호는 최소 하나의 숫자를 포함해야 합니다."
    )


# `POST /users/create-admin-user` API가 이메일 형식 유효성 검사 실패로 인해 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_email_validation(client: AsyncClient):
    # when
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "adminuser",
            "email": "invalid_email",
            "password": "password1",
        },
    )

    # then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# `POST /users/create-admin-user` API가 username이 너무 짧아서 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_username_too_short(client: AsyncClient):
    # when
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "ab",  # 3자 미만
            "email": "admin@example.com",
            "password": "password1",
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# `POST /users/create-admin-user` API가 username이 너무 길어서 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_username_too_long(client: AsyncClient):
    # when
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "a" * 51,
            "email": "admin@example.com",
            "password": "password1",
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# `POST /users/create-admin-user` API가 username 형식 invalid로 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_invalid_username_format(client: AsyncClient):
    # when
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "admin_user!",  # 특수문자 포함
            "email": "admin@example.com",
            "password": "password1",
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# `POST /users/create-admin-user` API가 password가 너무 짧아서 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_password_too_short(client: AsyncClient):
    # when
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "pas1",  # 5자 미만
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"][0]["msg"] == "비밀번호는 최소 5자 이상이어야 합니다."
    )


# `POST /users/create-admin-user` API가 password에 문자가 없어서 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_password_missing_letter(client: AsyncClient):
    # when
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "12345",  # 문자 없음
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"][0]["msg"]
        == "비밀번호는 최소 한 개의 알파벳을 포함해야 합니다."
    )


# `POST /users/create-admin-user` API가 phone 형식 invalid로 실패한다.
@pytest.mark.asyncio
async def test_create_admin_user_failed_by_invalid_phone_format(client: AsyncClient):
    # when
    response = await client.post(
        "/users/create-admin-user",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "password1",
            "phone": "1234567890",  # invalid 형식
        },
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"][0]["msg"]
        == "유효한 전화번호 형식이 아닙니다. 예: 010-1234-5678 또는 +821012345678"
    )
