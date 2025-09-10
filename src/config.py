from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    url: str = Field(alias="DATABASE_URL")
    echo: bool = Field(alias="DATABASE_ECHO")
    pool_size: int = Field(alias="DB_POOL_SIZE")
    max_overflow: int = Field(alias="DB_MAX_OVERFLOW")
    pool_recycle: int = Field(alias="DB_POOL_RECYCLE")


class RedisConfig(BaseSettings):
    url: str = Field(alias="REDIS_URL")


class CORSConfig(BaseSettings):
    origins: str = Field(alias="CORS_ORIGINS")
    credentials: bool = Field(alias="CORS_CREDENTIALS")
    methods: str = Field(alias="CORS_METHODS")
    headers: str = Field(alias="CORS_HEADERS")


class WebConfig(BaseSettings):
    host: str = Field(alias="WEB_HOST")
    port: int = Field(alias="WEB_PORT")
    # 워커 수 설정 (환경에 따라 조정 가능)
    workers: int = Field(default=1, alias="WEB_WORKERS")


class AppConfig(BaseSettings):
    environment: str = Field(alias="ENVIRONMENT")
    debug: bool = Field(alias="DEBUG")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


class JWTConfig(BaseSettings):
    secret: str = Field(alias="JWT_SECRET")
    access_expire_minutes: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_expire_days: int = Field(alias="REFRESH_TOKEN_EXPIRE_DAYS")


db = DatabaseConfig()
redis = RedisConfig()
cors = CORSConfig()
web = WebConfig()
app = AppConfig()
jwt = JWTConfig()
