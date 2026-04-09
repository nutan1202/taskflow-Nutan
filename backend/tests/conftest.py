"""Pytest fixtures for API integration tests."""

import os
from pathlib import Path
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session, sessionmaker

os.environ["APP_NAME"] = "TaskFlow Test API"
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "false"
os.environ["API_HOST"] = "127.0.0.1"
os.environ["API_PORT"] = "8000"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow_test",
)
os.environ["JWT_SECRET"] = "test-secret-at-least-32-characters-long"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRY_HOURS"] = "24"
os.environ["BCRYPT_ROUNDS"] = "12"
os.environ["SEED_USER_EMAIL"] = "test@example.com"
os.environ["SEED_USER_PASSWORD"] = "password123"
os.environ["SEED_USER_NAME"] = "Test User"
os.environ["LOG_LEVEL"] = "INFO"

from app.db.session import get_db  # noqa: E402
from app.main import create_app  # noqa: E402


def _ensure_test_database_exists(db_url: str) -> None:
    url = make_url(db_url)
    db_name = url.database
    if not db_name:
        raise RuntimeError("DATABASE_URL must include a database name for tests.")

    admin_url = URL.create(
        drivername=url.drivername,
        username=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database="postgres",
        query=url.query,
    )
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as conn:
            conn.execute(
                text(
                    """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :db_name
                      AND pid <> pg_backend_pid()
                    """
                ),
                {"db_name": db_name},
            )
            conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    finally:
        admin_engine.dispose()


@pytest.fixture(scope="session")
def test_engine() -> Generator:
    database_url = os.environ["DATABASE_URL"]
    _ensure_test_database_exists(database_url)

    alembic_cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    alembic_cfg.set_main_option(
        "script_location",
        str(Path(__file__).resolve().parents[1] / "alembic"),
    )
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(alembic_cfg, "head")
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        yield engine
    finally:
        engine.dispose()
        command.downgrade(alembic_cfg, "base")


@pytest.fixture(autouse=True)
def clean_database(test_engine) -> Generator[None, None, None]:
    yield
    with test_engine.begin() as conn:
        table_names = conn.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename != 'alembic_version'
                """
            )
        ).scalars()
        names = [f'"{name}"' for name in table_names]
        if names:
            conn.execute(text(f"TRUNCATE TABLE {', '.join(names)} RESTART IDENTITY CASCADE"))


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


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
