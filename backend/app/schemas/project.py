"""Project request/response schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskInProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    project_id: UUID
    assignee_id: UUID | None
    due_date: date | None
    created_at: datetime
    updated_at: datetime


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    created_at: datetime


class ProjectDetailResponse(ProjectResponse):
    tasks: list[TaskInProjectResponse] = []


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class UpdateProjectRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    page: int
    limit: int
    total: int


class AssigneeTaskCount(BaseModel):
    assignee_id: UUID | None
    assignee_name: str | None
    count: int


class ProjectStatsResponse(BaseModel):
    project_id: UUID
    counts_by_status: dict[str, int]
    counts_by_assignee: list[AssigneeTaskCount]
