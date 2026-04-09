"""Idempotent TaskFlow seed script for local/dev Docker startup."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import create_engine, text

SEED_USER_ID = UUID("11111111-1111-1111-1111-111111111111")
SEED_PROJECT_ID = UUID("22222222-2222-2222-2222-222222222222")
SEED_TASK_IDS = (
    UUID("33333333-3333-3333-3333-333333333331"),
    UUID("33333333-3333-3333-3333-333333333332"),
    UUID("33333333-3333-3333-3333-333333333333"),
)

# bcrypt("password123") with cost 12
SEED_PASSWORD_HASH = "$2b$12$YZfko1udeXPL64SvgmdPfewzpOek2T7vaHNeV8y7WmLRay3k/5J/i"


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def run_seed() -> None:
    database_url = _required_env("DATABASE_URL")
    seed_user_email = os.getenv("SEED_USER_EMAIL", "test@example.com").strip().lower()
    seed_user_name = os.getenv("SEED_USER_NAME", "Test User").strip() or "Test User"

    now = datetime.now(timezone.utc)
    due_1 = (now + timedelta(days=3)).date()
    due_2 = (now + timedelta(days=5)).date()
    due_3 = (now + timedelta(days=1)).date()

    engine = create_engine(database_url, pool_pre_ping=True)

    inserted = {"users": 0, "projects": 0, "tasks": 0}

    with engine.begin() as conn:
        user_exists = conn.execute(
            text("SELECT id FROM users WHERE email = :email LIMIT 1"),
            {"email": seed_user_email},
        ).first()
        if user_exists is None:
            conn.execute(
                text(
                    """
                    INSERT INTO users (id, name, email, password, created_at)
                    VALUES (:id, :name, :email, :password, :created_at)
                    """
                ),
                {
                    "id": str(SEED_USER_ID),
                    "name": seed_user_name,
                    "email": seed_user_email,
                    "password": SEED_PASSWORD_HASH,
                    "created_at": now,
                },
            )
            inserted["users"] += 1

        project_exists = conn.execute(
            text("SELECT id FROM projects WHERE id = :id LIMIT 1"),
            {"id": str(SEED_PROJECT_ID)},
        ).first()
        if project_exists is None:
            conn.execute(
                text(
                    """
                    INSERT INTO projects (id, name, description, owner_id, created_at)
                    VALUES (:id, :name, :description, :owner_id, :created_at)
                    """
                ),
                {
                    "id": str(SEED_PROJECT_ID),
                    "name": "TaskFlow Demo Project",
                    "description": "Seeded project for reviewer testing",
                    "owner_id": str(SEED_USER_ID),
                    "created_at": now,
                },
            )
            inserted["projects"] += 1

        task_seed_rows = (
            {
                "id": str(SEED_TASK_IDS[0]),
                "title": "Seed task: todo",
                "description": "Initial task in todo state",
                "status": "todo",
                "priority": "medium",
                "due_date": due_1,
            },
            {
                "id": str(SEED_TASK_IDS[1]),
                "title": "Seed task: in progress",
                "description": "Task currently being worked on",
                "status": "in_progress",
                "priority": "high",
                "due_date": due_2,
            },
            {
                "id": str(SEED_TASK_IDS[2]),
                "title": "Seed task: done",
                "description": "Completed task example",
                "status": "done",
                "priority": "low",
                "due_date": due_3,
            },
        )

        for row in task_seed_rows:
            task_exists = conn.execute(
                text("SELECT id FROM tasks WHERE id = :id LIMIT 1"),
                {"id": row["id"]},
            ).first()
            if task_exists is not None:
                continue

            conn.execute(
                text(
                    """
                    INSERT INTO tasks (
                        id, title, description, status, priority,
                        project_id, assignee_id, creator_id,
                        due_date, created_at, updated_at
                    )
                    VALUES (
                        :id, :title, :description, :status, :priority,
                        :project_id, :assignee_id, :creator_id,
                        :due_date, :created_at, :updated_at
                    )
                    """
                ),
                {
                    **row,
                    "project_id": str(SEED_PROJECT_ID),
                    "assignee_id": str(SEED_USER_ID),
                    "creator_id": str(SEED_USER_ID),
                    "created_at": now,
                    "updated_at": now,
                },
            )
            inserted["tasks"] += 1

    print(
        "seed_completed",
        f"users_inserted={inserted['users']}",
        f"projects_inserted={inserted['projects']}",
        f"tasks_inserted={inserted['tasks']}",
    )


if __name__ == "__main__":
    run_seed()
