import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CollabStatus(str, enum.Enum):
    """Valid status values for a collaboration request."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class CollaborationRequest(Base, TimestampMixin):
    """A request from a developer to collaborate on another developer's project."""

    __tablename__ = "collaboration_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    requester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)  # optional pitch from requester
    status: Mapped[CollabStatus] = mapped_column(
        SAEnum(CollabStatus, name="collab_status_enum"),
        nullable=False,
        default=CollabStatus.PENDING,
    )
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True  # set when owner accepts or declines
    )

    # Relationships
    project = relationship(
        "Project",
        back_populates="collaboration_requests",
    )
    requester = relationship(
        "User",
        foreign_keys=[requester_id],
        back_populates="collaboration_requests_sent",
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "requester_id",
            name="uq_collab_project_requester",  # one open request per user per project
        ),
        Index("idx_collab_project_id", "project_id"),
        Index("idx_collab_requester_id", "requester_id"),
        Index("idx_collab_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<CollaborationRequest id={self.id} status={self.status} requester_id={self.requester_id}>"