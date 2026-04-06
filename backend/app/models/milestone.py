import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Milestone(Base):
    """A timestamped progress update posted by a project owner. Immutable once created."""

    __tablename__ = "milestones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)  # short headline
    body: Mapped[str | None] = mapped_column(Text, nullable=True)    # optional expanded description

    # Intentionally only created_at — milestones are immutable, no updated_at
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    project = relationship(
        "Project",
        back_populates="milestones",
    )

    __table_args__ = (
        Index("idx_milestones_project_id", "project_id"),
        Index("idx_milestones_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Milestone id={self.id} title={self.title!r}>"