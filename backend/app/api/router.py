"""Aggregate API routers."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.routes import auth, health, projects, tasks

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    tasks.router,
    tags=["tasks"],
    dependencies=[Depends(get_current_user)],
)
