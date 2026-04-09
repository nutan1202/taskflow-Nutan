"""Pytest fixtures for API integration tests."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["APP_NAME"] = "TaskFlow Test API"
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "false"
os.environ["API_HOST"] = "127.0.0.1"
os.environ["API_PORT"] = "8000"
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow_test"
)
os.environ["JWT_SECRET"] = "test-secret-at-least-32-characters-long"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRY_HOURS"] = "24"
os.environ["BCRYPT_ROUNDS"] = "12"
os.environ["SEED_USER_EMAIL"] = "test@example.com"
os.environ["SEED_USER_PASSWORD"] = "password123"
os.environ["SEED_USER_NAME"] = "Test User"
os.environ["LOG_LEVEL"] = "INFO"

import app.models  # noqa: F401, E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    fastapi_app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(fastapi_app) as c:
            yield c
    finally:
        fastapi_app.dependency_overrides.clear()
