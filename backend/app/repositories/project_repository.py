"""Repository helpers for project workflows."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.project import Project
from app.models.task import Task
from app.models.user import User


def list_accessible_projects(
    db: Session,
    *,
    user_id: UUID,
    page: int,
    limit: int,
) -> tuple[list[Project], int]:
    conditions = or_(
        Project.owner_id == user_id,
        Task.assignee_id == user_id,
        Task.creator_id == user_id,
    )

    total_stmt = (
        select(func.count(func.distinct(Project.id)))
        .select_from(Project)
        .outerjoin(Task, Task.project_id == Project.id)
        .where(conditions)
    )
    total = int(db.execute(total_stmt).scalar_one() or 0)

    offset = (page - 1) * limit
    projects_stmt = (
        select(Project)
        .outerjoin(Task, Task.project_id == Project.id)
        .where(conditions)
        .distinct()
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    projects = list(db.execute(projects_stmt).scalars().all())
    return projects, total


def create_project(
    db: Session,
    *,
    name: str,
    description: str | None,
    owner_id: UUID,
) -> Project:
    project = Project(name=name, description=description, owner_id=owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project_by_id(db: Session, project_id: UUID) -> Project | None:
    stmt = select(Project).where(Project.id == project_id)
    return db.execute(stmt).scalar_one_or_none()


def get_accessible_project_with_tasks(
    db: Session,
    *,
    project_id: UUID,
    user_id: UUID,
) -> Project | None:
    stmt = (
        select(Project)
        .options(selectinload(Project.tasks))
        .outerjoin(Task, Task.project_id == Project.id)
        .where(
            Project.id == project_id,
            or_(
                Project.owner_id == user_id,
                Task.assignee_id == user_id,
                Task.creator_id == user_id,
            ),
        )
        .distinct()
    )
    return db.execute(stmt).scalar_one_or_none()


def get_accessible_project(
    db: Session,
    *,
    project_id: UUID,
    user_id: UUID,
) -> Project | None:
    stmt = (
        select(Project)
        .outerjoin(Task, Task.project_id == Project.id)
        .where(
            Project.id == project_id,
            or_(
                Project.owner_id == user_id,
                Task.assignee_id == user_id,
                Task.creator_id == user_id,
            ),
        )
        .distinct()
    )
    return db.execute(stmt).scalar_one_or_none()


def get_project_task_stats(
    db: Session,
    *,
    project_id: UUID,
) -> tuple[dict[str, int], list[dict[str, object]]]:
    status_rows = db.execute(
        select(Task.status, func.count(Task.id))
        .where(Task.project_id == project_id)
        .group_by(Task.status)
    ).all()

    counts_by_status = {"todo": 0, "in_progress": 0, "done": 0}
    for status_value, count in status_rows:
        status_key = getattr(status_value, "value", str(status_value))
        counts_by_status[status_key] = int(count)

    assignee_rows = db.execute(
        select(Task.assignee_id, User.name, func.count(Task.id))
        .select_from(Task)
        .outerjoin(User, User.id == Task.assignee_id)
        .where(Task.project_id == project_id)
        .group_by(Task.assignee_id, User.name)
        .order_by(func.count(Task.id).desc(), User.name.asc().nullsfirst())
    ).all()

    counts_by_assignee: list[dict[str, object]] = []
    for assignee_id, assignee_name, count in assignee_rows:
        counts_by_assignee.append(
            {
                "assignee_id": assignee_id,
                "assignee_name": assignee_name,
                "count": int(count),
            }
        )

    return counts_by_status, counts_by_assignee


def update_project(
    db: Session,
    project: Project,
    *,
    name: str | None,
    description: str | None,
) -> Project:
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()
