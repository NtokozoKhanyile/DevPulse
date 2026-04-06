import enum
import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class NotificationType(str, enum.Enum):
    """All notification events that can be delivered to a user's inbox."""

    NEW_COMMENT = "new_comment"           # someone commented on your project
    COLLAB_REQUEST = "collab_request"     # someone raised a hand on your project
    COLLAB_ACCEPTED = "collab_accepted"   # your collaboration request was accepted
    COLLAB_DECLINED = "collab_declined"   # your collaboration request was declined
    MILESTONE_POSTED = "milestone_posted" # a project you follow posted a milestone
    PROJECT_COMPLETED = "project_completed" # a project you follow is on the Celebration Wall


class Notification(Base, TimestampMixin):
    """An in-app notification delivered to a user's inbox."""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),  # nullable — system events have no actor
        nullable=True,
    )
    type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType, name="notification_type_enum"),
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False  # e.g. "project", "comment", "collab_request"
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False  # ID of the referenced entity
    )
    message: Mapped[str] = mapped_column(
        String(300), nullable=False  # human-readable notification text
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Relationships
    recipient = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="notifications",
    )
    actor = relationship(
        "User",
        foreign_keys=[actor_id],  # explicit — two FKs to users, SQLAlchemy needs guidance
    )

    __table_args__ = (
        Index("idx_notifications_recipient_id", "recipient_id"),
        Index("idx_notifications_is_read", "recipient_id", "is_read"),  # composite — unread count badge
        Index("idx_notifications_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Notification id={self.id} type={self.type} recipient_id={self.recipient_id}>"