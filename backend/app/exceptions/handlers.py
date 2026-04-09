"""Map exceptions to assignment JSON error bodies."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.errors import (
    AppError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)


def _format_validation_message(error: dict) -> str:
    error_type = error.get("type", "")
    message = str(error.get("msg", "invalid")).strip()

    if error_type == "missing":
        return "is required"
    if message.startswith("Field required"):
        return "is required"
    if message:
        return message[0].lower() + message[1:] if len(message) > 1 else message.lower()
    return "invalid"


def _extract_field_name(error: dict) -> str:
    loc = [str(x) for x in error.get("loc", ()) if x not in ("body", "query", "path")]
    return ".".join(loc) if loc else "request"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_exception_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.error})

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_exception_handler(
        _request: Request,
        _exc: UnauthorizedError,
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"error": "unauthorized"})

    @app.exception_handler(ForbiddenError)
    async def forbidden_exception_handler(
        _request: Request,
        _exc: ForbiddenError,
    ) -> JSONResponse:
        return JSONResponse(status_code=403, content={"error": "forbidden"})

    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(
        _request: Request,
        _exc: NotFoundError,
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"error": "not found"})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        fields: dict[str, str] = {}
        for err in exc.errors():
            key = _extract_field_name(err)
            fields[key] = _format_validation_message(err)
        return JSONResponse(
            status_code=400,
            content={"error": "validation failed", "fields": fields},
        )
