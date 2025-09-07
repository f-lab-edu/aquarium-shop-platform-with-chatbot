from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    url: str = Field(default="", alias="DATABASE_URL")
    echo: bool = Field(default=True, alias="DATABASE_ECHO")

    # 연결 풀 설정 (환경에 따라 조정 가능)
    pool_size: int = Field(default=20, alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=0, alias="DB_MAX_OVERFLOW")
    pool_recycle: int = Field(default=300, alias="DB_POOL_RECYCLE")


class RedisConfig(BaseSettings):
    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    password: str = Field(default="", alias="REDIS_PASSWORD")
    db: int = Field(default=0, alias="REDIS_DB")

    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class CORSConfig(BaseSettings):
    origins: str = Field(default="*", alias="CORS_ORIGINS")
    credentials: bool = Field(default=True, alias="CORS_CREDENTIALS")
    methods: str = Field(default="*", alias="CORS_METHODS")
    headers: str = Field(default="*", alias="CORS_HEADERS")


class WebConfig(BaseSettings):
    host: str = Field(default="0.0.0.0", alias="WEB_HOST")
    port: int = Field(default=8000, alias="WEB_PORT")
    # 워커 수 설정 (환경에 따라 조정 가능)
    workers: int = Field(default=1, alias="WEB_WORKERS")


class AppConfig(BaseSettings):
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


db = DatabaseConfig()
redis = RedisConfig()
cors = CORSConfig()
web = WebConfig()
app = AppConfig()
