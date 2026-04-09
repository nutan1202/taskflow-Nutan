"""Project business logic."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import ForbiddenError, NotFoundError
from app.models.user import User
from app.repositories.project_repository import (
    create_project, delete_project, get_accessible_project_with_tasks,
    get_project_by_id, list_accessible_projects, update_project)
from app.schemas.project import (CreateProjectRequest, ProjectDetailResponse,
                                 ProjectListResponse, ProjectResponse,
                                 UpdateProjectRequest)


def list_projects_for_user(
    db: Session,
    *,
    user: User,
    page: int,
    limit: int,
) -> ProjectListResponse:
    projects, total = list_accessible_projects(
        db,
        user_id=user.id,
        page=page,
        limit=limit,
    )
    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(project) for project in projects],
        page=page,
        limit=limit,
        total=total,
    )


def create_project_for_user(
    db: Session,
    *,
    user: User,
    payload: CreateProjectRequest,
) -> ProjectResponse:
    project = create_project(
        db,
        name=payload.name.strip(),
        description=payload.description,
        owner_id=user.id,
    )
    return ProjectResponse.model_validate(project)


def get_project_details_for_user(
    db: Session,
    *,
    project_id: UUID,
    user: User,
) -> ProjectDetailResponse:
    project = get_accessible_project_with_tasks(
        db,
        project_id=project_id,
        user_id=user.id,
    )
    if project is None:
        raise NotFoundError()
    return ProjectDetailResponse.model_validate(project)


def update_project_for_user(
    db: Session,
    *,
    project_id: UUID,
    user: User,
    payload: UpdateProjectRequest,
) -> ProjectResponse:
    project = get_project_by_id(db, project_id)
    if project is None:
        raise NotFoundError()
    if project.owner_id != user.id:
        raise ForbiddenError()

    updated = update_project(
        db,
        project,
        name=payload.name.strip() if payload.name is not None else None,
        description=payload.description,
    )
    return ProjectResponse.model_validate(updated)


def delete_project_for_user(
    db: Session,
    *,
    project_id: UUID,
    user: User,
) -> None:
    project = get_project_by_id(db, project_id)
    if project is None:
        raise NotFoundError()
    if project.owner_id != user.id:
        raise ForbiddenError()
    delete_project(db, project)
