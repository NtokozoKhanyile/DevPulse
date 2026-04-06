import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CelebrationEntry(Base, TimestampMixin):
    """One entry per completed project. Powers the public Celebration Wall."""

    __tablename__ = "celebration_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one celebration entry per project — enforced at DB level
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,  # denormalised — avoids join on high-traffic public wall endpoint
    )
    featured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False  # admin can feature entries at the top of the wall
    )
    shoutout: Mapped[str | None] = mapped_column(
        String(300), nullable=True  # optional message from the developer on completion
    )

    # Relationships
    project = relationship(
        "Project",
        back_populates="celebration_entry",
    )
    owner = relationship(
        "User",
    )

    __table_args__ = (
        Index("idx_celebration_owner_id", "owner_id"),
        Index("idx_celebration_featured", "featured"),
        Index("idx_celebration_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<CelebrationEntry id={self.id} project_id={self.project_id} featured={self.featured}>"