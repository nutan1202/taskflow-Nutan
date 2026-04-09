"""Initial schema migration for TaskFlow.

Creates users, projects, and tasks tables with proper relationships,
indexes, and constraints.

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema for TaskFlow application."""

    # Create task_status enum type
    task_status_enum = postgresql.ENUM(
        "todo", "in_progress", "done", name="task_status", create_type=True
    )
    task_status_enum.create(op.get_bind())

    # Create task_priority enum type
    task_priority_enum = postgresql.ENUM(
        "low", "medium", "high", name="task_priority", create_type=True
    )
    task_priority_enum.create(op.get_bind())

    # Create users table
    op.create_table(
        "users",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    # Create indexes for users table
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_created_at", "users", ["created_at"])

    # Create projects table
    op.create_table(
        "projects",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name="fk_projects_owner_id_users",
            ondelete="CASCADE",
        ),
    )

    # Create indexes for projects table
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    op.create_index("ix_projects_created_at", "projects", ["created_at"])
    op.create_index(
        "ix_projects_owner_id_created_at", "projects", ["owner_id", "created_at"]
    )

    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", task_status_enum, nullable=False, server_default="todo"),
        sa.Column(
            "priority", task_priority_enum, nullable=False, server_default="medium"
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_tasks_project_id_projects",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["assignee_id"],
            ["users.id"],
            name="fk_tasks_assignee_id_users",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
            name="fk_tasks_creator_id_users",
            ondelete="CASCADE",
        ),
    )

    # Create single-column indexes for tasks table
    op.create_index("ix_tasks_project_id", "tasks", ["project_id"])
    op.create_index("ix_tasks_assignee_id", "tasks", ["assignee_id"])
    op.create_index("ix_tasks_creator_id", "tasks", ["creator_id"])
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_priority", "tasks", ["priority"])
    op.create_index("ix_tasks_due_date", "tasks", ["due_date"])
    op.create_index("ix_tasks_created_at", "tasks", ["created_at"])
    op.create_index("ix_tasks_updated_at", "tasks", ["updated_at"])

    # Create composite indexes for tasks table
    op.create_index("ix_tasks_project_id_status", "tasks", ["project_id", "status"])
    op.create_index(
        "ix_tasks_project_id_assignee_id", "tasks", ["project_id", "assignee_id"]
    )
    op.create_index("ix_tasks_assignee_id_status", "tasks", ["assignee_id", "status"])
    op.create_index("ix_tasks_project_id_due_date", "tasks", ["project_id", "due_date"])
    op.create_index(
        "ix_tasks_assignee_id_due_date", "tasks", ["assignee_id", "due_date"]
    )


def downgrade() -> None:
    """Drop all tables and enum types."""

    # Drop tasks table and its indexes (indexes are dropped automatically with table)
    op.drop_table("tasks")

    # Drop projects table and its indexes
    op.drop_table("projects")

    # Drop users table and its indexes
    op.drop_table("users")

    # Drop enum types
    # Note: PostgreSQL requires explicit enum type drops
    op.execute("DROP TYPE IF EXISTS task_priority")
    op.execute("DROP TYPE IF EXISTS task_status")
