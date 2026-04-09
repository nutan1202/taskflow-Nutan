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
from app.repositories.task_repository import (
    can_access_project_tasks,
    create_task,
    delete_task,
    get_project_for_tasks_by_id,
    get_task_by_id,
    get_task_with_project_by_id,
    get_user_by_id,
    list_project_tasks,
    update_task,
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
    "get_user_by_id",
    "get_project_for_tasks_by_id",
    "can_access_project_tasks",
    "list_project_tasks",
    "create_task",
    "get_task_by_id",
    "get_task_with_project_by_id",
    "update_task",
    "delete_task",
]
