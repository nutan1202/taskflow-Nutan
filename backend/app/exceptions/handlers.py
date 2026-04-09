"""Map exceptions to assignment JSON error bodies."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    from app.api.deps import UnauthorizedError

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_exception_handler(
        _request: Request,
        _exc: UnauthorizedError,
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"error": "unauthorized"})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        fields: dict[str, str] = {}
        for err in exc.errors():
            loc_parts = [
                str(x) for x in err.get("loc", ()) if x not in ("body", "query", "path")
            ]
            key = ".".join(loc_parts) if loc_parts else "request"
            fields[key] = str(err.get("msg", "invalid"))
        return JSONResponse(
            status_code=400,
            content={"error": "validation failed", "fields": fields},
        )
