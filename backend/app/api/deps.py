"""FastAPI dependencies (DB session, auth, pagination)."""

import uuid
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.exceptions.errors import UnauthorizedError
from app.models.user import User
from app.utils.jwt_utils import (
    TokenExpiredError,
    TokenValidationError,
    decode_access_token,
)

DbSession = Annotated[Session, Depends(get_db)]


def _raise_unauthorized() -> None:
    raise UnauthorizedError()


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        _raise_unauthorized()

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        _raise_unauthorized()
    return token


def get_current_user(
    db: DbSession,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> User:
    token = _extract_bearer_token(authorization)

    try:
        claims = decode_access_token(token)
    except (TokenValidationError, TokenExpiredError):
        _raise_unauthorized()

    try:
        user_id = uuid.UUID(claims.user_id)
    except ValueError:
        _raise_unauthorized()

    user = db.get(User, user_id)
    if user is None:
        _raise_unauthorized()
    if user.email != claims.email:
        _raise_unauthorized()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
