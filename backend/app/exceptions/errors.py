"""Application exception hierarchy for consistent API error contracts."""


class AppError(Exception):
    """Base app exception with fixed status code and payload error string."""

    status_code: int = 500
    error: str = "internal server error"


class UnauthorizedError(AppError):
    status_code = 401
    error = "unauthorized"


class ForbiddenError(AppError):
    status_code = 403
    error = "forbidden"


class NotFoundError(AppError):
    status_code = 404
    error = "not found"


class ValidationFailedError(AppError):
    status_code = 400
    error = "validation failed"

    def __init__(self, fields: dict[str, str]):
        super().__init__("validation failed")
        self.fields = fields
