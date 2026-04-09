"""Authentication business logic."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import UnauthorizedError, ValidationFailedError
from app.repositories.auth_repository import create_user, get_user_by_email
from app.schemas.auth import (AuthResponse, LoginRequest, RegisterRequest,
                              UserResponse)
from app.utils.jwt_utils import create_access_token
from app.utils.password import hash_password, verify_password


def register_user(db: Session, payload: RegisterRequest) -> AuthResponse:
    normalized_email = payload.email.lower()

    existing_user = get_user_by_email(db, normalized_email)
    if existing_user is not None:
        raise ValidationFailedError({"email": "already exists"})

    try:
        user = create_user(
            db,
            name=payload.name.strip(),
            email=normalized_email,
            password_hash=hash_password(payload.password),
        )
    except IntegrityError:
        db.rollback()
        raise ValidationFailedError({"email": "already exists"})

    token = create_access_token(user_id=str(user.id), email=user.email)
    return AuthResponse(token=token, user=UserResponse.model_validate(user))


def login_user(db: Session, payload: LoginRequest) -> AuthResponse:
    user = get_user_by_email(db, payload.email.lower())
    if user is None:
        raise UnauthorizedError()

    if not verify_password(payload.password, user.password):
        raise UnauthorizedError()

    token = create_access_token(user_id=str(user.id), email=user.email)
    return AuthResponse(token=token, user=UserResponse.model_validate(user))
