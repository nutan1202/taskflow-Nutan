"""FastAPI dependencies (DB session, auth, pagination)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.exceptions.errors import UnauthorizedError
from app.models.user import User
from app.utils.jwt_utils import (
    TokenExpiredError,
    TokenValidationError,
    decode_access_token,
)

DbSession = Annotated[Session, Depends(get_db)]
logger = get_logger(__name__)


def _raise_unauthorized(reason: str, request: Request | None = None) -> None:
    request_id = getattr(request.state, "request_id", None) if request else None
    logger.warning(
        "auth_failed",
        extra={
            "event": "auth_failed",
            "reason": reason,
            "request_id": request_id,
        },
    )
    raise UnauthorizedError()


def _extract_bearer_token(
    authorization: str | None, request: Request | None = None
) -> str:
    if not authorization:
        _raise_unauthorized("missing_authorization_header", request)

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        _raise_unauthorized("invalid_authorization_scheme", request)
    return token


def get_current_user(
    db: DbSession,
    request: Request,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> User:
    token = _extract_bearer_token(authorization, request)

    try:
        claims = decode_access_token(token)
    except (TokenValidationError, TokenExpiredError):
        _raise_unauthorized("invalid_or_expired_token", request)

    try:
        user_id = uuid.UUID(claims.user_id)
    except ValueError:
        _raise_unauthorized("invalid_user_id_claim", request)

    user = db.get(User, user_id)
    if user is None:
        _raise_unauthorized("user_not_found", request)
    if user.email != claims.email:
        _raise_unauthorized("email_claim_mismatch", request)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
