from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    url: str = Field(default="sqlite+aiosqlite:///:memory:", alias="DATABASE_URL")
    echo: bool = Field(default=False, alias="DATABASE_ECHO")
    pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    pool_recycle: int = Field(default=1800, alias="DB_POOL_RECYCLE")


class RedisConfig(BaseSettings):
    url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")


class CORSConfig(BaseSettings):
    origins: str = Field(default="*", alias="CORS_ORIGINS")
    credentials: bool = Field(default=False, alias="CORS_CREDENTIALS")
    methods: str = Field(default="*", alias="CORS_METHODS")
    headers: str = Field(default="*", alias="CORS_HEADERS")


class WebConfig(BaseSettings):
    host: str = Field(default="127.0.0.1", alias="WEB_HOST")
    port: int = Field(default=8000, alias="WEB_PORT")
    # 워커 수 설정 (환경에 따라 조정 가능)
    workers: int = Field(default=1, alias="WEB_WORKERS")


class AppConfig(BaseSettings):
    environment: str = Field(default="test", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


class JWTConfig(BaseSettings):
    secret: str = Field(default="dev-secret", alias="JWT_SECRET")
    access_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")


db = DatabaseConfig()
redis = RedisConfig()
cors = CORSConfig()
web = WebConfig()
app = AppConfig()
jwt = JWTConfig()
