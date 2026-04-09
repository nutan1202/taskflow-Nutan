"""Task model."""

import enum
import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, enum.Enum):
    """Task priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):
    """Task model representing a work item within a project."""

    __tablename__ = "tasks"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=None,  # Let application handle UUID generation
    )

    # Required Fields
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional Fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Enum Fields
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status", native_enum=False),
        nullable=False,
        default=TaskStatus.TODO,
    )

    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="task_priority", native_enum=False),
        nullable=False,
        default=TaskPriority.MEDIUM,
    )

    # Foreign Keys
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Optional Date Field
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks",
        foreign_keys=[project_id],
    )

    assignee: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id],
    )

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys=[creator_id],
    )

    # Indexes
    __table_args__ = (
        # Single column indexes for common filters
        Index("ix_tasks_project_id", "project_id"),  # For filtering tasks by project
        Index("ix_tasks_assignee_id", "assignee_id"),  # For filtering tasks by assignee
        Index(
            "ix_tasks_creator_id", "creator_id"
        ),  # For permission checks and filtering by creator
        Index("ix_tasks_status", "status"),  # For filtering by status
        Index("ix_tasks_priority", "priority"),  # For filtering by priority
        Index("ix_tasks_due_date", "due_date"),  # For filtering/sorting by due date
        Index("ix_tasks_created_at", "created_at"),  # For sorting by creation date
        Index("ix_tasks_updated_at", "updated_at"),  # For sorting by last update
        # Composite indexes for common query patterns
        Index(
            "ix_tasks_project_id_status", "project_id", "status"
        ),  # Project tasks by status
        Index(
            "ix_tasks_project_id_assignee_id", "project_id", "assignee_id"
        ),  # Project tasks by assignee
        Index(
            "ix_tasks_assignee_id_status", "assignee_id", "status"
        ),  # User's assigned tasks by status
        Index(
            "ix_tasks_project_id_due_date", "project_id", "due_date"
        ),  # Project tasks sorted by due date
        Index(
            "ix_tasks_assignee_id_due_date", "assignee_id", "due_date"
        ),  # User's tasks sorted by due date
    )

    def __repr__(self) -> str:
        return (
            "<Task("
            f"id={self.id}, title={self.title}, status={self.status}, "
            f"project_id={self.project_id})>"
        )
