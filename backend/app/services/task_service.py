"""Task business logic."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import ForbiddenError, NotFoundError, ValidationFailedError
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.repositories.task_repository import (
    can_access_project_tasks,
    create_task,
    delete_task,
    get_project_for_tasks_by_id,
    get_task_with_project_by_id,
    get_user_by_id,
    list_project_tasks,
    update_task,
)
from app.schemas.task_api import (
    CreateTaskRequest,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
)


def _can_view_project_tasks(*, user: User, project_id: UUID, db: Session) -> bool:
    return can_access_project_tasks(db, project_id=project_id, user_id=user.id)


def _can_modify_task(*, user: User, task: Task) -> bool:
    # Collaborative update policy: owner, task creator, or current assignee can edit.
    return (
        task.project.owner_id == user.id
        or task.creator_id == user.id
        or task.assignee_id == user.id
    )


def _can_delete_task(*, user: User, task: Task) -> bool:
    # Assignment requirement: only project owner or task creator may delete.
    return task.project.owner_id == user.id or task.creator_id == user.id


def list_tasks_for_project(
    db: Session,
    *,
    project_id: UUID,
    user: User,
    status: TaskStatus | None,
    assignee_id: UUID | None,
    page: int,
    limit: int,
) -> TaskListResponse:
    project = get_project_for_tasks_by_id(db, project_id)
    if project is None:
        raise NotFoundError()
    if not _can_view_project_tasks(user=user, project_id=project_id, db=db):
        raise ForbiddenError()

    tasks, total = list_project_tasks(
        db,
        project_id=project_id,
        status=status,
        assignee_id=assignee_id,
        page=page,
        limit=limit,
    )
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        page=page,
        limit=limit,
        total=total,
    )


def create_task_in_project(
    db: Session,
    *,
    project_id: UUID,
    user: User,
    payload: CreateTaskRequest,
) -> TaskResponse:
    project = get_project_for_tasks_by_id(db, project_id)
    if project is None:
        raise NotFoundError()
    if not _can_view_project_tasks(user=user, project_id=project_id, db=db):
        raise ForbiddenError()

    if (
        payload.assignee_id is not None
        and get_user_by_id(db, payload.assignee_id) is None
    ):
        raise ValidationFailedError({"assignee_id": "not found"})

    task = create_task(
        db,
        title=payload.title.strip(),
        description=payload.description,
        priority=payload.priority,
        project_id=project_id,
        assignee_id=payload.assignee_id,
        creator_id=user.id,
        due_date=payload.due_date,
    )
    return TaskResponse.model_validate(task)


def update_task_for_user(
    db: Session,
    *,
    task_id: UUID,
    user: User,
    payload: UpdateTaskRequest,
) -> TaskResponse:
    task = get_task_with_project_by_id(db, task_id)
    if task is None:
        raise NotFoundError()
    if not _can_modify_task(user=user, task=task):
        raise ForbiddenError()

    updates = payload.model_dump(exclude_unset=True)

    if (
        "assignee_id" in updates
        and updates["assignee_id"] is not None
        and get_user_by_id(db, updates["assignee_id"]) is None
    ):
        raise ValidationFailedError({"assignee_id": "not found"})

    if "title" in updates and updates["title"] is not None:
        updates["title"] = updates["title"].strip()

    updated = update_task(
        db,
        task,
        updates=updates,
    )
    return TaskResponse.model_validate(updated)


def delete_task_for_user(db: Session, *, task_id: UUID, user: User) -> None:
    task = get_task_with_project_by_id(db, task_id)
    if task is None:
        raise NotFoundError()
    if not _can_delete_task(user=user, task=task):
        raise ForbiddenError()
    delete_task(db, task)
