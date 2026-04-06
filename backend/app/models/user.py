import uuid

from sqlalchemy import Boolean, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Represents a developer account on the DevPulse platform."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(255), nullable=True)  # must start with https://github.com/
    website_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # set True after email verification

    # Relationships
    projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    comments = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    collaboration_requests_sent = relationship(
        "CollaborationRequest",
        foreign_keys="CollaborationRequest.requester_id",
        back_populates="requester",
        cascade="all, delete-orphan",
    )
    notifications = relationship(
        "Notification",
        back_populates="recipient",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_users_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"