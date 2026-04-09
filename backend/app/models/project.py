"""Project model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User


class Project(Base):
    """Project model representing a collection of tasks."""

    __tablename__ = "projects"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=None,  # Let application handle UUID generation
    )

    # Required Fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional Fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Foreign Keys
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_projects",
        foreign_keys=[owner_id],
    )

    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("ix_projects_owner_id", "owner_id"),  # For filtering projects by owner
        Index("ix_projects_created_at", "created_at"),  # For sorting by creation date
        Index(
            "ix_projects_owner_id_created_at", "owner_id", "created_at"
        ),  # Composite for owner's projects sorted by date
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
