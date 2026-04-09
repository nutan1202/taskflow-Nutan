"""Authentication routes (`/auth/*`)."""

from fastapi import APIRouter, status

from app.api.deps import DbSession
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth_service import login_user, register_user

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: DbSession) -> AuthResponse:
    return register_user(db, payload)


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
def login(payload: LoginRequest, db: DbSession) -> AuthResponse:
    return login_user(db, payload)
