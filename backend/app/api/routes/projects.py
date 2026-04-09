"""Project routes (`/projects/*`)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.project import (CreateProjectRequest, ProjectDetailResponse,
                                 ProjectListResponse, ProjectResponse,
                                 ProjectStatsResponse, UpdateProjectRequest)
from app.services.project_service import (create_project_for_user,
                                          delete_project_for_user,
                                          get_project_details_for_user,
                                          get_project_stats_for_user,
                                          list_projects_for_user,
                                          update_project_for_user)

router = APIRouter()


@router.get("", response_model=ProjectListResponse, status_code=status.HTTP_200_OK)
def list_projects(
    db: DbSession,
    current_user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ProjectListResponse:
    return list_projects_for_user(
        db,
        user=current_user,
        page=page,
        limit=limit,
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(
    payload: CreateProjectRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectResponse:
    return create_project_for_user(db, user=current_user, payload=payload)


@router.get(
    "/{project_id}/stats",
    response_model=ProjectStatsResponse,
    status_code=status.HTTP_200_OK,
)
def get_project_stats(
    project_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectStatsResponse:
    return get_project_stats_for_user(db, project_id=project_id, user=current_user)


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_project(
    project_id: UUID, db: DbSession, current_user: CurrentUser
) -> ProjectDetailResponse:
    return get_project_details_for_user(
        db,
        project_id=project_id,
        user=current_user,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
def update_project_endpoint(
    project_id: UUID,
    payload: UpdateProjectRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectResponse:
    return update_project_for_user(
        db,
        project_id=project_id,
        user=current_user,
        payload=payload,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_endpoint(
    project_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    delete_project_for_user(db, project_id=project_id, user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
