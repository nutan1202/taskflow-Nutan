"""Task routes (`/projects/{id}/tasks`, `/tasks/*`)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.deps import CurrentUser, DbSession
from app.models.task import TaskStatus
from app.schemas.task_api import (
    CreateTaskRequest,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
)
from app.services.task_service import (
    create_task_in_project,
    delete_task_for_user,
    list_tasks_for_project,
    update_task_for_user,
)

router = APIRouter()


@router.get(
    "/projects/{project_id}/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
)
def list_project_tasks_endpoint(
    project_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    assignee_filter: Annotated[UUID | None, Query(alias="assignee")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> TaskListResponse:
    return list_tasks_for_project(
        db,
        project_id=project_id,
        user=current_user,
        status=status_filter,
        assignee_id=assignee_filter,
        page=page,
        limit=limit,
    )


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task_endpoint(
    project_id: UUID,
    payload: CreateTaskRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> TaskResponse:
    return create_task_in_project(
        db,
        project_id=project_id,
        user=current_user,
        payload=payload,
    )


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def update_task_endpoint(
    task_id: UUID,
    payload: UpdateTaskRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> TaskResponse:
    return update_task_for_user(db, task_id=task_id, user=current_user, payload=payload)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(
    task_id: UUID, db: DbSession, current_user: CurrentUser
) -> Response:
    delete_task_for_user(db, task_id=task_id, user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
