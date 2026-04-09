"""Repository helpers for task workflows."""

from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.project import Project
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def get_project_for_tasks_by_id(db: Session, project_id: UUID) -> Project | None:
    stmt = select(Project).where(Project.id == project_id)
    return db.execute(stmt).scalar_one_or_none()


def can_access_project_tasks(db: Session, *, project_id: UUID, user_id: UUID) -> bool:
    stmt = (
        select(Project.id)
        .outerjoin(Task, Task.project_id == Project.id)
        .where(
            Project.id == project_id,
            or_(
                Project.owner_id == user_id,
                Task.assignee_id == user_id,
                Task.creator_id == user_id,
            ),
        )
        .limit(1)
    )
    return db.execute(stmt).first() is not None


def list_project_tasks(
    db: Session,
    *,
    project_id: UUID,
    status: TaskStatus | None,
    assignee_id: UUID | None,
    page: int,
    limit: int,
) -> tuple[list[Task], int]:
    filters = [Task.project_id == project_id]
    if status is not None:
        filters.append(Task.status == status)
    if assignee_id is not None:
        filters.append(Task.assignee_id == assignee_id)

    total_stmt = select(func.count(Task.id)).where(*filters)
    total = int(db.execute(total_stmt).scalar_one() or 0)

    offset = (page - 1) * limit
    tasks_stmt = (
        select(Task)
        .where(*filters)
        .order_by(Task.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    tasks = list(db.execute(tasks_stmt).scalars().all())
    return tasks, total


def create_task(
    db: Session,
    *,
    title: str,
    description: str | None,
    priority: TaskPriority,
    project_id: UUID,
    assignee_id: UUID | None,
    creator_id: UUID,
    due_date: date | None,
) -> Task:
    task = Task(
        title=title,
        description=description,
        priority=priority,
        project_id=project_id,
        assignee_id=assignee_id,
        creator_id=creator_id,
        due_date=due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_by_id(db: Session, task_id: UUID) -> Task | None:
    stmt = select(Task).where(Task.id == task_id)
    return db.execute(stmt).scalar_one_or_none()


def get_task_with_project_by_id(db: Session, task_id: UUID) -> Task | None:
    stmt = select(Task).options(joinedload(Task.project)).where(Task.id == task_id)
    return db.execute(stmt).scalar_one_or_none()


def update_task(db: Session, task: Task, *, updates: dict[str, Any]) -> Task:
    for field in (
        "title",
        "description",
        "status",
        "priority",
        "assignee_id",
        "due_date",
    ):
        if field in updates:
            setattr(task, field, updates[field])
    task.updated_at = datetime.now(timezone.utc)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
