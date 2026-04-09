"""Pydantic request/response schemas."""

from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.schemas.project import (
    AssigneeTaskCount,
    CreateProjectRequest,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectStatsResponse,
    UpdateProjectRequest,
)
from app.schemas.task_api import (
    CreateTaskRequest,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
)

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "UserResponse",
    "AuthResponse",
    "CreateProjectRequest",
    "UpdateProjectRequest",
    "ProjectResponse",
    "ProjectDetailResponse",
    "ProjectListResponse",
    "AssigneeTaskCount",
    "ProjectStatsResponse",
    "CreateTaskRequest",
    "UpdateTaskRequest",
    "TaskResponse",
    "TaskListResponse",
]
