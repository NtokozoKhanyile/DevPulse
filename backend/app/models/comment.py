import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Comment(Base, TimestampMixin):
    """A comment on a project. Supports one level of nesting via parent_id."""

    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="SET NULL"),  # SET NULL preserves thread structure
        nullable=True,
    )
    body: Mapped[str] = mapped_column(String(2000), nullable=False)  # hard cap prevents abuse
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False  # soft delete — never hard delete comments
    )

    # Relationships
    project = relationship(
        "Project",
        back_populates="comments",
    )
    author = relationship(
        "User",
        back_populates="comments",
    )
    # Self-referential: parent comment
    parent = relationship(
        "Comment",
        back_populates="replies",
        remote_side="Comment.id",  # this side is the "one" in one-to-many
    )
    # Self-referential: child replies
    replies = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_comments_project_id", "project_id"),
        Index("idx_comments_author_id", "author_id"),
        Index("idx_comments_parent_id", "parent_id"),
    )

    def __repr__(self) -> str:
        return f"<Comment id={self.id} author_id={self.author_id} is_deleted={self.is_deleted}>"