"""User model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task import Task


class User(Base):
    """User model representing application users."""

    __tablename__ = "users"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=None,  # Let application handle UUID generation
    )

    # Required Fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # Hashed password

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    owned_projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="owner",
        foreign_keys="Project.owner_id",
        cascade="all, delete-orphan",
    )

    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )

    created_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.creator_id",
    )

    # Indexes
    __table_args__ = (
        Index("ix_users_email", "email"),  # For login and uniqueness checks
        Index(
            "ix_users_created_at", "created_at"
        ),  # For sorting/filtering by registration date
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
