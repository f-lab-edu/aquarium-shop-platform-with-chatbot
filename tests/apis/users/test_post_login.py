import jwt
import pytest
from fastapi import status
from httpx import AsyncClient
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession

from src import config
from src.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.mark.asyncio
async def test_login_successfully(client: AsyncClient, session: AsyncSession):
    """유효한 email과 password로 로그인이 성공한다."""
    # given
    # 테스트용 사용자 생성
    test_password = "testpassword123"  # NOSONAR
    test_user = User(
        username="testuser",
        email="test@example.com",
        password=pwd_context.hash(test_password),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    session.add(test_user)
    await session.commit()
    await session.refresh(test_user)

    # when
    # POST /login API 호출
    response = await client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": test_password,
        },
    )

    # then
    # 응답 상태 코드가 200이어야 한다
    assert response.status_code == status.HTTP_200_OK

    # 응답 본문에 access_token만 포함되어야 한다 (refresh_token은 cookie로)
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" not in data
    assert data["token_type"] == "bearer"

    # access token이 유효한 JWT여야 한다
    access_payload = jwt.decode(
        data["access_token"], config.jwt.secret, algorithms=["HS256"]
    )
    assert access_payload["sub"] == str(test_user.id)
    assert access_payload["role"] == test_user.role

    # refresh token이 httpOnly cookie로 설정되어야 한다
    cookies = response.cookies
    assert "refresh_token" in cookies
    refresh_token = cookies["refresh_token"]

    # refresh token이 유효한 JWT여야 한다
    refresh_payload = jwt.decode(refresh_token, config.jwt.secret, algorithms=["HS256"])
    assert refresh_payload["sub"] == str(test_user.id)
    assert refresh_payload["role"] == test_user.role


@pytest.mark.asyncio
async def test_login_failed_by_nonexistent_email(client: AsyncClient):
    """존재하지 않는 email로 로그인 시 실패한다."""
    # when
    response = await client.post(
        "/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123",  # NOSONAR
        },
    )

    # then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = response.json()["detail"][0]
    assert error["msg"] == "잘못된 이메일 또는 비밀번호입니다."
    assert error["code"] == "invalid_credentials"


@pytest.mark.asyncio
async def test_login_failed_by_wrong_password(
    client: AsyncClient, session: AsyncSession
):
    """잘못된 password로 로그인 시 실패한다."""
    # given
    test_user = User(
        username="testuser",
        email="test@example.com",
        password=pwd_context.hash("correctpassword123"),  # NOSONAR
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    session.add(test_user)
    await session.commit()

    # when
    response = await client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword123",  # NOSONAR
        },
    )

    # then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = response.json()["detail"][0]
    assert error["msg"] == "잘못된 이메일 또는 비밀번호입니다."
    assert error["code"] == "invalid_credentials"


@pytest.mark.asyncio
async def test_login_failed_by_invalid_email_format(client: AsyncClient):
    """잘못된 email 형식으로 로그인 시 실패한다."""
    # when
    response = await client.post(
        "/login",
        json={
            "email": "invalid-email",
            "password": "password123",  # NOSONAR
        },
    )

    # then
    # Note: 현재는 서버에서 email 유효성을 검증하지 않고 단순히 DB 조회 실패로 처리됨
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = response.json()["detail"][0]
    assert error["code"] == "invalid_credentials"


@pytest.mark.asyncio
async def test_login_failed_by_missing_field(client: AsyncClient):
    """필수 필드가 누락된 경우 로그인이 실패한다."""
    # when - email 누락
    response = await client.post(
        "/login",
        json={
            "password": "password123",  # NOSONAR
        },
    )

    # then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # when - password 누락
    response = await client.post(
        "/login",
        json={
            "email": "test@example.com",
        },
    )

    # then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
