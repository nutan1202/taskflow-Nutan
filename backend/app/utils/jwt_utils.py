"""JWT token creation and validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import get_settings


@dataclass(frozen=True)
class TokenClaims:
    """Validated claims extracted from an access token."""

    user_id: str
    email: str
    exp: int
    iat: int


class TokenValidationError(Exception):
    """Base class for token validation errors."""


class TokenExpiredError(TokenValidationError):
    """Raised when a token is expired."""


def create_access_token(
    *,
    user_id: str,
    email: str,
    expires_in_hours: int | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Required claims:
    - user_id
    - email
    """
    if not user_id:
        raise ValueError("user_id must be a non-empty string.")
    if not email or "@" not in email:
        raise ValueError("email must be a valid non-empty email address.")

    settings = get_settings()
    now = datetime.now(timezone.utc)
    expiry_hours = expires_in_hours or settings.jwt_expiry_hours
    expires_at = now + timedelta(hours=expiry_hours)

    payload: dict[str, Any] = {
        "user_id": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    return jwt.encode(
        payload,
        key=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> TokenClaims:
    """
    Decode and validate an access token.

    Raises:
    - TokenExpiredError: token has expired
    - TokenValidationError: token is invalid or missing required claims
    """
    if not token:
        raise TokenValidationError("Token is required.")

    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            key=settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "iat"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenValidationError("Invalid token.") from exc

    user_id = payload.get("user_id")
    email = payload.get("email")
    exp = payload.get("exp")
    iat = payload.get("iat")

    if not isinstance(user_id, str) or not user_id:
        raise TokenValidationError("Token missing valid user_id claim.")
    if not isinstance(email, str) or not email:
        raise TokenValidationError("Token missing valid email claim.")
    if not isinstance(exp, int):
        raise TokenValidationError("Token missing valid exp claim.")
    if not isinstance(iat, int):
        raise TokenValidationError("Token missing valid iat claim.")

    return TokenClaims(user_id=user_id, email=email, exp=exp, iat=iat)
