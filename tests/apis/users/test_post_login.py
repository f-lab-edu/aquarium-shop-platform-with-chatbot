from datetime import datetime, timedelta, timezone

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


@pytest.mark.asyncio
async def test_login_with_different_roles(client: AsyncClient, session: AsyncSession):
    """다양한 role의 사용자가 로그인할 수 있다."""
    # given - SELLER 사용자
    seller_password = "sellerpass123"  # NOSONAR
    seller = User(
        username="seller",
        email="seller@example.com",
        password=pwd_context.hash(seller_password),
        role=UserRole.SELLER,
        is_active=True,
    )
    session.add(seller)

    # ADMIN 사용자
    admin_password = "adminpass123"  # NOSONAR
    admin = User(
        username="admin",
        email="admin@example.com",
        password=pwd_context.hash(admin_password),
        role=UserRole.ADMIN,
        is_active=True,
    )
    session.add(admin)
    await session.commit()

    # when & then - SELLER 로그인
    response = await client.post(
        "/login",
        json={
            "email": "seller@example.com",
            "password": seller_password,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    seller_token = response.json()["access_token"]
    seller_payload = jwt.decode(seller_token, config.jwt.secret, algorithms=["HS256"])
    assert seller_payload["role"] == UserRole.SELLER

    # when & then - ADMIN 로그인
    response = await client.post(
        "/login",
        json={
            "email": "admin@example.com",
            "password": admin_password,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    admin_token = response.json()["access_token"]
    admin_payload = jwt.decode(admin_token, config.jwt.secret, algorithms=["HS256"])
    assert admin_payload["role"] == UserRole.ADMIN


@pytest.mark.asyncio
async def test_login_token_expiry_times(client: AsyncClient, session: AsyncSession):
    """토큰의 만료 시간이 올바르게 설정된다."""
    # given
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

    # when
    response = await client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": test_password,
        },
    )

    # then
    data = response.json()
    now = datetime.now(timezone.utc)

    # Access token 만료 시간 확인
    access_payload = jwt.decode(
        data["access_token"], config.jwt.secret, algorithms=["HS256"]
    )
    access_exp = datetime.fromtimestamp(access_payload["exp"], tz=timezone.utc)
    expected_access_exp = now + timedelta(minutes=config.jwt.access_expire_minutes)
    # 1분의 여유를 두고 검증
    assert abs((access_exp - expected_access_exp).total_seconds()) < 60

    # Refresh token 만료 시간 확인 (cookie에서 가져옴)
    refresh_token = response.cookies["refresh_token"]
    refresh_payload = jwt.decode(refresh_token, config.jwt.secret, algorithms=["HS256"])
    refresh_exp = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
    expected_refresh_exp = now + timedelta(days=config.jwt.refresh_expire_days)
    # 1분의 여유를 두고 검증
    assert abs((refresh_exp - expected_refresh_exp).total_seconds()) < 60
