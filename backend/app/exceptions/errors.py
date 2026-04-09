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
