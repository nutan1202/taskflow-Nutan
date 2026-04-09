"""Data access helpers."""

from app.repositories.auth_repository import create_user, get_user_by_email
from app.repositories.project_repository import (
    create_project,
    delete_project,
    get_accessible_project_with_tasks,
    get_project_by_id,
    list_accessible_projects,
    update_project,
)

__all__ = [
    "get_user_by_email",
    "create_user",
    "list_accessible_projects",
    "create_project",
    "get_project_by_id",
    "get_accessible_project_with_tasks",
    "update_project",
    "delete_project",
]
