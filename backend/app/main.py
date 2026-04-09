"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.db.session import engine
from app.exceptions.handlers import register_exception_handlers
from app.middleware.request_context import RequestContextMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    setup_logging(level=settings.log_level)
    logger.info(
        "application_startup",
        extra={"event": "startup", "environment": settings.environment},
    )
    yield
    logger.info("application_shutdown", extra={"event": "shutdown"})
    engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
