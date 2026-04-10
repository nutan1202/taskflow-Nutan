"""Centralized, strongly validated application settings."""

import re
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "development", "staging", "production", "test"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
JwtAlgorithm = Literal["HS256", "HS384", "HS512"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(min_length=1, validation_alias="APP_NAME")
    environment: Environment = Field(validation_alias="ENVIRONMENT")
    debug: bool = Field(validation_alias="DEBUG")
    api_host: str = Field(min_length=1, validation_alias="API_HOST")
    api_port: int = Field(ge=1, le=65535, validation_alias="API_PORT")
    database_url: str = Field(min_length=1, validation_alias="DATABASE_URL")
    jwt_secret: SecretStr = Field(min_length=32, validation_alias="JWT_SECRET")
    jwt_algorithm: JwtAlgorithm = Field(validation_alias="JWT_ALGORITHM")
    bcrypt_rounds: int = Field(ge=12, le=16, validation_alias="BCRYPT_ROUNDS")
    seed_user_email: str = Field(min_length=3, validation_alias="SEED_USER_EMAIL")
    seed_user_password: SecretStr = Field(
        min_length=8, validation_alias="SEED_USER_PASSWORD"
    )
    seed_user_name: str = Field(min_length=1, validation_alias="SEED_USER_NAME")
    log_level: LogLevel = Field(validation_alias="LOG_LEVEL")

    @field_validator(
        "app_name",
        "api_host",
        "database_url",
        "seed_user_name",
        mode="after",
    )
    @classmethod
    def no_blank_strings(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        lower = value.lower()
        if not (
            lower.startswith("postgresql://")
            or lower.startswith("postgresql+psycopg://")
            or lower.startswith("postgresql+asyncpg://")
        ):
            raise ValueError(
                "must start with postgresql://, postgresql+psycopg://, "
                "or postgresql+asyncpg://"
            )
        return value

    @field_validator("seed_user_email")
    @classmethod
    def validate_seed_user_email(cls, value: str) -> str:
        cleaned = value.strip()
        if not re.fullmatch(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cleaned):
            raise ValueError("must be a valid email address")
        return cleaned

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Compatibility accessor used by SQLAlchemy session setup."""
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
