from pydantic_settings import BaseSettings, SettingsConfigDict
from celery import Celery

# > this Setting class will help the application to read the env variables from .env file
# > every and each env variable that we want to read from .env file should be defined here as attribute
# config.py
from pydantic import Field, field_validator
import re
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection URL")

    # JWT
    JWT_SECRET: str = Field(..., min_length=16, description="Secret key for JWT tokens")
    JWT_ALGO: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRY: int = Field(
        default=3600, ge=300, le=86400, description="Access token expiry in seconds"
    )
    REFRESH_TOKEN_EXPIRY: int = Field(
        default=2592000,
        ge=86400,
        le=2592000,
        description="Refresh token expiry in seconds",
    )

    # Redis
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535)
    REDIS_PASSWORD: str | None = Field(default=None)
    REDIS_DB: int = Field(default=0, ge=0, le=15)

    # Security
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    ALLOWED_HOSTS: list[str] = Field(default=["localhost", "127.0.0.1"])

    # Application
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(
        default="development", pattern="^(development|staging|production)$"
    )

    # API
    API_PREFIX: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="Book Management API")
    PROJECT_VERSION: str = Field(default="1.0.0")

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Requests per minute")
    RATE_LIMIT_PERIOD: int = Field(
        default=60, description="Rate limit period in seconds"
    )

    # mail config
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    # DOMAIN
    DOMAIN: str = Field(...)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str):
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError(
                "DATABASE_URL must start with postgresql:// or postgresql+asyncpg://"
            )
        return v

    @field_validator("JWT_SECRET")
    def validate_jwt_secret(cls, v: str):
        if len(v) < 16:
            raise ValueError("JWT_SECRET must be at least 16 characters long")
        return v

settings = Settings()
broker_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
result_backend = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"



# Initialize Celery app in config.py
c_app = Celery(
    "myproject",
    broker_url=broker_url,
    result_backend=result_backend,
)

# Configure Celery
c_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
)